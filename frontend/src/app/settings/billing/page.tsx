import React from 'react';

const paymentHistory = [
  { date: '2023-08-01', amount: '$20.00', status: 'Paid' },
  { date: '2023-07-01', amount: '$20.00', status: 'Paid' },
  { date: '2023-06-01', amount: '$20.00', status: 'Paid' },
];

export default function BillingPage() {
  return (
    <div>
      <h2 className="text-2xl font-bold mb-4">Billing & Subscription</h2>

      <div className="mb-8">
        <h3 className="text-xl font-semibold mb-2">Current Plan</h3>
        <p className="text-gray-600">You are on the <span className="font-bold text-blue-600">Pro Plan</span>.</p>
        <button className="mt-4 bg-blue-500 text-white font-bold py-2 px-4 rounded hover:bg-blue-700">
          Manage Subscription
        </button>
      </div>

      <div>
        <h3 className="text-xl font-semibold mb-4">Payment History</h3>
        <div className="overflow-x-auto">
          <table className="min-w-full bg-white border">
            <thead className="bg-gray-200">
              <tr>
                <th className="py-2 px-4 border-b">Date</th>
                <th className="py-2 px-4 border-b">Amount</th>
                <th className="py-2 px-4 border-b">Status</th>
              </tr>
            </thead>
            <tbody>
              {paymentHistory.map((payment, index) => (
                <tr key={index} className="text-center">
                  <td className="py-2 px-4 border-b">{payment.date}</td>
                  <td className="py-2 px-4 border-b">{payment.amount}</td>
                  <td className="py-2 px-4 border-b">
                    <span className="bg-green-200 text-green-800 py-1 px-3 rounded-full text-sm">{payment.status}</span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
