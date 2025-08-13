"use client";

import React, { createContext, useContext, useState, ReactNode } from 'react';

type ToastMessage = {
  id: number;
  message: string;
  type: 'success' | 'error' | 'info';
};

type ToastContextType = {
  addToast: (message: string, type: 'success' | 'error' | 'info') => void;
};

const ToastContext = createContext<ToastContextType | undefined>(undefined);

export const useToast = () => {
  const context = useContext(ToastContext);
  if (!context) {
    throw new Error('useToast must be used within a ToastProvider');
  }
  return context;
};

export const ToastProvider = ({ children }: { children: ReactNode }) => {
  const [toasts, setToasts] = useState<ToastMessage[]>([]);

  const addToast = (message: string, type: 'success' | 'error' | 'info' = 'info') => {
    const id = Date.now();
    setToasts((prevToasts) => [...prevToasts, { id, message, type }]);
    setTimeout(() => {
      removeToast(id);
    }, 5000);
  };

  const removeToast = (id: number) => {
    setToasts((prevToasts) => prevToasts.filter((toast) => toast.id !== id));
  };

  return (
    <ToastContext.Provider value={{ addToast }}>
      {children}
      <div className="fixed bottom-5 right-5 z-50">
        {toasts.map((toast) => (
          <div key={toast.id} className={`p-4 rounded-md shadow-lg mb-2 text-white ${toast.type === 'error' ? 'bg-red-500' : 'bg-blue-500'}`}>
            {toast.message}
            <button onClick={() => removeToast(toast.id)} className="ml-4 font-bold">X</button>
          </div>
        ))}
      </div>
    </ToastContext.Provider>
  );
};
