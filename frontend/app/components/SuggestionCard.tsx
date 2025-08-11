'use client'

import { ReactNode } from 'react'

interface SuggestionCardProps {
  children?: ReactNode
  prompt: string
  explanation: string
  confidence: number
  onLike?: () => void
  onDislike?: () => void
  liked?: boolean
  disliked?: boolean
  loading?: boolean
}

export default function SuggestionCard({
  prompt,
  explanation,
  confidence,
  onLike,
  onDislike,
  liked,
  disliked,
  loading,
  children
}: SuggestionCardProps) {
  return (
    <div
      className={`
        group border border-blue-200 dark:border-blue-900/40
        rounded-2xl p-5 mb-2
        bg-white/90 dark:bg-gray-800/80
        shadow-xl dark:shadow-blue-950/30
        backdrop-blur transition
        hover:scale-[1.015] hover:shadow-2xl
        relative
        ${loading ? "opacity-60 pointer-events-none" : ""}
      `}
    >
      <div className="flex items-center gap-2 mb-2">
        <span className="text-blue-600 dark:text-blue-300 text-lg font-medium">👉</span>
        <span className="font-semibold dark:text-blue-100 text-gray-900">{prompt}</span>
      </div>
      <p className="text-sm text-gray-500 dark:text-gray-400 mb-2">{explanation}</p>
      <div className="flex items-center justify-between pt-1">
        <span className="text-xs text-gray-400 dark:text-gray-500">
          Confidence: {Math.round(confidence * 100)}%
        </span>
        <div className="flex gap-1">
          <button
            className={`
              px-2 py-1 rounded-full
              transition
              ${liked ? "bg-green-500/30 text-green-600 dark:text-green-400" : "hover:bg-green-500/10"}
            `}
            aria-label="Like suggestion"
            onClick={onLike}
          >👍</button>
          <button
            className={`
              px-2 py-1 rounded-full
              transition
              ${disliked ? "bg-red-500/30 text-red-600 dark:text-red-400" : "hover:bg-red-500/10"}
            `}
            aria-label="Dislike suggestion"
            onClick={onDislike}
          >👎</button>
        </div>
      </div>
      {children}
    </div>
  )
}
