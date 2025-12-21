
import React from 'react';

const Footer: React.FC = () => {
  return (
    <footer className="w-full border-t border-gray-200 dark:border-border-dark bg-white dark:bg-background-dark py-8 px-4 mt-auto">
      <div className="max-w-7xl mx-auto flex flex-col md:flex-row justify-between items-center gap-4 text-sm text-slate-500 dark:text-slate-400">
        <p>© {new Date().getFullYear()} Funda.nl Huis Analyse. Not affiliated with Funda Real Estate B.V.</p>
        <div className="flex gap-6">
          <a className="hover:text-primary transition-colors cursor-pointer">Privacy</a>
          <a className="hover:text-primary transition-colors cursor-pointer">Terms</a>
          <a className="hover:text-primary transition-colors cursor-pointer">Contact</a>
        </div>
      </div>
    </footer>
  );
};

export default Footer;
