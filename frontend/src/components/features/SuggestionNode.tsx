'use client';

import { motion } from 'framer-motion';
import { Handle, Position, NodeProps } from 'reactflow';

const SuggestionNode = ({ data }: NodeProps) => {
  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.8 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.3 }}
      whileHover={{ scale: 1.05 }}
      className="bg-primary/20 border border-primary/50 rounded-lg p-4 w-48 h-24 flex items-center justify-center text-center"
    >
      <Handle type="target" position={Position.Top} className="!bg-primary" />
      <div>{data.label}</div>
      <Handle type="source" position={Position.Bottom} className="!bg-primary" />
    </motion.div>
  );
};

export default SuggestionNode;
