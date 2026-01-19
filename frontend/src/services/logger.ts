export type LogFields = Record<string, unknown>;

function formatError(error: unknown): unknown {
  if (error instanceof Error) {
    return { name: error.name, message: error.message, stack: error.stack };
  }
  return error;
}

const enabled = import.meta.env.DEV;

export function logError(scope: string, message: string, error?: unknown, fields?: LogFields): void {
  if (!enabled) return;
  console.error({
    level: 'error',
    scope,
    message,
    ...(fields || {}),
    error: error === undefined ? undefined : formatError(error),
  });
}

