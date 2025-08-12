import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import Topbar from './Topbar';

describe('Topbar', () => {
  it('renders the topbar with a title', () => {
    render(<Topbar />);
    const headingElement = screen.getByRole('heading', { name: /topbar/i });
    expect(headingElement).toBeInTheDocument();
  });
});
