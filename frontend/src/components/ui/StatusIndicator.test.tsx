import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import StatusIndicator from './StatusIndicator';

describe('StatusIndicator', () => {
  it('renders the status message correctly', () => {
    const status = 'Testing status...';
    render(<StatusIndicator status={status} />);

    expect(screen.getByText('Status:')).toBeInTheDocument();
    expect(screen.getByText(status)).toBeInTheDocument();
  });

  it('displays a different status message', () => {
    const status = 'Another test status';
    render(<StatusIndicator status={status} />);

    expect(screen.getByText(status)).toBeInTheDocument();
  });
});
