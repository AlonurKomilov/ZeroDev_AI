'use client';

import DeployStatusCard from '../components/DeployStatusCard';

export default function DeployPage() {
  return (
    <section className="max-w-2xl mx-auto flex flex-col gap-8 mt-8">
      <h1 className="text-3xl font-bold text-white mb-2">Deploy & Status</h1>
      <p className="text-zinc-400 mb-4">
        Deploy your latest changes, monitor status, and review real-time logs from a single, unified dashboard.
      </p>
      <div className="rounded-2xl bg-zinc-900/70 p-6 shadow-lg border border-zinc-800">
        <DeployStatusCard />
      </div>
    </section>
  );
}
