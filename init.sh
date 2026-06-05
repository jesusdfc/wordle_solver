#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_URL="http://127.0.0.1:9000"
FRONTEND_URL="http://127.0.0.1:5173"
FRONTEND_PORT=5173

kill_port() {
  local port="$1"
  local pid pids

  if [[ "${OSTYPE:-}" == msys* || "${OSTYPE:-}" == cygwin* ]]; then
    pids=$(netstat -ano 2>/dev/null | grep ":${port} " | grep LISTENING | awk '{print $NF}' | sort -u || true)
    for pid in $pids; do
      if [[ -n "$pid" && "$pid" != "0" ]]; then
        taskkill //PID "$pid" //F >/dev/null 2>&1 || true
      fi
    done
  elif command -v lsof >/dev/null 2>&1; then
    pids=$(lsof -ti:"${port}" 2>/dev/null || true)
    if [[ -n "$pids" ]]; then
      kill $pids 2>/dev/null || true
    fi
  elif command -v fuser >/dev/null 2>&1; then
    fuser -k "${port}/tcp" >/dev/null 2>&1 || true
  fi
}

cleanup() {
  local pid
  for pid in "${BACKEND_PID:-}" "${FRONTEND_PID:-}"; do
    if [[ -n "$pid" ]] && kill -0 "$pid" 2>/dev/null; then
      kill "$pid" 2>/dev/null || true
    fi
  done
  wait 2>/dev/null || true
}
trap cleanup EXIT INT TERM

open_browser() {
  local url="$1"
  if [[ "${OSTYPE:-}" == msys* || "${OSTYPE:-}" == cygwin* ]]; then
    cmd.exe /c start "" "$url" >/dev/null 2>&1
  elif command -v xdg-open >/dev/null 2>&1; then
    xdg-open "$url" >/dev/null 2>&1
  elif [[ "${OSTYPE:-}" == darwin* ]]; then
    open "$url"
  else
    echo "Open $url in your browser"
  fi
}

wait_for_url() {
  local url="$1"
  local attempt=0
  while (( attempt < 60 )); do
    if curl -sf -o /dev/null "$url" 2>/dev/null; then
      return 0
    fi
    sleep 0.5
    ((attempt += 1))
  done
  echo "Timed out waiting for $url" >&2
  return 1
}

network_label() {
  local ip="$1"
  local adapter="$2"
  local lower
  lower=$(printf '%s' "$adapter" | tr '[:upper:]' '[:lower:]')

  if [[ "$lower" == *tailscale* ]]; then
    printf '%s' "Tailscale VPN"
    return
  fi
  if [[ "$lower" == *wsl* || "$lower" == *hyper-v* || "$lower" == *vethernet* ]]; then
    printf '%s' "WSL / Hyper-V virtual switch"
    return
  fi
  if [[ "$lower" == *docker* ]]; then
    printf '%s' "Docker virtual network"
    return
  fi
  if [[ "$lower" == *"wi-fi"* || "$lower" == *wifi* || "$lower" == *wlan* ]]; then
    printf '%s' "Wi-Fi — share on same router"
    return
  fi
  if [[ "$lower" == *ethernet* && "$lower" != *vethernet* ]]; then
    printf '%s' "Wired Ethernet LAN"
    return
  fi

  if [[ "$ip" =~ ^100\.(6[4-9]|[7-9][0-9]|1[0-1][0-9]|12[0-7])\. ]]; then
    printf '%s' "Tailscale / CGNAT VPN"
  elif [[ "$ip" =~ ^192\.168\. ]]; then
    printf '%s' "Home Wi-Fi / LAN — share on same router"
  elif [[ "$ip" =~ ^172\.(1[6-9]|2[0-9]|3[0-1])\. ]]; then
    printf '%s' "WSL / Docker / virtual network"
  elif [[ "$ip" =~ ^10\. ]]; then
    printf '%s' "VPN or private virtual network"
  else
    printf '%s' "Network interface"
  fi
}

print_network_urls() {
  local port="$1"
  local found=0

  echo "  Local:    http://127.0.0.1:${port}/  (this machine only)"

  if [[ "${OSTYPE:-}" == msys* || "${OSTYPE:-}" == cygwin* ]]; then
    local adapter="" line ip label
    while IFS= read -r line; do
      line="${line//$'\r'/}"
      if [[ "$line" =~ adapter[[:space:]]+(.+):$ || "$line" =~ Adapter[[:space:]]+(.+):$ ]]; then
        adapter="${BASH_REMATCH[1]}"
      elif [[ "$line" =~ IPv4[^:]*:[[:space:]]*(.+)$ ]]; then
        ip="${BASH_REMATCH[1]// /}"
        if [[ -n "$ip" && "$ip" != "127.0.0.1" ]]; then
          label="$(network_label "$ip" "$adapter")"
          printf "  Network:  http://%s:%s/  (%s)\n" "$ip" "$port" "$label"
          found=1
        fi
      fi
    done < <(ipconfig 2>/dev/null || true)
  elif command -v ip >/dev/null 2>&1; then
    local iface ip label
    while read -r _ iface _ ip_cidr; do
      ip="${ip_cidr%%/*}"
      [[ -z "$ip" || "$ip" == "127.0.0.1" ]] && continue
      label="$(network_label "$ip" "$iface")"
      printf "  Network:  http://%s:%s/  (%s)\n" "$ip" "$port" "$label"
      found=1
    done < <(ip -4 -o addr show scope global 2>/dev/null || true)
  elif command -v ifconfig >/dev/null 2>&1; then
    local iface ip label
    while read -r iface ip; do
      [[ -z "$ip" || "$ip" == "127.0.0.1" ]] && continue
      label="$(network_label "$ip" "$iface")"
      printf "  Network:  http://%s:%s/  (%s)\n" "$ip" "$port" "$label"
      found=1
    done < <(ifconfig 2>/dev/null | awk '/^[^ \t]/ {iface=$1} /inet / {print iface, $2}' | sed 's/addr://' || true)
  fi

  if (( found == 0 )); then
    echo "  Network:  (no addresses found — check ipconfig / ip addr)"
  fi
}

echo "Freeing port ${FRONTEND_PORT}..."
kill_port "$FRONTEND_PORT"

echo "Installing backend dependencies..."
(cd "$ROOT/backend" && uv sync --quiet)

echo "Installing frontend dependencies..."
(cd "$ROOT/frontend" && npm install --silent)

echo "Starting backend on $BACKEND_URL ..."
(cd "$ROOT/backend" && uv run python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 9000) &
BACKEND_PID=$!

echo "Starting frontend (LAN enabled) on port ${FRONTEND_PORT} ..."
(cd "$ROOT/frontend" && npm run dev) &
FRONTEND_PID=$!

echo "Waiting for frontend..."
wait_for_url "$FRONTEND_URL"

echo ""
print_network_urls "$FRONTEND_PORT"
echo ""
echo "  Tip: share the Wi-Fi / 192.168.x.x address with devices on the same router."
echo ""

echo "Opening browser..."
open_browser "$FRONTEND_URL"

echo "Press Ctrl+C to stop both servers."
wait "$BACKEND_PID" "$FRONTEND_PID"
