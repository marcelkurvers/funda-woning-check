
import React from 'react';

const Header: React.FC = () => {
  return (
    <header className="w-full border-b border-gray-200 dark:border-border-dark bg-white dark:bg-background-dark px-6 py-4 sticky top-0 z-50">
      <div className="max-w-7xl mx-auto flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="flex items-center justify-center text-primary">
            <span className="material-symbols-outlined text-3xl">analytics</span>
          </div>
          <h2 className="text-lg font-bold tracking-tight text-slate-900 dark:text-white">Funda.nl Huis Analyse</h2>
        </div>
        <button className="bg-slate-100 hover:bg-slate-200 dark:bg-surface-dark dark:hover:bg-border-dark text-slate-900 dark:text-white px-4 py-2 rounded-lg text-sm font-semibold transition-colors flex items-center gap-2">
          <span className="material-symbols-outlined text-[20px]">account_circle</span>
          <span>Log in</span>
        </button>
      </div>
    </header>
  );
};

export default Header;
