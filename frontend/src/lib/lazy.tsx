import {
  lazy,
  Suspense,
  type ComponentType,
  type ReactNode,
} from 'react';

interface LazyComponentProps {
  fallback?: ReactNode;
}

function DefaultFallback() {
  return (
    <div className="flex h-full items-center justify-center">
      <div className="skeleton-shimmer h-8 w-32 rounded" />
    </div>
  );
}

export function lazyLoad<P extends object>(
  importFn: () => Promise<{ default: ComponentType<P> }>,
  fallback?: ReactNode
) {
  const LazyComponent = lazy(importFn);

  return function LazyWrapper(props: LazyComponentProps & P) {
    const { fallback: fallbackProp, ...rest } = props;
    return (
      <Suspense fallback={fallback ?? fallbackProp ?? <DefaultFallback />}>
        <LazyComponent {...rest} />
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
