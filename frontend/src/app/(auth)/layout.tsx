import React from 'react';

const AuthLayout = ({ children }: { children: React.ReactNode }) => {
  return (
    <div className="flex items-center justify-center min-h-screen bg-background">
      {children}
    </div>
  );
};

export default AuthLayout;
