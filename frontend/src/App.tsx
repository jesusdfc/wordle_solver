import { useState } from "react";

import type { AppMode } from "./types";
import { BenchmarkScreen } from "./components/BenchmarkScreen";
import { MenuScreen } from "./components/MenuScreen";
import { PlayScreen } from "./components/PlayScreen";

export default function App() {
  const [mode, setMode] = useState<AppMode>("menu");

  if (mode === "play") {
    return <PlayScreen onBack={() => setMode("menu")} />;
  }

  if (mode === "benchmark") {
    return <BenchmarkScreen onBack={() => setMode("menu")} />;
  }

  return (
    <MenuScreen onPlay={() => setMode("play")} onBenchmark={() => setMode("benchmark")} />
  );
}
