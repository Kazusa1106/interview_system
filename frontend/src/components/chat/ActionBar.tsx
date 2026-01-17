import { Button } from '@/components/ui/button';

interface ActionBarProps {
  onUndo?: () => void;
  onSkip?: () => void;
  onRestart?: () => void;
  canUndo?: boolean;
  canSkip?: boolean;
}

export function ActionBar({
  onUndo,
  onSkip,
  onRestart,
  canUndo = false,
  canSkip = false,
}: ActionBarProps) {
  return (
    <div className="flex gap-2" role="toolbar" aria-label="访谈操作">
      {onUndo && (
        <Button
          variant="outline"
          size="sm"
          onClick={onUndo}
          disabled={!canUndo}
          aria-label="撤回上一条消息"
          title="撤回 (Ctrl+Z)"
        >
          撤回
        </Button>
      )}
      {onSkip && (
        <Button
          variant="outline"
          size="sm"
          onClick={onSkip}
          disabled={!canSkip}
          aria-label="跳过当前问题"
          title="跳过当前问题"
        >
          跳过
        </Button>
      )}
      {onRestart && (
        <Button
          variant="ghost"
          size="sm"
          onClick={onRestart}
          aria-label="重新开始访谈"
          title="重新开始 (Ctrl+R)"
        >
          重新开始
        </Button>
      )}
    </div>
  );
}
