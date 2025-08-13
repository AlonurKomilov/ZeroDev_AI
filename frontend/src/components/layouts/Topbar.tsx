import React from 'react';
import { ThemeToggle } from '../ui/ThemeToggle';

const Topbar = () => {
  return (
    <header className="h-16 bg-card text-card-foreground p-4 border-b flex items-center justify-between">
      <h1 className="text-xl font-bold">Topbar</h1>
      <ThemeToggle />
    </header>
  );
};

export default Topbar;
