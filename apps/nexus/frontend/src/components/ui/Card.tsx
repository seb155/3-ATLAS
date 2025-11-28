import type { ReactNode } from 'react';
import { cn } from '@/lib/utils';

interface CardProps {
  children: ReactNode;
  className?: string;
  variant?: 'default' | 'glass' | 'gradient' | 'elevated';
  hover?: boolean;
  glow?: boolean;
}

export function Card({
  children,
  className,
  variant = 'default',
  hover = false,
  glow = false
}: CardProps) {
  const variants = {
    default: 'border border-border bg-card',
    glass: 'glass',
    gradient: 'relative border-0 bg-card',
    elevated: 'border-0 bg-card shadow-elegant-lg'
  };

  return (
    <div
      className={cn(
        'rounded-lg p-6',
        variants[variant],
        hover && 'hover:shadow-lg hover:border-primary/50 hover:-translate-y-1 transition-all duration-200',
        glow && 'hover:shadow-glow',
        className
      )}
    >
      {children}
    </div>
  );
}

interface CardHeaderProps {
  children: ReactNode;
  className?: string;
}

export function CardHeader({ children, className }: CardHeaderProps) {
  return <div className={cn('mb-4', className)}>{children}</div>;
}

interface CardTitleProps {
  children: ReactNode;
  className?: string;
}

export function CardTitle({ children, className }: CardTitleProps) {
  return <h3 className={cn('text-xl font-semibold', className)}>{children}</h3>;
}

interface CardDescriptionProps {
  children: ReactNode;
  className?: string;
}

export function CardDescription({ children, className }: CardDescriptionProps) {
  return <p className={cn('text-sm text-muted-foreground mt-1', className)}>{children}</p>;
}

interface CardContentProps {
  children: ReactNode;
  className?: string;
}

export function CardContent({ children, className }: CardContentProps) {
  return <div className={cn(className)}>{children}</div>;
}
