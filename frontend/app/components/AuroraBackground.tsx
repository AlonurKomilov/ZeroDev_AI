'use client'

import { useEffect } from 'react'

export default function AuroraBackground() {
  useEffect(() => {
    const style = document.createElement('style')
    style.innerHTML = `
      @keyframes aurora {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
      }
    `
    document.head.appendChild(style)
    return () => {
      document.head.removeChild(style)
    }
  }, [])

  return (
    <div
      className="fixed inset-0 -z-10 opacity-30 blur-sm"
      style={{
        background: 'linear-gradient(135deg, #0f172a, #1e3a8a, #0f172a)',
        backgroundSize: '400% 400%',
        animation: 'aurora 20s ease-in-out infinite',
      }}
    />
  )
}
