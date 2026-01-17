import { useState, useRef, useEffect, type KeyboardEvent } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { cn } from '@/lib/utils';

interface MessageInputProps {
  onSend: (text: string) => void;
  disabled?: boolean;
  placeholder?: string;
  autoFocus?: boolean;
}

export function MessageInput({
  onSend,
  disabled = false,
  placeholder = '输入消息...',
  autoFocus = true,
}: MessageInputProps) {
  const [text, setText] = useState('');
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (autoFocus && inputRef.current) {
      inputRef.current.focus();
    }
  }, [autoFocus]);

  const handleSend = () => {
    if (!text.trim() || disabled) return;
    onSend(text.trim());
    setText('');
    inputRef.current?.focus();
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="flex gap-2" role="search" aria-label="消息输入">
      <Input
        ref={inputRef}
        value={text}
        onChange={(e) => setText(e.target.value)}
        onKeyDown={handleKeyDown}
        placeholder={placeholder}
        disabled={disabled}
        className={cn('min-h-[48px] rounded-xl border border-border')}
        aria-label="输入您的回答"
        aria-describedby="input-hint"
      />
      <span id="input-hint" className="sr-only">
        按 Enter 键发送消息
      </span>
      <Button
        onClick={handleSend}
        disabled={disabled || !text.trim()}
        size="sm"
        aria-label="发送消息"
      >
        发送
      </Button>
    </div>
  );
}
