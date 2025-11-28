import { useLogStore, type LogLevel } from '../store/useLogStore';
import { toast } from 'sonner';

class Logger {
  private isDevelopment = import.meta.env.DEV;

  private log(level: LogLevel, message: string, context?: Record<string, unknown>, stack?: string) {
    // Add to log store
    useLogStore.getState().addLog({
      level,
      source: 'FRONTEND',
      message,
      context,
      stack,
    });

    // Also log to browser console
    const logMessage = context
      ? `[${level}] ${message}`
      : `[${level}] ${message}`;

    switch (level) {
      case 'DEBUG':
        if (this.isDevelopment) {
          console.debug(logMessage, context || '');
        }
        break;
      case 'INFO':
        console.info(logMessage, context || '');
        break;
      case 'WARN':
        console.warn(logMessage, context || '');
        break;
      case 'ERROR':
        console.error(logMessage, context || '', stack || '');
        break;
    }
  }

  debug(message: string, context?: Record<string, unknown>) {
    this.log('DEBUG', message, context);
  }

  info(message: string, context?: Record<string, unknown>) {
    this.log('INFO', message, context);
  }

  warn(message: string, context?: Record<string, unknown>) {
    this.log('WARN', message, context);
    // Show warning toast for user
    toast.warning(message);
  }

  error(message: string, errorOrContext?: Error | Record<string, unknown>) {
    let context: Record<string, unknown> | undefined;
    let stack: string | undefined;

    if (errorOrContext instanceof Error) {
      stack = errorOrContext.stack;
      context = {
        name: errorOrContext.name,
        message: errorOrContext.message,
      };
    } else {
      context = errorOrContext;
    }

    this.log('ERROR', message, context, stack);
    // Show error toast for user
    toast.error(message);
  }

  success(message: string) {
    this.log('INFO', message, { type: 'success' });
    toast.success(message);
  }
}

export const logger = new Logger();
