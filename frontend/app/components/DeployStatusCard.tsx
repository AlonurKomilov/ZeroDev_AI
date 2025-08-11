"use client";

export default function DeployStatusCard() {
  return (
    <div className="bg-zinc-900 rounded-xl p-6 shadow border border-zinc-800 flex flex-col gap-2">
      <h3 className="text-white font-semibold text-lg mb-2">Deployment Status</h3>
      <div className="text-zinc-300">Everything up-to-date! 🚀</div>
      <div className="text-xs text-zinc-400 mt-2">
        (Replace this with real deployment status, logs, or progress bars)
      </div>
    </div>
  );
}
