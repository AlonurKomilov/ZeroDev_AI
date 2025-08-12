import React from 'react';

const FeedbackManagement = () => {
  return (
    <div className="bg-white dark:bg-gray-800 shadow-md rounded-lg p-6">
      <h2 className="text-2xl font-semibold mb-4">User Feedback</h2>
      {/* Placeholder for a table */}
      <div className="overflow-x-auto">
        <table className="min-w-full">
          <thead>
            <tr>
              <th className="px-6 py-3 border-b-2 border-gray-300 dark:border-gray-700 text-left text-xs font-semibold text-gray-600 dark:text-gray-300 uppercase tracking-wider">User</th>
              <th className="px-6 py-3 border-b-2 border-gray-300 dark:border-gray-700 text-left text-xs font-semibold text-gray-600 dark:text-gray-300 uppercase tracking-wider">Feedback</th>
              <th className="px-6 py-3 border-b-2 border-gray-300 dark:border-gray-700 text-left text-xs font-semibold text-gray-600 dark:text-gray-300 uppercase tracking-wider">Status</th>
            </tr>
          </thead>
          <tbody className="bg-white dark:bg-gray-800">
            <tr>
              <td className="px-6 py-4 whitespace-nowrap border-b border-gray-200 dark:border-gray-700">user@example.com</td>
              <td className="px-6 py-4 whitespace-nowrap border-b border-gray-200 dark:border-gray-700">Great platform!</td>
              <td className="px-6 py-4 whitespace-nowrap border-b border-gray-200 dark:border-gray-700">
                <span className="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-green-100 text-green-800">
                  Reviewed
                </span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default FeedbackManagement;
