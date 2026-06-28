import React from 'react';
import Sidebar from './Sidebar';

export default function Layout({ children, activePage, setActivePage }) {
  return (
    <div className="flex min-h-screen bg-[#0f172a] text-slate-100 font-sans">
      {/* Sidebar Navigation */}
      <Sidebar activePage={activePage} setActivePage={setActivePage} />

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col min-w-0">
        {/* Top Header */}
        <header className="h-16 flex items-center justify-between px-8 border-b border-slate-800 bg-[#1e293b]/50 backdrop-blur-md sticky top-0 z-40">
          <div className="flex items-center space-x-3">
            <span className="text-xl font-bold font-sans tracking-wide text-gradient">
              AI Risk & Collections Platform
            </span>
          </div>
          <div className="flex items-center space-x-4">
            <div className="text-xs text-slate-400 bg-slate-800 px-3 py-1.5 rounded-full border border-slate-700">
              Environment: <span className="text-emerald-400 font-semibold">Sandbox</span>
            </div>
            <div className="w-8 h-8 rounded-full bg-gradient-to-tr from-indigo-500 to-violet-500 flex items-center justify-center font-bold text-sm text-white">
              JD
            </div>
          </div>
        </header>

        {/* Dynamic Page Wrapper */}
        <main className="flex-1 p-8 overflow-y-auto max-w-7xl w-full mx-auto animate-slide-up">
          {children}
        </main>
      </div>
    </div>
  );
}
