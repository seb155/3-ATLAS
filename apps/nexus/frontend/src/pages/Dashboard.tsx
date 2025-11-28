import { FileText, CheckSquare, Network, TrendingUp, Rocket, BookOpen, Calendar } from 'lucide-react';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import { Button } from '@/components/ui/Button';
import { StatCard } from '@/components/ui/StatCard';

export function Dashboard() {
  const stats = [
    { name: 'Notes', value: 0, icon: <FileText className="h-6 w-6" />, color: 'text-blue-500', change: 0, trend: 'neutral' as const },
    { name: 'Tasks', value: 0, icon: <CheckSquare className="h-6 w-6" />, color: 'text-green-500', change: 0, trend: 'neutral' as const },
    { name: 'Connections', value: 0, icon: <Network className="h-6 w-6" />, color: 'text-purple-500', change: 0, trend: 'neutral' as const },
    { name: 'Growth', value: '0%', icon: <TrendingUp className="h-6 w-6" />, color: 'text-orange-500', change: 0, trend: 'neutral' as const },
  ];

  const recentActivity = [
    { type: 'note', title: 'Welcome to Nexus', time: 'Just now', status: 'new' },
    { type: 'system', title: 'Nexus initialized', time: '1 minute ago', status: 'info' },
  ];

  const upcomingFeatures = [
    { name: 'Notes & Wiki', phase: 'Phase 2', status: 'Next', eta: '3-4 weeks' },
    { name: 'Task Management', phase: 'Phase 3', status: 'Planned', eta: 'Q1 2026' },
    { name: '3D Graph Visualization', phase: 'Phase 5', status: 'Planned', eta: 'Q2 2026' },
  ];

  return (
    <div className="space-y-6">
      {/* Hero Section with Animated Gradient */}
      <div className="relative overflow-hidden rounded-2xl p-8">
        {/* Gradient Background */}
        <div className="absolute inset-0" style={{background: 'linear-gradient(135deg, hsl(var(--primary) / 0.1), transparent, hsl(270 100% 65% / 0.05))'}} />

        {/* Animated Mesh Gradient */}
        <div className="absolute inset-0 opacity-30 dark:opacity-20">
          <div className="absolute top-0 -left-4 w-72 h-72 bg-primary rounded-full mix-blend-multiply dark:mix-blend-screen filter blur-xl animate-blob" />
          <div className="absolute top-0 -right-4 w-72 h-72 bg-purple-500 rounded-full mix-blend-multiply dark:mix-blend-screen filter blur-xl animate-blob animation-delay-2000" />
        </div>

        {/* Content */}
        <div className="relative z-10">
          <h1 className="text-4xl md:text-5xl font-bold text-gradient">
            Dashboard
          </h1>
          <p className="text-muted-foreground mt-2 text-lg">
            Welcome to Nexus - Your Knowledge Graph Portal
          </p>
        </div>
      </div>

      {/* Stats Grid with StatCard */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {stats.map((stat) => (
          <StatCard
            key={stat.name}
            title={stat.name}
            value={stat.value}
            change={stat.change}
            trend={stat.trend}
            icon={stat.icon}
            iconColor={stat.color}
          />
        ))}
      </div>

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Getting Started */}
        <Card>
          <CardHeader>
            <div className="flex items-center gap-2">
              <Rocket className="h-5 w-5 text-primary" />
              <CardTitle>Getting Started</CardTitle>
            </div>
            <CardDescription>Follow these steps to explore Nexus</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="flex items-start gap-3">
                <div className="bg-primary text-primary-foreground rounded-full w-6 h-6 flex items-center justify-center flex-shrink-0 text-sm">
                  1
                </div>
                <div className="flex-1">
                  <p className="font-medium">Create your first note</p>
                  <p className="text-sm text-muted-foreground">
                    Start building your knowledge base with rich text notes (Phase 2)
                  </p>
                </div>
              </div>
              <div className="flex items-start gap-3">
                <div className="bg-muted text-muted-foreground rounded-full w-6 h-6 flex items-center justify-center flex-shrink-0 text-sm">
                  2
                </div>
                <div className="flex-1">
                  <p className="font-medium">Add tasks</p>
                  <p className="text-sm text-muted-foreground">
                    Track your work with the integrated task management system (Phase 3)
                  </p>
                </div>
              </div>
              <div className="flex items-start gap-3">
                <div className="bg-muted text-muted-foreground rounded-full w-6 h-6 flex items-center justify-center flex-shrink-0 text-sm">
                  3
                </div>
                <div className="flex-1">
                  <p className="font-medium">Explore the graph</p>
                  <p className="text-sm text-muted-foreground">
                    Visualize connections between your notes and tasks in 3D (Phase 5)
                  </p>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Recent Activity with Timeline */}
        <Card variant="glass">
          <CardHeader>
            <div className="flex items-center gap-2">
              <Calendar className="h-5 w-5 text-primary" />
              <CardTitle>Recent Activity</CardTitle>
            </div>
            <CardDescription>Your latest actions and updates</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="relative">
              {/* Vertical line */}
              <div className="absolute left-2 top-0 bottom-0 w-px bg-border" />

              {/* Activity items */}
              <div className="space-y-4">
                {recentActivity.map((activity, idx) => (
                  <div key={idx} className="relative flex gap-4 pl-6">
                    {/* Dot */}
                    <div className="absolute left-0 top-1 w-4 h-4 rounded-full border-2 border-primary bg-background" />

                    {/* Content */}
                    <div className="flex-1">
                      <p className="text-sm font-medium">{activity.title}</p>
                      <p className="text-xs text-muted-foreground">{activity.time}</p>
                    </div>

                    <Badge variant={activity.status === 'new' ? 'success' : 'info'}>
                      {activity.status}
                    </Badge>
                  </div>
                ))}
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Upcoming Features with Glass Effect */}
      <Card variant="glass" className="overflow-hidden">
        <div className="absolute inset-0 pointer-events-none" style={{background: 'linear-gradient(135deg, hsl(var(--primary) / 0.05), transparent)'}} />

        <CardHeader>
          <div className="flex items-center gap-2">
            <BookOpen className="h-5 w-5 text-primary" />
            <CardTitle>Upcoming Features</CardTitle>
          </div>
          <CardDescription>What's coming next in Nexus development</CardDescription>
        </CardHeader>

        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {upcomingFeatures.map((feature, idx) => (
              <div
                key={idx}
                className="group relative border border-border rounded-lg p-4 hover:border-primary/50 hover:-translate-y-1 transition-all duration-200"
                style={{ animationDelay: `${idx * 100}ms` }}
              >
                {/* Gradient border on hover */}
                <div className="absolute inset-0 rounded-lg opacity-0 group-hover:opacity-100 transition-opacity -z-10" style={{background: 'linear-gradient(90deg, hsl(var(--primary) / 0), hsl(var(--primary) / 0.2), hsl(var(--primary) / 0))'}} />

                <div className="flex items-start justify-between mb-2">
                  <h4 className="font-semibold text-sm">{feature.name}</h4>
                  <Badge variant={feature.status === 'Next' ? 'warning' : 'default'}>
                    {feature.status}
                  </Badge>
                </div>
                <p className="text-xs text-muted-foreground mb-2">{feature.phase}</p>
                <p className="text-xs text-muted-foreground">ETA: {feature.eta}</p>
              </div>
            ))}
          </div>

          <div className="mt-4 flex gap-3">
            <Button variant="outline" size="sm">
              View Full Roadmap
            </Button>
            <Button variant="ghost" size="sm">
              Read Documentation
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
