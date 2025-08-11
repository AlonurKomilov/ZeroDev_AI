"use client";

import { useState } from "react";

export default function SettingsPanel() {
  const [apiKey, setApiKey] = useState("");
  const [defaultModel, setDefaultModel] = useState("gpt-4o");

  return (
    <form className="space-y-6">
      <div>
        <label className="block text-zinc-400 mb-2 text-sm">API Key</label>
        <input
          className="w-full rounded bg-zinc-800 text-white p-2 border border-zinc-700 focus:ring-2 focus:ring-emerald-400"
          value={apiKey}
          onChange={e => setApiKey(e.target.value)}
          placeholder="Enter your API key"
        />
      </div>
      <div>
        <label className="block text-zinc-400 mb-2 text-sm">Default Model</label>
        <select
          className="w-full rounded bg-zinc-800 text-white p-2 border border-zinc-700"
          value={defaultModel}
          onChange={e => setDefaultModel(e.target.value)}
        >
          <option value="gpt-4o">GPT-4o</option>
          <option value="claude-3">Claude 3</option>
          <option value="mistral">Mistral</option>
        </select>
      </div>
      <button
        type="button"
        className="bg-emerald-500 px-4 py-2 rounded text-white hover:bg-emerald-600 transition"
        onClick={() => alert("Settings saved! (demo)")}
      >
        Save Settings
      </button>
    </form>
  );
}
