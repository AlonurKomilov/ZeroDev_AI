import React from 'react';

export const Button = React.forwardRef<
  HTMLButtonElement,
  React.ButtonHTMLAttributes<HTMLButtonElement>
>(({ className, ...props }, ref) => {
  return (
    <button
      className={`p-2 rounded-md ${className}`}
      ref={ref}
      {...props}
    />
  );
});

Button.displayName = 'Button';
