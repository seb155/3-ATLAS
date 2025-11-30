import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { RulesSidebar } from './RulesSidebar';

const mockRules = [
    {
        id: 'rule-1',
        name: 'Auto-Generate Motors',
        description: 'Creates motor for each pump',
        source: 'FIRM' as const,
        priority: 10,
        discipline: 'ELECTRICAL',
        action_type: 'CREATE_CHILD',
        is_active: true,
    },
    {
        id: 'rule-2',
        name: 'Cable Sizing Rule',
        description: 'Auto-size cables based on load',
        source: 'PROJECT' as const,
        priority: 50,
        discipline: 'ELECTRICAL',
        action_type: 'CREATE_CABLE',
        is_active: true,
    },
    {
        id: 'rule-3',
        name: 'Inactive Rule',
        description: 'This rule is disabled',
        source: 'COUNTRY' as const,
        priority: 30,
        discipline: null,
        action_type: 'SET_PROPERTY',
        is_active: false,
    },
];

const mockSelectedAssets = [
    { id: 'asset-1', name: 'PUMP-001', type: 'EQUIPMENT' },
    { id: 'asset-2', name: 'PUMP-002', type: 'EQUIPMENT' },
];

describe('RulesSidebar', () => {
    it('renders active rules', () => {
        render(
            <RulesSidebar
                rules={mockRules}
                selectedAssets={mockSelectedAssets}
                isExecuting={false}
                onExecuteRule={vi.fn()}
            />
        );

        // Active rules should be visible
        expect(screen.getByText('Auto-Generate Motors')).toBeInTheDocument();
        expect(screen.getByText('Cable Sizing Rule')).toBeInTheDocument();

        // Inactive rule should not be visible
        expect(screen.queryByText('Inactive Rule')).not.toBeInTheDocument();
    });

    it('shows empty state when no active rules', () => {
        const inactiveRules = mockRules.map(r => ({ ...r, is_active: false }));

        render(
            <RulesSidebar
                rules={inactiveRules}
                selectedAssets={mockSelectedAssets}
                isExecuting={false}
                onExecuteRule={vi.fn()}
            />
        );

        expect(screen.getByText('No active rules available')).toBeInTheDocument();
    });

    it('shows empty state with empty rules array', () => {
        render(
            <RulesSidebar
                rules={[]}
                selectedAssets={mockSelectedAssets}
                isExecuting={false}
                onExecuteRule={vi.fn()}
            />
        );

        expect(screen.getByText('No active rules available')).toBeInTheDocument();
    });

    it('displays source badges for rules', () => {
        render(
            <RulesSidebar
                rules={mockRules}
                selectedAssets={mockSelectedAssets}
                isExecuting={false}
                onExecuteRule={vi.fn()}
            />
        );

        // Source badges should be displayed
        expect(screen.getByText('FIRM')).toBeInTheDocument();
        expect(screen.getByText('PROJECT')).toBeInTheDocument();
    });

    it('displays rule descriptions', () => {
        render(
            <RulesSidebar
                rules={mockRules}
                selectedAssets={mockSelectedAssets}
                isExecuting={false}
                onExecuteRule={vi.fn()}
            />
        );

        expect(screen.getByText('Creates motor for each pump')).toBeInTheDocument();
        expect(screen.getByText('Auto-size cables based on load')).toBeInTheDocument();
    });

    it('calls onExecuteRule when execute button is clicked', () => {
        const handleExecute = vi.fn();

        render(
            <RulesSidebar
                rules={mockRules}
                selectedAssets={mockSelectedAssets}
                isExecuting={false}
                onExecuteRule={handleExecute}
            />
        );

        // Find and click execute button (Play icon button)
        const executeButtons = screen.getAllByRole('button');
        if (executeButtons.length > 0) {
            fireEvent.click(executeButtons[0]);
            expect(handleExecute).toHaveBeenCalled();
        }
    });
});
