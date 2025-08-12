'use client';

import React, { useState, useEffect, useRef } from 'react';
import { useVirtualizer } from '@tanstack/react-virtual';

interface Props {
  params: { project_id: string };
}

const GenerationPage = ({ params }: Props) => {
  const [logs, setLogs] = useState<string[]>([]);
  const parentRef = useRef<HTMLDivElement>(null);

  // Mock WebSocket connection
  useEffect(() => {
    const interval = setInterval(() => {
      setLogs((prevLogs) => [
        ...prevLogs,
        `[${new Date().toLocaleTimeString()}] Log message #${prevLogs.length + 1} for project ${params.project_id}`,
      ]);
    }, 100); // Add a new log every 100ms

    return () => clearInterval(interval);
  }, [params.project_id]);

  const rowVirtualizer = useVirtualizer({
    count: logs.length,
    getScrollElement: () => parentRef.current,
    estimateSize: () => 35,
    overscan: 5,
  });

  useEffect(() => {
    // Scroll to the bottom as new logs are added
    if (rowVirtualizer && logs.length > 0) {
      rowVirtualizer.scrollToIndex(logs.length - 1, { align: 'start', behavior: 'smooth' });
    }
  }, [logs.length, rowVirtualizer]);

  return (
    <div className="flex flex-col h-full">
      <h1 className="text-3xl font-bold mb-4">
        Generating Project: <span className="text-primary">{params.project_id}</span>
      </h1>
      <div
        ref={parentRef}
        className="flex-1 overflow-y-auto bg-card rounded-lg p-4 border"
      >
        <div style={{ height: `${rowVirtualizer.getTotalSize()}px`, width: '100%', position: 'relative' }}>
          {rowVirtualizer.getVirtualItems().map((virtualItem) => (
            <div
              key={virtualItem.key}
              style={{
                position: 'absolute',
                top: 0,
                left: 0,
                width: '100%',
                height: `${virtualItem.size}px`,
                transform: `translateY(${virtualItem.start}px)`,
              }}
              className="p-2 font-mono text-sm"
            >
              <code>{logs[virtualItem.index]}</code>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default GenerationPage;
