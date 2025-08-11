'use client'

import SuggestionCard from './SuggestionCard'

export interface Suggestion {
  suggested_prompt: string
  confidence: number
  explanation: string
}

interface SuggestionListProps {
  suggestions: Suggestion[]
  onLike?: (idx: number) => void
  onDislike?: (idx: number) => void
  likedIdx?: number | null
  dislikedIdx?: number | null
  loadingIdx?: number | null
}

export default function SuggestionList({
  suggestions,
  onLike,
  onDislike,
  likedIdx,
  dislikedIdx,
  loadingIdx
}: SuggestionListProps) {
  if (!suggestions || suggestions.length === 0) return null

  return (
    <div className="space-y-4 mt-6">
      <h2 className="text-lg font-semibold text-white dark:text-blue-200 drop-shadow mb-1">💡 Suggestions:</h2>
      {suggestions.map((sug, i) => (
        <SuggestionCard
          key={i}
          prompt={sug.suggested_prompt}
          explanation={sug.explanation}
          confidence={sug.confidence}
          onLike={onLike ? () => onLike(i) : undefined}
          onDislike={onDislike ? () => onDislike(i) : undefined}
          liked={likedIdx === i}
          disliked={dislikedIdx === i}
          loading={loadingIdx === i}
        />
      ))}
    </div>
  )
}
