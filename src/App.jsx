import React from "react";
import { Routes, Route, useLocation } from "react-router-dom";
import Home from "./pages/Home.jsx";
import Realtime from "./pages/Realtime.jsx";
import Header from "./components/Header.jsx";
import Dashboard from "./pages/Dashboard.jsx";
import Splash from "./components/Splash.jsx"; // استدعاء مكوّن Splash
import Members from "./pages/Members";


export default function App() {
  const { pathname } = useLocation();

  return (
    <Splash key={pathname}> {/* Splash يتفعل مع كل تنقل صفحة */}
      <div className="app">
        <Header />
        <main className="container">
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/realtime" element={<Realtime />} />
            <Route path="/dashboard" element={<Dashboard />} />
            <Route path="/members" element={<Members />} />
          </Routes>
        </main>
        <footer className="footer">
          <div className="sadu-strip" aria-hidden="true"></div>
          <p>© 2025 VisionGuard — جميع الحقوق محفوظة</p>
        </footer>
      </div>
    </Splash>
  );
}
