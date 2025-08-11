'use client'

import { useState } from 'react'
import AuroraBackground from './components/AuroraBackground'
import FancyPromptInput from './components/FancyPromptInput'
import SuggestionList, { Suggestion } from './components/SuggestionList'
import { useToast } from './components/ToastContext'

export default function Dashboard() {
  const [prompt, setPrompt] = useState('')
  const [loading, setLoading] = useState(false)
  const [suggestions, setSuggestions] = useState<Suggestion[]>([])
  const [likedIdx, setLikedIdx] = useState<number | null>(null)
  const [dislikedIdx, setDislikedIdx] = useState<number | null>(null)
  const [loadingIdx, setLoadingIdx] = useState<number | null>(null)

  // Feedback modal (bonus: keyingi step uchun extensible)
  const [feedbackOpen, setFeedbackOpen] = useState(false)
  const [feedbackIdx, setFeedbackIdx] = useState<number | null>(null)
  const [feedbackScore, setFeedbackScore] = useState<number | null>(null)
  const [feedbackComment, setFeedbackComment] = useState('')

  const { showToast } = useToast()

  // Prompt yuborish
  const handlePromptSubmit = async () => {
    if (!prompt.trim()) return
    setLoading(true)
    setSuggestions([])
    setLikedIdx(null)
    setDislikedIdx(null)
    showToast('Thinking...', 'info')

    try {
      const res = await fetch('/suggest_prompt', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          prompt,
          role: 'guest',
          user_id: 'web-client'
        })
      })
      if (!res.ok) throw new Error(`Server error: ${res.status}`)
      const data = await res.json()
      setSuggestions(data.suggestions || [])
      showToast('AI suggestions received!', 'success')
    } catch (err: any) {
      showToast('Error fetching suggestions!', 'error')
    } finally {
      setLoading(false)
    }
  }

  // Like/Dislike harakati (modal ochish uchun)
  const handleLike = (idx: number) => {
    setLikedIdx(idx)
    setDislikedIdx(null)
    setFeedbackIdx(idx)
    setFeedbackScore(1)
    setFeedbackOpen(true)
  }

  const handleDislike = (idx: number) => {
    setDislikedIdx(idx)
    setLikedIdx(null)
    setFeedbackIdx(idx)
    setFeedbackScore(0)
    setFeedbackOpen(true)
  }

  // Feedback yuborish
  const handleFeedbackSubmit = async () => {
    if (feedbackIdx === null || feedbackScore === null) return
    setLoadingIdx(feedbackIdx)
    try {
      const res = await fetch('/feedback', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          prompt: suggestions[feedbackIdx]?.suggested_prompt,
          user_id: 'web-client',
          score: feedbackScore,
          comment: feedbackComment
        })
      })
      if (!res.ok) throw new Error('Feedback failed')
      showToast('Thank you for your feedback!', 'success')
      setTimeout(() => {
        setFeedbackOpen(false)
        setFeedbackComment('')
        setLoadingIdx(null)
      }, 1000)
    } catch {
      showToast('Error submitting feedback!', 'error')
      setLoadingIdx(null)
    }
  }

  return (
    <>
      <AuroraBackground />
      <main className="relative z-10 p-6 space-y-6 max-w-3xl mx-auto">
        <h1 className="text-2xl font-bold text-white dark:text-blue-200 drop-shadow-md">
          🧠 ZeroDev Prompt Tester
        </h1>

        {/* Modular, animated prompt input */}
        <FancyPromptInput
          value={prompt}
          onChange={setPrompt}
          onSubmit={handlePromptSubmit}
          loading={loading}
          placeholder="Describe your idea, question, or code problem..."
        />

        {/* AI Suggestions — modular card list */}
        <SuggestionList
          suggestions={suggestions}
          onLike={handleLike}
          onDislike={handleDislike}
          likedIdx={likedIdx}
          dislikedIdx={dislikedIdx}
          loadingIdx={loadingIdx}
        />

        {/* Feedback modal */}
        {feedbackOpen && feedbackIdx !== null && (
          <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
            <div className="bg-white dark:bg-gray-900 rounded-xl p-6 w-full max-w-md space-y-4 shadow-lg dark:shadow-blue-900">
              <h3 className="text-lg font-semibold dark:text-blue-100">
                {feedbackScore === 1 ? '👍 You liked this suggestion' : '👎 You disliked this suggestion'}
              </h3>
              <textarea
                rows={3}
                className="w-full border rounded p-2 text-sm bg-white/80 dark:bg-gray-800/80 dark:text-blue-100"
                placeholder="Add a comment (optional)..."
                value={feedbackComment}
                onChange={(e) => setFeedbackComment(e.target.value)}
              />
              <div className="flex justify-between items-center pt-2">
                <button
                  className="text-gray-500 dark:text-gray-300 text-sm"
                  onClick={() => {
                    setFeedbackOpen(false)
                    setFeedbackComment('')
                  }}
                >
                  Cancel
                </button>
                <button
                  className="bg-blue-600 text-white px-4 py-1 rounded hover:bg-blue-700 dark:bg-blue-800 dark:hover:bg-blue-900 text-sm"
                  onClick={handleFeedbackSubmit}
                  disabled={loadingIdx === feedbackIdx}
                >
                  {loadingIdx === feedbackIdx ? 'Sending...' : 'Submit Feedback'}
                </button>
              </div>
            </div>
          </div>
        )}
      </main>
    </>
  )
}
