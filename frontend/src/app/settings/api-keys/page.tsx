"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import { authService } from "@/lib/auth";

// Define the type for an API key
type ApiKey = {
  id: string;
  service_name: string;
  display_key: string; // e.g., "sk-....1234"
  created_at: string;
};

// --- Real API Functions ---
const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000';

const fetchApiKeys = async (): Promise<string[]> => {
  const token = authService.getToken();
  if (!token) throw new Error("Not authenticated");
  
  const res = await fetch(`${API_BASE_URL}/api/keys`, {
    headers: { 
      "Authorization": `Bearer ${token}`,
      "Content-Type": "application/json"
    }
  });
  
  if (!res.ok) {
    if (res.status === 401) {
      authService.logout();
      window.location.href = '/login';
    }
    throw new Error("Failed to fetch API keys");
  }
  
  return res.json();
};

const addApiKey = async ({ service, key }: { service: string; key: string }): Promise<{message: string}> => {
  const token = authService.getToken();
  if (!token) throw new Error("Not authenticated");
  
  const res = await fetch(`${API_BASE_URL}/api/keys`, {
    method: "POST",
    headers: { 
      "Content-Type": "application/json",
      "Authorization": `Bearer ${token}`
    },
    body: JSON.stringify({ service_name: service, api_key: key }),
  });
  
  if (!res.ok) {
    if (res.status === 401) {
      authService.logout();
      window.location.href = '/login';
    }
    throw new Error("Failed to add API key");
  }
  
  return res.json();
};

const deleteApiKey = async (serviceName: string): Promise<void> => {
  const token = authService.getToken();
  if (!token) throw new Error("Not authenticated");
  
  const res = await fetch(`${API_BASE_URL}/api/keys/${serviceName}`, { 
    method: "DELETE",
    headers: { 
      "Authorization": `Bearer ${token}`,
      "Content-Type": "application/json"
    }
  });
  
  if (!res.ok) {
    if (res.status === 401) {
      authService.logout();
      window.location.href = '/login';
    }
    throw new Error("Failed to delete API key");
  }
};

// --- Component ---

export default function ApiKeysPage() {
  const queryClient = useQueryClient();
  const [newService, setNewService] = useState("");
  const [newKey, setNewKey] = useState("");

  const { data: serviceNames, isLoading, isError, error } = useQuery<string[]>({
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
    onError: (error) => {
      alert(`Failed to add API key: ${error.message}`);
    }
  });

  const deleteMutation = useMutation({
    mutationFn: deleteApiKey,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["apiKeys"] });
    },
    onError: (error) => {
      alert(`Failed to delete API key: ${error.message}`);
    }
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
        {isError && <p className="text-red-500">Failed to load keys: {error?.message}</p>}
        {serviceNames && serviceNames.length > 0 ? (
          serviceNames.map((serviceName) => (
            <div key={serviceName} className="flex justify-between items-center p-3 border rounded-md dark:border-gray-700">
              <div>
                <p className="font-semibold">{serviceName}</p>
                <p className="text-sm text-gray-500 font-mono">sk-****-{serviceName.toLowerCase()}</p>
              </div>
              <button
                onClick={() => deleteMutation.mutate(serviceName)}
                disabled={deleteMutation.isPending && deleteMutation.variables === serviceName}
                className="bg-red-500 text-white px-3 py-1 rounded-md hover:bg-red-600 disabled:bg-gray-400 text-sm"
              >
                {deleteMutation.isPending && deleteMutation.variables === serviceName ? "Deleting..." : "Delete"}
              </button>
            </div>
          ))
        ) : (
          serviceNames && <p className="text-gray-500">You haven&apos;t added any API keys yet.</p>
        )}
      </div>
    </div>
  );
}
