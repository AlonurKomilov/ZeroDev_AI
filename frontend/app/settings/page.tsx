'use client';

import SettingsPanel from '../components/SettingsPanel';
import ThemeToggle from '../components/ThemeToggle';

export default function SettingsPage() {
  return (
    <section className="max-w-2xl mx-auto flex flex-col gap-8 mt-8">
      <h1 className="text-3xl font-bold text-white mb-2">Settings</h1>
      <p className="text-zinc-400 mb-4">
        Personalize your ZeroDev AI experience, manage your API key, and select your default model.
      </p>
      <div className="rounded-2xl bg-zinc-900/70 p-6 shadow-lg border border-zinc-800">
        <SettingsPanel />
      </div>
      <div className="flex justify-end">
        <ThemeToggle />
      </div>
    </section>
  );
}
