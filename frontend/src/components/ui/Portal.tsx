"use client";

import { useState, useEffect } from 'react';
import { createPortal } from 'react-dom';

const Portal: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
    return () => setMounted(false);
  }, []);

  if (!mounted) {
    return null;
  }

  const el = document.getElementById('modal-root');
  return el ? createPortal(children, el) : null;
};

export default Portal;
