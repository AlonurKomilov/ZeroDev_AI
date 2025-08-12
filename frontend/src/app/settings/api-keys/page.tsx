"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";

// Define the type for an API key
type ApiKey = {
  id: string;
  service_name: string;
  display_key: string; // e.g., "sk-....1234"
  created_at: string;
};

// --- Mock API Functions ---
// In a real app, these would be in a dedicated API service file.

const fetchApiKeys = async (): Promise<ApiKey[]> => {
  console.log("Fetching API keys...");
  // const res = await fetch("/api/keys");
  // if (!res.ok) throw new Error("Failed to fetch keys");
  // return res.json();
  return Promise.resolve([
    { id: "1", service_name: "OpenAI", display_key: "sk-....-xxxx", created_at: new Date().toISOString() },
    { id: "2", service_name: "Anthropic", display_key: "sk-....-yyyy", created_at: new Date().toISOString() },
  ]);
};

const addApiKey = async ({ service, key }: { service: string; key: string }): Promise<ApiKey> => {
  console.log("Adding API key:", { service, key });
  // const res = await fetch("/api/keys", {
  //   method: "POST",
  //   headers: { "Content-Type": "application/json" },
  //   body: JSON.stringify({ service_name: service, api_key: key }),
  // });
  // if (!res.ok) throw new Error("Failed to add key");
  // return res.json();
  return Promise.resolve({
      id: Math.random().toString(),
      service_name: service,
      display_key: `new-....-${Math.random().toString(36).substring(8)}`,
      created_at: new Date().toISOString()
  });
};

const deleteApiKey = async (id: string): Promise<void> => {
  console.log("Deleting API key:", id);
  // const res = await fetch(`/api/keys/${id}`, { method: "DELETE" });
  // if (!res.ok) throw new Error("Failed to delete key");
};

// --- Component ---

export default function ApiKeysPage() {
  const queryClient = useQueryClient();
  const [newService, setNewService] = useState("");
  const [newKey, setNewKey] = useState("");

  const { data: keys, isLoading, isError } = useQuery<ApiKey[]>({
    queryKey: ["apiKeys"],
    queryFn: fetchApiKeys,
  });

  const addMutation = useMutation({
    mutationFn: addApiKey,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["apiKeys"] });
      setNewService("");
      setNewKey("");
    },
  });

  const deleteMutation = useMutation({
    mutationFn: deleteApiKey,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["apiKeys"] });
    },
  });

  const handleAddKey = (e: React.FormEvent) => {
    e.preventDefault();
    if (!newService || !newKey) {
      alert("Please provide both a service name and an API key.");
      return;
    }
    addMutation.mutate({ service: newService, key: newKey });
  };

  return (
    <div>
      <h2 className="text-2xl font-bold mb-4">Manage API Keys</h2>
      <p className="mb-6 text-gray-600 dark:text-gray-400">
        Securely add your own LLM API keys. We encrypt your keys at rest.
      </p>

      {/* Add New Key Form */}
      <form onSubmit={handleAddKey} className="mb-8 p-4 border rounded-lg dark:border-gray-700">
        <h3 className="font-semibold text-lg mb-2">Add New Key</h3>
        <div className="flex flex-col md:flex-row gap-4">
          <input
            type="text"
            value={newService}
            onChange={(e) => setNewService(e.target.value)}
            placeholder="Service Name (e.g., OpenAI)"
            className="flex-grow px-3 py-2 bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-md"
            required
          />
          <input
            type="password"
            value={newKey}
            onChange={(e) => setNewKey(e.target.value)}
            placeholder="API Key"
            className="flex-grow px-3 py-2 bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-md"
            required
          />
          <button type="submit" disabled={addMutation.isPending} className="bg-blue-500 text-white px-4 py-2 rounded-md hover:bg-blue-600 disabled:bg-gray-400">
            {addMutation.isPending ? "Adding..." : "Add Key"}
          </button>
        </div>
      </form>

      {/* List of Keys */}
      <div className="space-y-4">
        <h3 className="font-semibold text-lg">Your Keys</h3>
        {isLoading && <p>Loading keys...</p>}
        {isError && <p className="text-red-500">Failed to load keys.</p>}
        {keys?.map((key) => (
          <div key={key.id} className="flex justify-between items-center p-3 border rounded-md dark:border-gray-700">
            <div>
              <p className="font-semibold">{key.service_name}</p>
              <p className="text-sm text-gray-500 font-mono">{key.display_key}</p>
            </div>
            <button
              onClick={() => deleteMutation.mutate(key.id)}
              disabled={deleteMutation.isPending && deleteMutation.variables === key.id}
              className="bg-red-500 text-white px-3 py-1 rounded-md hover:bg-red-600 disabled:bg-gray-400 text-sm"
            >
              Delete
            </button>
          </div>
        ))}
         {keys && keys.length === 0 && <p className="text-gray-500">You haven&apos;t added any API keys yet.</p>}
      </div>
    </div>
  );
}
