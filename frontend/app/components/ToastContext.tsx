'use client'

import { createContext, useCallback, useContext, useState, ReactNode } from 'react'

export interface Toast {
  id: number
  message: string
  type?: 'success' | 'error' | 'info'
}

interface ToastContextProps {
  showToast: (msg: string, type?: Toast['type']) => void
}

const ToastContext = createContext<ToastContextProps | undefined>(undefined)

export function useToast() {
  const ctx = useContext(ToastContext)
  if (!ctx) throw new Error('useToast must be used within a ToastProvider')
  return ctx
}

let toastCounter = 0

export function ToastProvider({ children }: { children: ReactNode }) {
  const [toasts, setToasts] = useState<Toast[]>([])

  const showToast = useCallback((message: string, type?: Toast['type']) => {
    const id = ++toastCounter
    setToasts((toasts) => [...toasts, { id, message, type }])
    setTimeout(() => {
      setToasts((toasts) => toasts.filter((t) => t.id !== id))
    }, 3000) // auto-dismiss after 3s
  }, [])

  return (
    <ToastContext.Provider value={{ showToast }}>
      {children}
      <div className="fixed bottom-6 right-6 space-y-2 z-[100]">
        {toasts.map((toast) => (
          <div
            key={toast.id}
            className={`px-4 py-2 rounded shadow-lg text-white
              ${toast.type === 'success' ? 'bg-green-600/90' : ''}
              ${toast.type === 'error' ? 'bg-red-600/90' : ''}
              ${toast.type === 'info' || !toast.type ? 'bg-blue-700/90' : ''}
              animate-fade-in`}
            style={{ minWidth: 180 }}
          >
            {toast.message}
          </div>
        ))}
      </div>
      <style jsx global>{`
        @keyframes fade-in {
          from { opacity: 0; transform: translateY(10px);}
          to { opacity: 1; transform: translateY(0);}
        }
        .animate-fade-in {
          animation: fade-in 0.5s cubic-bezier(0.4,0,0.2,1);
        }
      `}</style>
    </ToastContext.Provider>
  )
}
