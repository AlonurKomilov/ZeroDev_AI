'use client';

import FancyPromptInput from '../components/FancyPromptInput';
import SuggestionList from '../components/SuggestionList';
import FeedbackModal from '../components/FeedbackModal';

export default function PromptPage() {
  return (
    <section className="max-w-3xl mx-auto flex flex-col gap-8 mt-8">
      <h1 className="text-3xl font-bold text-white mb-2">Prompt Tester</h1>
      <p className="text-zinc-400 mb-4">
        Enter your prompt and let ZeroDev AI generate instant, high-quality responses. Experiment, ideate, and launch — all in one place!
      </p>
      <div className="rounded-2xl bg-zinc-900/70 p-6 shadow-lg border border-zinc-800">
        <FancyPromptInput />
      </div>
      <div className="mt-4">
        <SuggestionList />
      </div>
      <div className="flex justify-end">
        <FeedbackModal />
      </div>
    </section>
  );
}
