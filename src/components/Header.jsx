import React from 'react'
import { Link, NavLink } from 'react-router-dom'

export default function Header(){
  return (
    <header className="header">
      <div className="brand">
        <img src="/assets/icon1.png" alt="" className="brand-icon" />
        <span className="divider">|</span>
        <span className="brand-sub">كشف مخالفات المحتوى</span>
      </div>
      <nav className="nav">
        <NavLink to="/" className={({isActive}) => isActive ? 'active' : ''}>الرئيسية</NavLink>
        <NavLink to="/realtime" className={({isActive}) => isActive ? 'active' : ''}>الكشف اللحظي</NavLink>
      </nav>
    </header>
  )
}
