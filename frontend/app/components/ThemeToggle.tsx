'use client';

import { useTheme } from '../hooks/useTheme';
import { useEffect, useState } from 'react';

export default function ThemeToggle() {
  const [theme, setTheme] = useTheme();
  const [isMounted, setIsMounted] = useState(false);

  useEffect(() => {
    setIsMounted(true);
  }, []);

  if (!isMounted) return null;

  return (
    <button
      aria-label="Toggle Theme"
      className="fixed top-6 right-6 z-50 bg-white/80 dark:bg-gray-900/80 rounded-full shadow p-2 transition hover:scale-110"
      onClick={() => setTheme(theme === 'dark' ? 'light' : 'dark')}
    >
      {theme === 'dark' ? (
        <svg
          width={24}
          height={24}
          fill="none"
          stroke="currentColor"
          strokeWidth={2}
          className="text-yellow-400"
          viewBox="0 0 24 24"
        >
          <path d="M21 12.79A9 9 0 0111.21 3a7 7 0 108.58 9.79z" />
        </svg>
      ) : (
        <svg
          width={24}
          height={24}
          fill="none"
          stroke="currentColor"
          strokeWidth={2}
          className="text-yellow-500"
          viewBox="0 0 24 24"
        >
          <circle cx={12} cy={12} r={5} />
          <path d="M12 1v2m0 18v2m11-11h-2M3 12H1m16.95 7.07l-1.41-1.41M6.34 6.34L4.93 4.93m12.02 0l-1.41 1.41M6.34 17.66l-1.41 1.41" />
        </svg>
      )}
    </button>
  );
}
