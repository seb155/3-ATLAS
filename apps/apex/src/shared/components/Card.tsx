import { ReactNode } from 'react';
import clsx from 'clsx';

type CardProps = {
  title?: string;
  description?: string;
  children: ReactNode;
  className?: string;
  action?: ReactNode;
};

export function Card({ title, description, children, className, action }: CardProps) {
  return (
    <div
      className={clsx(
        'glass rounded-xl border border-white/5 p-5 shadow-glass backdrop-blur',
        className,
      )}
    >
      {(title || description || action) && (
        <div className="mb-3 flex items-start justify-between gap-4">
          <div>
            {title && <h3 className="text-base font-semibold text-white">{title}</h3>}
            {description && <p className="text-sm text-slate-400">{description}</p>}
          </div>
          {action ? <div className="shrink-0">{action}</div> : null}
        </div>
      )}
      {children}
    </div>
  );
}
