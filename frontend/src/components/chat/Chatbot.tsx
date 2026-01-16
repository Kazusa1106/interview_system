import { useEffect, useRef } from 'react';
import type { Message } from '@/types';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Button } from '@/components/ui/button';
import { MessageBubble } from './MessageBubble';
import { MessageInput } from './MessageInput';
import { ActionBar } from './ActionBar';
import { MessageSkeleton } from './MessageSkeleton';

interface ChatbotProps {
  messages: Message[];
  onSend: (text: string) => void;
  onUndo?: () => void;
  onSkip?: () => void;
  onRestart?: () => void;
  onStartInterview?: () => void;
  canUndo?: boolean;
  canSkip?: boolean;
  isLoading?: boolean;
}

export function Chatbot({
  messages,
  onSend,
  onUndo,
  onSkip,
  onRestart,
  onStartInterview,
  canUndo = false,
  canSkip = false,
  isLoading = false,
}: ChatbotProps) {
  const scrollRef = useRef<HTMLDivElement>(null);
  const isEmpty = messages.length === 0 && !isLoading;

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages]);

  return (
    <div className="flex h-full flex-col gap-4">
      <ScrollArea className="flex-1" ref={scrollRef}>
        <div className="flex flex-col gap-4 p-4">
          {isEmpty ? (
            <div className="flex h-full min-h-[400px] flex-col items-center justify-center gap-6 text-center">
              <div className="space-y-2">
                <h2 className="text-2xl font-semibold">欢迎使用 AI 教育访谈系统</h2>
                <p className="text-muted-foreground">
                  点击下方按钮开始访谈，系统将引导你完成学习评估
                </p>
              </div>
              <Button size="lg" onClick={onStartInterview}>
                快速访谈
              </Button>
            </div>
          ) : (
            <>
              {messages.map((msg) => (
                <MessageBubble key={msg.id} message={msg} />
              ))}
              {isLoading && <MessageSkeleton count={1} />}
            </>
          )}
        </div>
      </ScrollArea>

      <div className="flex flex-col gap-2 border-t border-border p-4">
        <ActionBar
          onUndo={onUndo}
          onSkip={onSkip}
          onRestart={onRestart}
          canUndo={canUndo}
          canSkip={canSkip}
        />
        <MessageInput onSend={onSend} disabled={isLoading} />
      </div>
    </div>
  );
}
