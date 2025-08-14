// frontend/src/app/subscribe/page.tsx
import React from 'react';

const tiers = [
  {
    name: 'Free',
    price: '$0',
    features: [
      'Basic feature 1',
      'Basic feature 2',
      'Basic feature 3',
    ],
    buttonText: 'Current Plan',
    buttonDisabled: true,
  },
  {
    name: 'Pro',
    price: '$20/month',
    features: [
      'All features in Free',
      'Advanced feature 1',
      'Advanced feature 2',
      'Priority support',
    ],
    buttonText: 'Upgrade to Pro',
    buttonDisabled: false,
  },
];

const SubscribePage = () => {
  return (
    <div className="container mx-auto p-4">
      <h1 className="text-3xl font-bold text-center mb-10">Choose Your Plan</h1>
      <div className="flex justify-center gap-8">
        {tiers.map((tier) => (
          <div key={tier.name} className="border rounded-lg p-6 w-80 text-center flex flex-col">
            <h2 className="text-2xl font-semibold mb-4">{tier.name}</h2>
            <p className="text-4xl font-bold mb-6">{tier.price}</p>
            <ul className="text-left mb-8 flex-grow">
              {tier.features.map((feature, index) => (
                <li key={index} className="mb-2">- {feature}</li>
              ))}
            </ul>
            <button
              className={`w-full py-2 px-4 rounded font-bold ${tier.buttonDisabled ? 'bg-gray-400' : 'bg-blue-500 hover:bg-blue-700 text-white'}`}
              disabled={tier.buttonDisabled}
            >
              {tier.buttonText}
            </button>
          </div>
        ))}
      </div>
    </div>
  );
};

export default SubscribePage;
