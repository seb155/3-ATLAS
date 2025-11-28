import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { Badge } from './Badge';

describe('Badge', () => {
    it('renders children content', () => {
        render(<Badge>Active</Badge>);
        expect(screen.getByText('Active')).toBeInTheDocument();
    });

    it('applies default variant classes', () => {
        render(<Badge variant="default">Default</Badge>);
        const badge = screen.getByText('Default');

        expect(badge).toHaveClass('bg-slate-800');
        expect(badge).toHaveClass('text-slate-300');
    });

    it('applies success variant classes', () => {
        render(<Badge variant="success">Success</Badge>);
        const badge = screen.getByText('Success');

        expect(badge).toHaveClass('bg-green-500/10');
        expect(badge).toHaveClass('text-green-400');
    });

    it('applies warning variant classes', () => {
        render(<Badge variant="warning">Warning</Badge>);
        const badge = screen.getByText('Warning');

        expect(badge).toHaveClass('bg-yellow-500/10');
        expect(badge).toHaveClass('text-yellow-400');
    });

    it('applies error variant classes', () => {
        render(<Badge variant="error">Error</Badge>);
        const badge = screen.getByText('Error');

        expect(badge).toHaveClass('bg-red-500/10');
        expect(badge).toHaveClass('text-red-400');
    });

    it('applies info variant classes', () => {
        render(<Badge variant="info">Info</Badge>);
        const badge = screen.getByText('Info');

        expect(badge).toHaveClass('bg-blue-500/10');
        expect(badge).toHaveClass('text-blue-400');
    });

    it('applies outline variant classes', () => {
        render(<Badge variant="outline">Outline</Badge>);
        const badge = screen.getByText('Outline');

        expect(badge).toHaveClass('bg-transparent');
        expect(badge).toHaveClass('border-slate-600');
    });

    it('applies base styles', () => {
        render(<Badge>Badge</Badge>);
        const badge = screen.getByText('Badge');

        expect(badge).toHaveClass('inline-flex');
        expect(badge).toHaveClass('rounded-full');
        expect(badge).toHaveClass('text-xs');
        expect(badge).toHaveClass('border');
    });

    it('applies custom className', () => {
        render(<Badge className="custom-badge">Custom</Badge>);
        const badge = screen.getByText('Custom');

        expect(badge).toHaveClass('custom-badge');
        expect(badge).toHaveClass('inline-flex'); // Base classes should still be there
    });
});
