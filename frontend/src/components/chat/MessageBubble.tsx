import type { Message } from '@/types';
import { cn } from '@/lib/utils';

interface MessageBubbleProps {
  message: Message;
}

export function MessageBubble({ message }: MessageBubbleProps) {
  const isUser = message.role === 'user';
  const timestamp = new Date(message.timestamp).toLocaleTimeString('zh-CN', {
    hour: '2-digit',
    minute: '2-digit',
  });

  return (
    <div
      className={cn(
        'flex w-full',
        isUser ? 'justify-end slide-in-right' : 'justify-start slide-in-left'
      )}
    >
      <div
        className={cn(
          'max-w-[80%] px-4 py-3 hover-lift transition-shadow duration-200',
          isUser
            ? 'bg-primary text-primary-foreground rounded-2xl rounded-br-md hover:shadow-lg'
            : 'bg-card shadow-card rounded-2xl rounded-bl-md hover:shadow-card-hover'
        )}
      >
        <p className="whitespace-pre-wrap break-words">{message.content}</p>
        <time className={cn('mt-1 block text-xs opacity-70')}>{timestamp}</time>
      </div>
    </div>
  );
}
