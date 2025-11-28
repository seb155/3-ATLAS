import { FileText, Plus, Search, FolderTree } from 'lucide-react';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';

export function Notes() {
  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Notes & Wiki</h1>
          <p className="text-muted-foreground mt-2">
            Your knowledge base with rich text editing and wiki links
          </p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" size="sm">
            <Search className="h-4 w-4 mr-2" />
            Search
          </Button>
          <Button size="sm" disabled>
            <Plus className="h-4 w-4 mr-2" />
            New Note
          </Button>
        </div>
      </div>

      {/* Coming Soon Notice */}
      <Card>
        <CardContent className="py-12">
          <div className="text-center max-w-2xl mx-auto">
            <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-primary/10 mb-4">
              <FileText className="h-8 w-8 text-primary" />
            </div>
            <h2 className="text-2xl font-bold mb-2">Notes & Wiki Coming in Phase 2</h2>
            <p className="text-muted-foreground mb-6">
              We're building a powerful note-taking system with TipTap editor, hierarchical organization, and wiki-style linking.
            </p>
            <Badge variant="warning">Planned for 3-4 weeks</Badge>
          </div>
        </CardContent>
      </Card>

      {/* Planned Features */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle>Core Features</CardTitle>
            <CardDescription>What's coming in Phase 2</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {[
                'TipTap rich text editor',
                'Markdown support',
                'Hierarchical note organization',
                'Wiki links [[note-name]]',
                'Backlinks panel',
                'Full-text search',
                'Auto-save functionality',
                'Note templates',
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
            <CardTitle>Technical Stack</CardTitle>
            <CardDescription>Technologies we'll use</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {[
                { name: 'TipTap', desc: 'Headless editor framework' },
                { name: 'PostgreSQL', desc: 'Database for notes' },
                { name: 'FastAPI', desc: 'Backend API' },
                { name: 'Full-text Search', desc: 'PostgreSQL tsvector' },
              ].map((tech) => (
                <div key={tech.name} className="border-l-2 border-primary pl-3">
                  <p className="font-medium text-sm">{tech.name}</p>
                  <p className="text-xs text-muted-foreground">{tech.desc}</p>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Preview */}
      <Card>
        <CardHeader>
          <div className="flex items-center gap-2">
            <FolderTree className="h-5 w-5 text-primary" />
            <CardTitle>How It Will Work</CardTitle>
          </div>
          <CardDescription>A preview of the notes interface</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="border-2 border-dashed border-border rounded-lg p-8">
            <div className="flex gap-4">
              <div className="w-48 flex-shrink-0">
                <div className="bg-secondary/50 rounded p-2 mb-2">
                  <p className="text-xs font-semibold mb-2">Note Tree</p>
                  <div className="space-y-1 text-xs">
                    <div>📁 Projects</div>
                    <div className="ml-3">📄 Project A</div>
                    <div className="ml-3">📄 Project B</div>
                    <div>📁 Ideas</div>
                  </div>
                </div>
              </div>
              <div className="flex-1">
                <div className="bg-secondary/50 rounded p-4">
                  <p className="text-xs font-semibold mb-2">Editor</p>
                  <p className="text-xs text-muted-foreground">
                    Rich text editing with formatting, links, images, and more...
                  </p>
                </div>
              </div>
              <div className="w-48 flex-shrink-0">
                <div className="bg-secondary/50 rounded p-2">
                  <p className="text-xs font-semibold mb-2">Backlinks</p>
                  <p className="text-xs text-muted-foreground">
                    See which notes link here
                  </p>
                </div>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
