import * as DropdownMenu from '@radix-ui/react-dropdown-menu';
import { Copy, Edit, GitBranch, Zap, Undo, Trash2, ChevronRight } from 'lucide-react';
import toast from 'react-hot-toast';

interface ContextMenuProps {
    children: React.ReactNode;
    entityType: 'asset' | 'cable' | 'rule';
    entityTag: string;
    onEdit?: () => void;
    onDelete?: () => void;
    onViewRelationships?: () => void;
    onRunRules?: () => void;
    onRollback?: () => void;
}

export function ContextMenu({
    children,
    entityType,
    entityTag,
    onEdit,
    onDelete,
    onViewRelationships,
    onRunRules,
    onRollback
}: ContextMenuProps) {
    const handleCopyTag = () => {
        navigator.clipboard.writeText(entityTag);
        toast.success(`Copied: ${entityTag}`);
    };

    const handleEdit = () => {
        onEdit?.();
        toast.success(`Edit ${entityType}: ${entityTag}`);
    };

    const handleViewRelationships = () => {
        onViewRelationships?.();
        toast.success(`View relationships for ${entityTag}`);
    };

    const handleRunRules = () => {
        onRunRules?.();
        toast.success(`Running rules on ${entityTag}...`);
    };

    const handleRollback = () => {
        onRollback?.();
        toast.success(`Rollback last action on ${entityTag}`);
    };

    const handleDelete = () => {
        onDelete?.();
        toast.error(`Delete ${entityTag} (placeholder)`);
    };

    return (
        <DropdownMenu.Root>
            <DropdownMenu.Trigger asChild>
                {children}
            </DropdownMenu.Trigger>

            <DropdownMenu.Portal>
                <DropdownMenu.Content
                    className="min-w-[220px] bg-slate-900 border border-slate-700 rounded-lg shadow-xl p-1 z-50"
                    sideOffset={5}
                >
                    {/* Copy Tag */}
                    <DropdownMenu.Item
                        className="flex items-center gap-3 px-3 py-2 text-sm text-slate-300 rounded cursor-pointer outline-none hover:bg-slate-800 focus:bg-slate-800"
                        onSelect={handleCopyTag}
                    >
                        <Copy size={16} />
                        <span>Copy Tag</span>
                        <kbd className="ml-auto text-xs text-slate-500">Ctrl+C</kbd>
                    </DropdownMenu.Item>

                    <DropdownMenu.Separator className="h-px bg-slate-800 my-1" />

                    {/* Edit Properties */}
                    <DropdownMenu.Item
                        className="flex items-center gap-3 px-3 py-2 text-sm text-slate-300 rounded cursor-pointer outline-none hover:bg-slate-800 focus:bg-slate-800"
                        onSelect={handleEdit}
                    >
                        <Edit size={16} />
                        <span>Edit Properties</span>
                    </DropdownMenu.Item>

                    {/* View Relationships */}
                    <DropdownMenu.Item
                        className="flex items-center gap-3 px-3 py-2 text-sm text-slate-300 rounded cursor-pointer outline-none hover:bg-slate-800 focus:bg-slate-800"
                        onSelect={handleViewRelationships}
                    >
                        <GitBranch size={16} />
                        <span>View Relationships</span>
                        <ChevronRight size={14} className="ml-auto text-slate-500" />
                    </DropdownMenu.Item>

                    {/* Run Rules */}
                    <DropdownMenu.Item
                        className="flex items-center gap-3 px-3 py-2 text-sm text-slate-300 rounded cursor-pointer outline-none hover:bg-slate-800 focus:bg-slate-800"
                        onSelect={handleRunRules}
                    >
                        <Zap size={16} />
                        <span>Run Rules</span>
                    </DropdownMenu.Item>

                    <DropdownMenu.Separator className="h-px bg-slate-800 my-1" />

                    {/* Rollback Last Action */}
                    <DropdownMenu.Item
                        className="flex items-center gap-3 px-3 py-2 text-sm text-slate-300 rounded cursor-pointer outline-none hover:bg-slate-800 focus:bg-slate-800"
                        onSelect={handleRollback}
                    >
                        <Undo size={16} />
                        <span>Rollback Last Action</span>
                    </DropdownMenu.Item>

                    <DropdownMenu.Separator className="h-px bg-slate-800 my-1" />

                    {/* Delete */}
                    <DropdownMenu.Item
                        className="flex items-center gap-3 px-3 py-2 text-sm text-red-400 rounded cursor-pointer outline-none hover:bg-red-950/50 focus:bg-red-950/50"
                        onSelect={handleDelete}
                    >
                        <Trash2 size={16} />
                        <span>Delete</span>
                        <kbd className="ml-auto text-xs text-red-500/70">Del</kbd>
                    </DropdownMenu.Item>
                </DropdownMenu.Content>
            </DropdownMenu.Portal>
        </DropdownMenu.Root>
    );
}
