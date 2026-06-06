import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";

import { ExploreScreen } from "./components/ExploreScreen";
import { MenuScreen } from "./components/MenuScreen";
import { PlayScreen } from "./components/PlayScreen";

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<MenuScreen />} />
        <Route path="/play" element={<PlayScreen />} />
        <Route path="/explore" element={<ExploreScreen />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  );
}
