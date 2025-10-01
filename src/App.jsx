import React from 'react'
import { Routes, Route, Link, useLocation } from 'react-router-dom'
import Home from './pages/Home.jsx'
import Realtime from './pages/Realtime.jsx'
import Header from './components/Header.jsx'

export default function App() {
  const { pathname } = useLocation();
  return (
    <div className="app">
      <Header />
      <main className="container">
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/realtime" element={<Realtime />} />
        </Routes>
      </main>
      <footer className="footer">
        <div className="sadu-strip" aria-hidden="true"></div>
        <p>© 2025 VisionGuard — جميع الحقوق محفوظة</p>
      </footer>
    </div>
  )
}
