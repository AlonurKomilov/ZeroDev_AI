import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import AdvancedFeedback from './AdvancedFeedback';

describe('AdvancedFeedback', () => {
  const code = 'line 1\nline 2\nline 3';

  it('renders the code and allows selecting a line', () => {
    render(<AdvancedFeedback code={code} onSubmitFeedback={() => {}} />);

    // Check if lines are rendered
    expect(screen.getByText('line 1')).toBeInTheDocument();
    expect(screen.getByText('line 2')).toBeInTheDocument();

    // Click on the second line
    fireEvent.click(screen.getByText('line 2'));

    // Check if the feedback form appears for the correct line
    expect(screen.getByText('Feedback for line 2:')).toBeInTheDocument();
  });

  it('allows typing a comment and submitting feedback', () => {
    const handleSubmit = vi.fn();
    render(<AdvancedFeedback code={code} onSubmitFeedback={handleSubmit} />);

    // Select line 1
    fireEvent.click(screen.getByText('line 1'));

    // Type a comment
    const textarea = screen.getByPlaceholderText('Leave your comment...');
    fireEvent.change(textarea, { target: { value: 'This is a test comment' } });

    // Submit the form
    fireEvent.click(screen.getByText('Submit Feedback'));

    // Check if the submit handler was called with the correct data
    expect(handleSubmit).toHaveBeenCalledWith({
      line: 1,
      comment: 'This is a test comment',
    });
  });
});
