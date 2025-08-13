'use client';

import React, { useCallback, useState } from 'react';
import ReactFlow, {
  Controls,
  Background,
  applyNodeChanges,
  applyEdgeChanges,
  Node,
  Edge,
  OnNodesChange,
  OnEdgesChange,
  NodeChange,
  EdgeChange,
} from 'reactflow';
import 'reactflow/dist/style.css';
import { motion } from 'framer-motion';

import SuggestionNode from './SuggestionNode';
import SmartPromptInput from '../ui/SmartPromptInput';
import PromptHistory from './PromptHistory';
import { usePromptStore } from '@/stores/promptStore';
import PromptAssistant from './PromptAssistant';
import ModelSwitcher from '../ui/ModelSwitcher';

const nodeTypes = {
  suggestion: SuggestionNode,
};

const initialNodes: Node[] = [
  {
    id: '1',
    position: { x: 250, y: 50 },
    data: { label: 'User Authentication (OAuth)' },
    type: 'input',
    className: 'bg-card border-primary',
  },
  {
    id: '2',
    position: { x: 250, y: 200 },
    data: { label: 'PostgreSQL Database' },
    className: 'bg-card border-primary',
  },
  {
    id: '3',
    position: { x: 500, y: 125 },
    data: { label: 'REST API for Web App' },
    className: 'bg-card border-primary',
  },
  {
    id: 's1',
    position: { x: 50, y: 125 },
    data: { label: 'Add Admin Dashboard?' },
    type: 'suggestion',
  },
  {
    id: 's2',
    position: { x: 250, y: 350 },
    data: { label: 'Include Email Notifications?' },
    type: 'suggestion',
  },
  {
    id: 's3',
    position: { x: 600, y: 300 },
    data: { label: 'Integrate Stripe for Payments?' },
    type: 'suggestion',
  },
];

const initialEdges: Edge[] = [
  { id: 'e1-2', source: '1', target: '2', animated: true },
  { id: 'e2-3', source: '2', target: '3', animated: true },
];

const IdeationCanvas = () => {
  const [nodes, setNodes] = useState<Node[]>(initialNodes);
  const [edges, setEdges] = useState<Edge[]>(initialEdges);
  const [prompt, setPrompt] = useState('');
  const [showHistory, setShowHistory] = useState(false);
  const { addPromptToHistory } = usePromptStore();

  const onNodesChange: OnNodesChange = useCallback(
    (changes: NodeChange[]) => setNodes((nds) => applyNodeChanges(changes, nds)),
    [setNodes]
  );
  const onEdgesChange: OnEdgesChange = useCallback(
    (changes: EdgeChange[]) => setEdges((eds) => applyEdgeChanges(changes, eds)),
    [setEdges]
  );

  const handlePromptSubmit = () => {
    if (prompt.trim()) {
      addPromptToHistory(prompt);
      // Here you would typically send the prompt to your backend
      console.log('Submitted prompt:', prompt);
      setPrompt('');
    }
  };

  return (
    <motion.div
      className="w-full h-full relative"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.5 }}
    >
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        nodeTypes={nodeTypes}
        fitView
        className="bg-background"
      >
        <Controls />
        <Background />
      </ReactFlow>
      <div className="absolute bottom-4 left-4 right-4 bg-card/80 backdrop-blur-sm p-4 rounded-lg border flex flex-col gap-4">
        <div className="relative">
          <SmartPromptInput
            value={prompt}
            onChange={setPrompt}
            placeholder="Describe your project idea..."
          />
          <div className="absolute top-2 right-2 flex gap-2">
            <ModelSwitcher />
            <button
              onClick={() => setShowHistory(!showHistory)}
              className="p-2 bg-gray-200 dark:bg-gray-700 rounded-md hover:bg-gray-300 dark:hover:bg-gray-600"
            >
              History
            </button>
            <button
              onClick={handlePromptSubmit}
              className="p-2 bg-primary text-primary-foreground rounded-md hover:bg-primary/90"
            >
              Submit
            </button>
          </div>
          {showHistory && (
            <PromptHistory
              onSelectPrompt={(p) => {
                setPrompt(p);
                setShowHistory(false);
              }}
            />
          )}
        </div>
        <PromptAssistant
          currentPrompt={prompt}
          onAppend={(text) => setPrompt(prompt + text)}
        />
      </div>
    </motion.div>
  );
};

export default IdeationCanvas;
