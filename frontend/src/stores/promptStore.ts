import { create } from 'zustand';

interface PromptState {
  history: string[];
  currentModel: string;
  addPromptToHistory: (prompt: string) => void;
  setModel: (model: string) => void;
}

export const usePromptStore = create<PromptState>((set) => ({
  history: [],
  currentModel: 'GPT-4o Mini',
  addPromptToHistory: (prompt: string) =>
    set((state) => ({ history: [prompt, ...state.history] })),
  setModel: (model: string) => set({ currentModel: model }),
}));
