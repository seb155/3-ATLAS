/**
 * @deprecated Use aiService.ts instead
 *
 * This file is kept for backward compatibility only.
 * All AI classification now goes through the backend API.
 */

export { classifyInstrument } from './aiService';

// Legacy warning
console.warn(
  'geminiService.ts is deprecated. Please import from aiService.ts instead.'
);
