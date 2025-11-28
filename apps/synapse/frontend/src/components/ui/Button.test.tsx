import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { Button } from './Button';
import { Download } from 'lucide-react';

describe('Button', () => {
    it('renders with text', () => {
        render(<Button>Click me</Button>);
        expect(screen.getByText('Click me')).toBeInTheDocument();
    });

    it('handles click events', () => {
        const handleClick = vi.fn();
        render(<Button onClick={handleClick}>Click me</Button>);

        const button = screen.getByText('Click me');
        fireEvent.click(button);

        expect(handleClick).toHaveBeenCalledTimes(1);
    });

    it('renders with left icon', () => {
        render(
            <Button leftIcon={<Download data-testid="left-icon" />}>
                Download
            </Button>
        );

        expect(screen.getByTestId('left-icon')).toBeInTheDocument();
        expect(screen.getByText('Download')).toBeInTheDocument();
    });

    it('renders with right icon', () => {
        render(
            <Button rightIcon={<Download data-testid="right-icon" />}>
                Download
            </Button>
        );

        expect(screen.getByTestId('right-icon')).toBeInTheDocument();
        expect(screen.getByText('Download')).toBeInTheDocument();
    });

    it('applies primary variant classes', () => {
        render(<Button variant="primary">Primary</Button>);
        const button = screen.getByText('Primary');
        expect(button).toHaveClass('bg-mining-teal');
    });

    it('applies secondary variant classes', () => {
        render(<Button variant="secondary">Secondary</Button>);
        const button = screen.getByText('Secondary');
        expect(button).toHaveClass('bg-slate-800');
    });

    it('applies ghost variant classes', () => {
        render(<Button variant="ghost">Ghost</Button>);
        const button = screen.getByText('Ghost');
        expect(button).toHaveClass('text-slate-400');
    });

    it('applies danger variant classes', () => {
        render(<Button variant="danger">Danger</Button>);
        const button = screen.getByText('Danger');
        expect(button).toHaveClass('bg-red-600');
    });

    it('applies outline variant classes', () => {
        render(<Button variant="outline">Outline</Button>);
        const button = screen.getByText('Outline');
        expect(button).toHaveClass('border');
        expect(button).toHaveClass('border-slate-700');
    });

    it('applies small size classes', () => {
        render(<Button size="sm">Small</Button>);
        const button = screen.getByText('Small');
        expect(button).toHaveClass('px-3');
        expect(button).toHaveClass('py-1.5');
    });

    it('applies large size classes', () => {
        render(<Button size="lg">Large</Button>);
        const button = screen.getByText('Large');
        expect(button).toHaveClass('px-6');
        expect(button).toHaveClass('py-3');
    });

    it('respects disabled state', () => {
        const handleClick = vi.fn();
        render(<Button disabled onClick={handleClick}>Disabled</Button>);

        const button = screen.getByText('Disabled');
        expect(button).toBeDisabled();

        fireEvent.click(button);
        expect(handleClick).not.toHaveBeenCalled();
    });

    it('shows loading state', () => {
        render(<Button isLoading>Loading</Button>);
        const button = screen.getByText('Loading');

        expect(button).toBeDisabled();
        expect(button.querySelector('svg.animate-spin')).toBeInTheDocument();
    });

    it('hides icons when loading', () => {
        render(
            <Button
                isLoading
                leftIcon={<Download data-testid="left-icon" />}
                rightIcon={<Download data-testid="right-icon" />}
            >
                Loading
            </Button>
        );

        expect(screen.queryByTestId('left-icon')).not.toBeInTheDocument();
        expect(screen.queryByTestId('right-icon')).not.toBeInTheDocument();
    });

    it('applies custom className', () => {
        render(<Button className="custom-class">Custom</Button>);
        const button = screen.getByText('Custom');
        expect(button).toHaveClass('custom-class');
    });
});
