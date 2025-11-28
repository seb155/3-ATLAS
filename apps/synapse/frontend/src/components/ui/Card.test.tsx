import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { Card } from './Card';

describe('Card', () => {
    it('renders children content', () => {
        render(
            <Card>
                <p>Card content</p>
            </Card>
        );

        expect(screen.getByText('Card content')).toBeInTheDocument();
    });

    it('renders with title', () => {
        render(<Card title="Card Title">Content</Card>);

        expect(screen.getByText('Card Title')).toBeInTheDocument();
        expect(screen.getByText('Content')).toBeInTheDocument();
    });

    it('renders with description', () => {
        render(<Card description="Card description">Content</Card>);

        expect(screen.getByText('Card description')).toBeInTheDocument();
    });

    it('renders with title and description', () => {
        render(
            <Card title="Title" description="Description">
                Content
            </Card>
        );

        expect(screen.getByText('Title')).toBeInTheDocument();
        expect(screen.getByText('Description')).toBeInTheDocument();
    });

    it('renders with footer', () => {
        render(
            <Card footer={<div>Footer content</div>}>
                Main content
            </Card>
        );

        expect(screen.getByText('Footer content')).toBeInTheDocument();
        expect(screen.getByText('Main content')).toBeInTheDocument();
    });

    it('applies base styles', () => {
        const { container } = render(<Card>Content</Card>);
        const card = container.firstChild as HTMLElement;

        expect(card).toHaveClass('bg-slate-900');
        expect(card).toHaveClass('border');
        expect(card).toHaveClass('rounded-xl');
    });

    it('applies custom className', () => {
        const { container } = render(<Card className="custom-card">Content</Card>);
        const card = container.firstChild as HTMLElement;

        expect(card).toHaveClass('custom-card');
        expect(card).toHaveClass('bg-slate-900'); // Base classes should still be there
    });

    it('does not render header when no title or description', () => {
        const { container } = render(<Card>Content</Card>);
        const header = container.querySelector('.border-b');

        expect(header).not.toBeInTheDocument();
    });

    it('does not render footer when not provided', () => {
        const { container } = render(<Card>Content</Card>);
        const footer = container.querySelector('.bg-slate-950\\/50');

        expect(footer).not.toBeInTheDocument();
    });
});
