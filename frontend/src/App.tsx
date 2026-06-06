import { useState } from "react";

import type { AppMode } from "./types";
import { ExploreScreen } from "./components/ExploreScreen";
import { MenuScreen } from "./components/MenuScreen";
import { PlayScreen } from "./components/PlayScreen";

export default function App() {
  const [mode, setMode] = useState<AppMode>("menu");

  if (mode === "play") {
    return <PlayScreen onBack={() => setMode("menu")} />;
  }

  if (mode === "explore") {
    return <ExploreScreen onBack={() => setMode("menu")} />;
  }

  return (
    <MenuScreen onPlay={() => setMode("play")} onExplore={() => setMode("explore")} />
  );
}
