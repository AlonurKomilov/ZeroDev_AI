'use client';

import React, { useCallback } from 'react';
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

const nodeTypes = {
  suggestion: SuggestionNode,
};

const initialNodes: Node[] = [
  // Mirror Effect Nodes (solid)
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

  // Suggestion Cloud Nodes (transparent)
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
  const [nodes, setNodes] = React.useState<Node[]>(initialNodes);
  const [edges, setEdges] = React.useState<Edge[]>(initialEdges);

  const onNodesChange: OnNodesChange = useCallback(
    (changes: NodeChange[]) => setNodes((nds) => applyNodeChanges(changes, nds)),
    [setNodes]
  );
  const onEdgesChange: OnEdgesChange = useCallback(
    (changes: EdgeChange[]) => setEdges((eds) => applyEdgeChanges(changes, eds)),
    [setEdges]
  );

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
      <div className="absolute top-4 right-4 bg-card/80 backdrop-blur-sm p-3 rounded-lg border">
        <h3 className="font-bold text-lg">Cost Estimator</h3>
        <p className="text-muted-foreground">Calculating...</p>
        <p className="text-2xl font-bold text-primary">$1,234.56</p>
      </div>
    </motion.div>
  );
};

export default IdeationCanvas;
