import { cn } from '@/lib/utils';

interface StatsSkeletonProps {
  className?: string;
}

export function StatsSkeleton({ className }: StatsSkeletonProps) {
  return (
    <div className={cn('rounded-xl bg-card p-4 shadow-card', className)}>
      <div className="skeleton-shimmer mb-3 h-5 w-24 rounded" />
      <div className="space-y-2">
        <div className="flex items-center justify-between">
          <div className="skeleton-shimmer h-4 w-16 rounded" />
          <div className="skeleton-shimmer h-4 w-8 rounded" />
        </div>
        <div className="flex items-center justify-between">
          <div className="skeleton-shimmer h-4 w-20 rounded" />
          <div className="skeleton-shimmer h-4 w-12 rounded" />
        </div>
      </div>
    </div>
  );
}
