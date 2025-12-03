import { CheckSquare, Plus, Filter, LayoutGrid } from 'lucide-react';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';

export function Tasks() {
  const kanbanPreview = [
    { title: 'Backlog', count: 0, color: 'bg-gray-500' },
    { title: 'Todo', count: 0, color: 'bg-blue-500' },
    { title: 'In Progress', count: 0, color: 'bg-yellow-500' },
    { title: 'Done', count: 0, color: 'bg-green-500' },
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Task Management</h1>
          <p className="text-muted-foreground mt-2">
            Kanban boards and task tracking for project management
          </p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" size="sm" disabled>
            <Filter className="h-4 w-4 mr-2" />
            Filter
          </Button>
          <Button size="sm" disabled>
            <Plus className="h-4 w-4 mr-2" />
            New Task
          </Button>
        </div>
      </div>

      {/* Coming Soon Notice */}
      <Card>
        <CardContent className="py-12">
          <div className="text-center max-w-2xl mx-auto">
            <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-primary/10 mb-4">
              <CheckSquare className="h-8 w-8 text-primary" />
            </div>
            <h2 className="text-2xl font-bold mb-2">Task Management Coming in Phase 3</h2>
            <p className="text-muted-foreground mb-6">
              We're building a comprehensive task management system with Kanban boards, labels, and integration with notes.
            </p>
            <Badge variant="default">Planned for Q1 2026</Badge>
          </div>
        </CardContent>
      </Card>

      {/* Kanban Preview */}
      <Card>
        <CardHeader>
          <div className="flex items-center gap-2">
            <LayoutGrid className="h-5 w-5 text-primary" />
            <CardTitle>Kanban Board Preview</CardTitle>
          </div>
          <CardDescription>Drag-and-drop task management</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-4 gap-4">
            {kanbanPreview.map((column) => (
              <div key={column.title} className="border border-border rounded-lg p-4">
                <div className="flex items-center justify-between mb-3">
                  <div className="flex items-center gap-2">
                    <div className={`h-2 w-2 rounded-full ${column.color}`} />
                    <h4 className="font-semibold text-sm">{column.title}</h4>
                  </div>
                  <Badge variant="default">{column.count}</Badge>
                </div>
                <div className="h-32 border-2 border-dashed border-border rounded flex items-center justify-center">
                  <p className="text-xs text-muted-foreground">No tasks yet</p>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Features Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle>Planned Features</CardTitle>
            <CardDescription>What's coming in Phase 3</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {[
                'Drag-and-drop Kanban board',
                'Task CRUD operations',
                'Task detail panel',
                'Comments and discussions',
                'Labels and tags',
                'Assignees and due dates',
                'Link tasks to notes',
                'Task search and filters',
              ].map((feature) => (
                <div key={feature} className="flex items-center gap-2">
                  <div className="h-1.5 w-1.5 rounded-full bg-primary" />
                  <span className="text-sm">{feature}</span>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Integration</CardTitle>
            <CardDescription>Connected with other features</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="border-l-2 border-primary pl-3">
                <p className="font-medium text-sm">Notes Integration</p>
                <p className="text-xs text-muted-foreground mt-1">
                  Link tasks to relevant notes and documentation
                </p>
              </div>
              <div className="border-l-2 border-green-500 pl-3">
                <p className="font-medium text-sm">Roadmap Integration</p>
                <p className="text-xs text-muted-foreground mt-1">
                  Tasks feed into roadmap timeline and milestones
                </p>
              </div>
              <div className="border-l-2 border-purple-500 pl-3">
                <p className="font-medium text-sm">Graph Visualization</p>
                <p className="text-xs text-muted-foreground mt-1">
                  See task relationships in the 3D knowledge graph
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
