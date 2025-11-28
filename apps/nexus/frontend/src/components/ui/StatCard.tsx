import type { ReactNode } from 'react';
import { cn } from '@/lib/utils';
import { TrendingUp, TrendingDown, Minus } from 'lucide-react';

interface StatCardProps {
  title: string;
  value: string | number;
  change?: number;
  trend?: 'up' | 'down' | 'neutral';
  icon?: ReactNode;
  iconColor?: string;
  className?: string;
}

export function StatCard({
  title,
  value,
  change,
  trend = 'neutral',
  icon,
  iconColor = 'text-primary',
  className
}: StatCardProps) {
  const trendColors = {
    up: 'text-green-500',
    down: 'text-red-500',
    neutral: 'text-muted-foreground'
  };

  const TrendIcon = {
    up: TrendingUp,
    down: TrendingDown,
    neutral: Minus
  }[trend];

  return (
    <div
      className={cn(
        'relative overflow-hidden rounded-lg border border-border bg-card p-6',
        'hover:shadow-lg hover:border-primary/50 hover:-translate-y-1',
        'transition-all duration-200',
        className
      )}
    >
      <div className="flex items-center justify-between">
        <div className="flex-1">
          <p className="text-sm font-medium text-muted-foreground">{title}</p>
          <p className="text-3xl font-bold mt-2">{value}</p>

          {change !== undefined && (
            <div className={cn('flex items-center gap-1 mt-2 text-sm', trendColors[trend])}>
              <TrendIcon className="h-4 w-4" />
              <span>{change > 0 ? '+' : ''}{change}%</span>
            </div>
          )}
        </div>

        {icon && (
          <div className={cn(
            'flex items-center justify-center',
            'h-12 w-12 rounded-full',
            iconColor
          )}
          style={{background: 'linear-gradient(135deg, hsl(var(--primary) / 0.1), hsl(var(--primary) / 0.05))'}}
          >
            {icon}
          </div>
        )}
      </div>
    </div>
  );
}
