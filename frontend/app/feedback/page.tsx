'use client';

import AdminFeedbackTable from '../components/AdminFeedbackTable';
import FeedbackModal from '../components/FeedbackModal';

export default function FeedbackPage() {
  return (
    <section className="max-w-4xl mx-auto flex flex-col gap-8 mt-8">
      <h1 className="text-3xl font-bold text-white mb-2">Feedback & Ratings</h1>
      <p className="text-zinc-400 mb-4">
        Analyze feedback, success rates, and user sentiment. Improve your AI workflow by learning from real users!
      </p>
      <div className="rounded-2xl bg-zinc-900/70 p-6 shadow-lg border border-zinc-800">
        <AdminFeedbackTable />
      </div>
      <div className="flex justify-end">
        <FeedbackModal />
      </div>
    </section>
  );
}
