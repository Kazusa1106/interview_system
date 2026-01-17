import { lazy, Suspense, type ComponentType } from 'react';

interface LazyComponentProps {
  fallback?: React.ReactNode;
}

function DefaultFallback() {
  return (
    <div className="flex h-full items-center justify-center">
      <div className="skeleton-shimmer h-8 w-32 rounded" />
    </div>
  );
}

export function lazyLoad<T extends ComponentType<unknown>>(
  importFn: () => Promise<{ default: T }>,
  fallback?: React.ReactNode
) {
  const LazyComponent = lazy(importFn);

  return function LazyWrapper(props: React.ComponentProps<T> & LazyComponentProps) {
    return (
      <Suspense fallback={fallback ?? props.fallback ?? <DefaultFallback />}>
        <LazyComponent {...props} />
      </Suspense>
    );
  };
}

export const LazyChatbot = lazyLoad(
  () => import('@/components/chat/Chatbot').then((m) => ({ default: m.Chatbot }))
);

export const LazyCommandPalette = lazyLoad(
  () => import('@/components/common/CommandPalette').then((m) => ({ default: m.CommandPalette }))
);
