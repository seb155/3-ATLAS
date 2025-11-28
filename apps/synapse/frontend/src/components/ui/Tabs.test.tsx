import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { Tabs } from './Tabs';
import { Home, Settings, User } from 'lucide-react';

describe('Tabs', () => {
    const basicTabs = [
        { id: 'tab1', label: 'Tab 1' },
        { id: 'tab2', label: 'Tab 2' },
        { id: 'tab3', label: 'Tab 3' }
    ];

    const tabsWithIcons = [
        { id: 'home', label: 'Home', icon: Home },
        { id: 'settings', label: 'Settings', icon: Settings },
        { id: 'profile', label: 'Profile', icon: User }
    ];

    const tabsWithCounts = [
        { id: 'all', label: 'All', count: 10 },
        { id: 'active', label: 'Active', count: 5 },
        { id: 'pending', label: 'Pending', count: 3 }
    ];

    it('renders all tabs', () => {
        const handleChange = vi.fn();
        render(<Tabs tabs={basicTabs} activeTab="tab1" onChange={handleChange} />);

        expect(screen.getByText('Tab 1')).toBeInTheDocument();
        expect(screen.getByText('Tab 2')).toBeInTheDocument();
        expect(screen.getByText('Tab 3')).toBeInTheDocument();
    });

    it('highlights active tab', () => {
        const handleChange = vi.fn();
        render(<Tabs tabs={basicTabs} activeTab="tab2" onChange={handleChange} />);

        const activeTab = screen.getByText('Tab 2').closest('button');
        const inactiveTab = screen.getByText('Tab 1').closest('button');

        expect(activeTab).toHaveClass('border-mining-teal');
        expect(activeTab).toHaveClass('text-mining-teal');

        expect(inactiveTab).toHaveClass('border-transparent');
        expect(inactiveTab).toHaveClass('text-slate-400');
    });

    it('calls onChange when tab is clicked', () => {
        const handleChange = vi.fn();
        render(<Tabs tabs={basicTabs} activeTab="tab1" onChange={handleChange} />);

        const tab2 = screen.getByText('Tab 2');
        fireEvent.click(tab2);

        expect(handleChange).toHaveBeenCalledWith('tab2');
        expect(handleChange).toHaveBeenCalledTimes(1);
    });

    it('renders tabs with icons', () => {
        const handleChange = vi.fn();
        const { container } = render(
            <Tabs tabs={tabsWithIcons} activeTab="home" onChange={handleChange} />
        );

        // Check that icons are rendered (Lucide icons render as SVG)
        const svgs = container.querySelectorAll('svg');
        expect(svgs.length).toBeGreaterThanOrEqual(3);
    });

    it('renders tabs with count badges', () => {
        const handleChange = vi.fn();
        render(<Tabs tabs={tabsWithCounts} activeTab="all" onChange={handleChange} />);

        expect(screen.getByText('10')).toBeInTheDocument();
        expect(screen.getByText('5')).toBeInTheDocument();
        expect(screen.getByText('3')).toBeInTheDocument();
    });

    it('does not render count when count is undefined', () => {
        const handleChange = vi.fn();
        render(<Tabs tabs={basicTabs} activeTab="tab1" onChange={handleChange} />);

        const tab1 = screen.getByText('Tab 1').closest('button');
        const countBadge = tab1?.querySelector('.bg-slate-800.rounded-full');

        expect(countBadge).not.toBeInTheDocument();
    });

    it('applies custom className to container', () => {
        const handleChange = vi.fn();
        const { container } = render(
            <Tabs
                tabs={basicTabs}
                activeTab="tab1"
                onChange={handleChange}
                className="custom-tabs"
            />
        );

        const tabsContainer = container.firstChild as HTMLElement;
        expect(tabsContainer).toHaveClass('custom-tabs');
    });

    it('calls onChange with correct tab id for each tab', () => {
        const handleChange = vi.fn();
        render(<Tabs tabs={basicTabs} activeTab="tab1" onChange={handleChange} />);

        fireEvent.click(screen.getByText('Tab 1'));
        expect(handleChange).toHaveBeenLastCalledWith('tab1');

        fireEvent.click(screen.getByText('Tab 2'));
        expect(handleChange).toHaveBeenLastCalledWith('tab2');

        fireEvent.click(screen.getByText('Tab 3'));
        expect(handleChange).toHaveBeenLastCalledWith('tab3');

        expect(handleChange).toHaveBeenCalledTimes(3);
    });

    it('applies base styles to all tabs', () => {
        const handleChange = vi.fn();
        render(<Tabs tabs={basicTabs} activeTab="tab1" onChange={handleChange} />);

        const allTabs = screen.getAllByRole('button');
        allTabs.forEach(tab => {
            expect(tab).toHaveClass('flex');
            expect(tab).toHaveClass('items-center');
            expect(tab).toHaveClass('px-4');
            expect(tab).toHaveClass('py-3');
        });
    });
});
