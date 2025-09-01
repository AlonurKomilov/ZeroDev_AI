import React from 'react';
import Link from 'next/link';

const Sidebar = () => {
  return (
    <aside className="w-64 bg-card text-card-foreground p-4 border-r flex flex-col">
      <h2 className="text-lg font-bold mb-4">Sidebar</h2>

      {/* Spacer to push the upgrade button to the bottom */}
      <div className="flex-grow"></div>

      <Link href="/subscribe" passHref>
        <button className="w-full bg-green-500 text-white font-bold py-2 px-4 rounded hover:bg-green-700">
          Upgrade to Pro
        </button>
      </Link>
    </aside>
  );
};

export default Sidebar;
