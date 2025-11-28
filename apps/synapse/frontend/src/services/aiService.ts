/**
 * AI Service - Frontend client for backend AI classification
 *
 * Supports multiple AI providers via backend configuration:
 * - Ollama (free, local)
 * - OpenAI (paid)
 * - Google Gemini (paid, free tier available)
 *
 * All AI calls go through the backend to:
 * 1. Keep API keys secure (not exposed to browser)
 * 2. Allow runtime provider switching
 * 3. Provide consistent interface regardless of provider
 */

import { apiClient } from './apiClient';
import { Asset, IOType } from '../types';

export interface AIClassificationResult {
  system: string;
  io_type: string;
  suggested_area: string | null;
  confidence: number;
  provider: string;
  error: string | null;
}

export interface AIProviderInfo {
  name: string;
  status: 'active' | 'configured' | 'available';
  model: string | null;
  requires_api_key: boolean;
  description: string;
}

export interface AIHealthStatus {
  status: string;
  provider: string;
  model?: string;
  base_url?: string;
  available_models?: string[];
  error?: string;
}

export interface AIConfig {
  provider: string;
  model: string;
  ollama_url: string;
  openai_configured: boolean;
  gemini_configured: boolean;
}

/**
 * Classify an instrument using the backend AI service
 */
export const classifyInstrument = async (
  tag: string,
  description: string
): Promise<Partial<Asset>> => {
  try {
    const response = await apiClient.post<AIClassificationResult>('/ai/classify', {
      tag,
      description
    });

    const result = response.data;

    if (result.error) {
      console.warn('AI classification warning:', result.error);
      // Return fallback values
      return {
        system: 'Manual',
        ioType: IOType.AI
      };
    }

    return {
      system: result.system,
      ioType: result.io_type as IOType,
      area: result.suggested_area || '000'
    };
  } catch (error) {
    console.error('AI classification failed:', error);
    // Fallback to manual classification
    return {
      system: 'Manual',
      ioType: IOType.AI
    };
  }
};

/**
 * Check the health of the AI service
 */
export const checkAIHealth = async (): Promise<AIHealthStatus> => {
  try {
    const response = await apiClient.get<AIHealthStatus>('/ai/health');
    return response.data;
  } catch (error) {
    console.error('AI health check failed:', error);
    return {
      status: 'unreachable',
      provider: 'unknown',
      error: 'Could not reach AI service'
    };
  }
};

/**
 * Get list of available AI providers
 */
export const getAIProviders = async (): Promise<AIProviderInfo[]> => {
  try {
    const response = await apiClient.get<AIProviderInfo[]>('/ai/providers');
    return response.data;
  } catch (error) {
    console.error('Failed to fetch AI providers:', error);
    return [];
  }
};

/**
 * Get current AI configuration
 */
export const getAIConfig = async (): Promise<AIConfig | null> => {
  try {
    const response = await apiClient.get<AIConfig>('/ai/config');
    return response.data;
  } catch (error) {
    console.error('Failed to fetch AI config:', error);
    return null;
  }
};

/**
 * Switch AI provider (requires appropriate permissions)
 */
export const switchAIProvider = async (
  provider: 'ollama' | 'openai' | 'gemini' | 'none',
  model?: string,
  apiKey?: string
): Promise<{ message: string; health: AIHealthStatus }> => {
  const response = await apiClient.post('/ai/switch', {
    provider,
    model,
    api_key: apiKey
  });
  return response.data;
};

// Re-export for backward compatibility with geminiService
export { classifyInstrument as classifyWithAI };
