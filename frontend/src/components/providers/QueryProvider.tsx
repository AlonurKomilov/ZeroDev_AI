"use client";

import { QueryClient, QueryClientProvider, useQueryClient } from "@tanstack/react-query";
import { useEffect, useState } from "react";
import { useToast } from "@/contexts/ToastContext";

const GlobalErrorHandler = () => {
  const queryClient = useQueryClient();
  const { addToast } = useToast();

  useEffect(() => {
    queryClient.setDefaultOptions({
      queries: {
        onError: (error: any) => {
          addToast(error.message || "An unexpected error occurred", "error");
        },
      },
      mutations: {
        onError: (error: any) => {
          addToast(error.message || "An unexpected error occurred", "error");
        },
      },
    });
  }, [queryClient, addToast]);

  return null;
};

export default function QueryProvider({
  children,
}: {
  children: React.ReactNode;
}) {
  const [queryClient] = useState(() => new QueryClient());

  return (
    <QueryClientProvider client={queryClient}>
      <GlobalErrorHandler />
      {children}
    </QueryClientProvider>
  );
}
