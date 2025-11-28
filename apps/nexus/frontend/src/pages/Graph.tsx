import { Network, Zap, TrendingUp, Eye } from 'lucide-react';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';

export function Graph() {
  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold">3D Graph Visualization</h1>
        <p className="text-muted-foreground mt-2">
          Visualize your knowledge network in stunning 3D with advanced analytics
        </p>
      </div>

      {/* Coming Soon Notice */}
      <Card>
        <CardContent className="py-12">
          <div className="text-center max-w-2xl mx-auto">
            <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-primary/10 mb-4">
              <Network className="h-8 w-8 text-primary" />
            </div>
            <h2 className="text-2xl font-bold mb-2">3D Graph Coming in Phase 5 ⭐</h2>
            <p className="text-muted-foreground mb-6">
              The flagship feature! InfraNodus-style 3D visualization with advanced network analytics and community detection.
            </p>
            <div className="flex gap-2 justify-center">
              <Badge variant="default">Planned for Q2 2026</Badge>
              <Badge variant="info">Flagship Feature</Badge>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* 3D Preview */}
      <Card>
        <CardHeader>
          <div className="flex items-center gap-2">
            <Eye className="h-5 w-5 text-primary" />
            <CardTitle>Visualization Preview</CardTitle>
          </div>
          <CardDescription>How the 3D graph will look</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="aspect-video border-2 border-dashed border-border rounded-lg flex items-center justify-center" style={{background: 'linear-gradient(135deg, hsl(var(--background)), hsl(var(--secondary) / 0.2))'}}>
            <div className="text-center">
              <Network className="h-16 w-16 text-primary/50 mx-auto mb-4" />
              <p className="text-sm text-muted-foreground">
                3D force-directed graph with WebGL rendering
              </p>
              <p className="text-xs text-muted-foreground mt-1">
                Nodes: Notes, Tasks, Milestones | Edges: Links, References
              </p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Features Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card>
          <CardHeader>
            <div className="flex items-center gap-2">
              <Network className="h-5 w-5 text-blue-500" />
              <CardTitle>Visualization</CardTitle>
            </div>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              {[
                '2D force-directed graph',
                '3D WebGL visualization',
                'Interactive navigation',
                'Node filtering',
                'Custom styling',
                'Export visualizations',
              ].map((feature) => (
                <div key={feature} className="flex items-center gap-2">
                  <div className="h-1.5 w-1.5 rounded-full bg-blue-500" />
                  <span className="text-sm">{feature}</span>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <div className="flex items-center gap-2">
              <Zap className="h-5 w-5 text-purple-500" />
              <CardTitle>Analytics</CardTitle>
            </div>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              {[
                'Betweenness centrality',
                'Degree centrality',
                'PageRank algorithm',
                'Community detection',
                'Gap analysis',
                'Path finding',
              ].map((feature) => (
                <div key={feature} className="flex items-center gap-2">
                  <div className="h-1.5 w-1.5 rounded-full bg-purple-500" />
                  <span className="text-sm">{feature}</span>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <div className="flex items-center gap-2">
              <TrendingUp className="h-5 w-5 text-green-500" />
              <CardTitle>Advanced</CardTitle>
            </div>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              {[
                'Time-series animation',
                'Clustering coefficient',
                'Network metrics',
                'Custom layouts',
                'Semantic zoom',
                'Data export',
              ].map((feature) => (
                <div key={feature} className="flex items-center gap-2">
                  <div className="h-1.5 w-1.5 rounded-full bg-green-500" />
                  <span className="text-sm">{feature}</span>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* InfraNodus Inspiration */}
      <Card>
        <CardHeader>
          <CardTitle>InfraNodus-Inspired Analytics</CardTitle>
          <CardDescription>Advanced network analysis tools</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="border border-border rounded-lg p-4">
              <h4 className="font-semibold text-sm mb-2">Bridge Nodes</h4>
              <p className="text-xs text-muted-foreground">
                Find nodes that connect different communities - high betweenness centrality
              </p>
            </div>
            <div className="border border-border rounded-lg p-4">
              <h4 className="font-semibold text-sm mb-2">Hub Nodes</h4>
              <p className="text-xs text-muted-foreground">
                Identify the most connected nodes in your network - degree centrality
              </p>
            </div>
            <div className="border border-border rounded-lg p-4">
              <h4 className="font-semibold text-sm mb-2">Communities</h4>
              <p className="text-xs text-muted-foreground">
                Detect clusters of related content using Louvain algorithm
              </p>
            </div>
            <div className="border border-border rounded-lg p-4">
              <h4 className="font-semibold text-sm mb-2">Gaps</h4>
              <p className="text-xs text-muted-foreground">
                Find missing connections between concepts to expand your knowledge
              </p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
