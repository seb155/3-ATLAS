/**
 * ATLAS Framework - Multi-Provider Abstraction
 * Inspired by Lemmy's unified LLM interface
 *
 * Provides a unified interface for multiple LLM providers:
 * - Anthropic (Claude)
 * - OpenAI (GPT-4, o1)
 * - Google (Gemini)
 *
 * Usage:
 *   const providers = require('./providers');
 *   const claude = providers.anthropic({ model: 'opus' });
 *   const response = await claude.chat([{ role: 'user', content: 'Hello' }]);
 */

const https = require("https");
const http = require("http");
const fs = require("fs");
const path = require("path");

// ============================================================================
// Configuration
// ============================================================================

const CONFIG_PATH =
  process.env.ATLAS_PROVIDERS_CONFIG ||
  path.join(process.env.HOME, ".atlas", "providers.json");

const DEFAULT_CONFIG = {
  default: "anthropic",
  fallback: ["openai", "google"],
  providers: {
    anthropic: {
      baseUrl: "https://api.anthropic.com",
      models: {
        opus: "claude-opus-4-5-20251101",
        sonnet: "claude-sonnet-4-5-20250929",
        haiku: "claude-3-5-haiku-20241022",
      },
      defaultModel: "sonnet",
    },
    openai: {
      baseUrl: "https://api.openai.com/v1",
      models: {
        "gpt-4o": "gpt-4o",
        "gpt-4-turbo": "gpt-4-turbo",
        o1: "o1-preview",
        "o1-mini": "o1-mini",
      },
      defaultModel: "gpt-4o",
    },
    google: {
      baseUrl: "https://generativelanguage.googleapis.com/v1beta",
      models: {
        "gemini-pro": "gemini-1.5-pro-latest",
        "gemini-flash": "gemini-1.5-flash-latest",
      },
      defaultModel: "gemini-pro",
    },
  },
};

/**
 * Load configuration from file or use defaults
 */
function loadConfig() {
  try {
    if (fs.existsSync(CONFIG_PATH)) {
      const userConfig = JSON.parse(fs.readFileSync(CONFIG_PATH, "utf-8"));
      return { ...DEFAULT_CONFIG, ...userConfig };
    }
  } catch (e) {
    console.warn("Failed to load providers config, using defaults");
  }
  return DEFAULT_CONFIG;
}

const config = loadConfig();

// ============================================================================
// Provider Interface
// ============================================================================

/**
 * Base provider class with unified interface
 */
class BaseProvider {
  constructor(providerName, options = {}) {
    this.providerName = providerName;
    this.providerConfig = config.providers[providerName];
    this.model =
      options.model || this.providerConfig?.defaultModel || "default";
    this.apiKey = options.apiKey || this.getApiKey();
    this.baseUrl = options.baseUrl || this.providerConfig?.baseUrl;
  }

  getApiKey() {
    const envVars = {
      anthropic: "ANTHROPIC_API_KEY",
      openai: "OPENAI_API_KEY",
      google: "GOOGLE_API_KEY",
    };
    return process.env[envVars[this.providerName]];
  }

  getModelId() {
    const models = this.providerConfig?.models || {};
    return models[this.model] || this.model;
  }

  /**
   * Chat completion - must be implemented by subclasses
   */
  async chat(messages, options = {}) {
    throw new Error("chat() must be implemented by provider");
  }

  /**
   * Stream chat completion
   */
  async *streamChat(messages, options = {}) {
    throw new Error("streamChat() must be implemented by provider");
  }
}

// ============================================================================
// Anthropic Provider
// ============================================================================

class AnthropicProvider extends BaseProvider {
  constructor(options = {}) {
    super("anthropic", options);
  }

  async chat(messages, options = {}) {
    const systemMessage = messages.find((m) => m.role === "system");
    const userMessages = messages.filter((m) => m.role !== "system");

    const body = {
      model: this.getModelId(),
      max_tokens: options.maxTokens || 4096,
      messages: userMessages.map((m) => ({
        role: m.role,
        content: m.content,
      })),
    };

    if (systemMessage) {
      body.system = systemMessage.content;
    }

    const response = await this.request("/v1/messages", body);
    return {
      content: response.content?.[0]?.text || "",
      usage: {
        inputTokens: response.usage?.input_tokens || 0,
        outputTokens: response.usage?.output_tokens || 0,
      },
      model: response.model,
      provider: "anthropic",
    };
  }

  async request(endpoint, body) {
    return new Promise((resolve, reject) => {
      const url = new URL(endpoint, this.baseUrl);

      const req = https.request(
        {
          hostname: url.hostname,
          path: url.pathname,
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            "x-api-key": this.apiKey,
            "anthropic-version": "2023-06-01",
          },
        },
        (res) => {
          let data = "";
          res.on("data", (chunk) => (data += chunk));
          res.on("end", () => {
            try {
              resolve(JSON.parse(data));
            } catch (e) {
              reject(new Error(`Invalid response: ${data}`));
            }
          });
        }
      );

      req.on("error", reject);
      req.write(JSON.stringify(body));
      req.end();
    });
  }
}

// ============================================================================
// OpenAI Provider
// ============================================================================

class OpenAIProvider extends BaseProvider {
  constructor(options = {}) {
    super("openai", options);
  }

  async chat(messages, options = {}) {
    const body = {
      model: this.getModelId(),
      max_tokens: options.maxTokens || 4096,
      messages: messages.map((m) => ({
        role: m.role,
        content: m.content,
      })),
    };

    const response = await this.request("/chat/completions", body);
    return {
      content: response.choices?.[0]?.message?.content || "",
      usage: {
        inputTokens: response.usage?.prompt_tokens || 0,
        outputTokens: response.usage?.completion_tokens || 0,
      },
      model: response.model,
      provider: "openai",
    };
  }

  async request(endpoint, body) {
    return new Promise((resolve, reject) => {
      const url = new URL(endpoint, this.baseUrl);

      const req = https.request(
        {
          hostname: url.hostname,
          path: url.pathname,
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${this.apiKey}`,
          },
        },
        (res) => {
          let data = "";
          res.on("data", (chunk) => (data += chunk));
          res.on("end", () => {
            try {
              resolve(JSON.parse(data));
            } catch (e) {
              reject(new Error(`Invalid response: ${data}`));
            }
          });
        }
      );

      req.on("error", reject);
      req.write(JSON.stringify(body));
      req.end();
    });
  }
}

// ============================================================================
// Google Provider
// ============================================================================

class GoogleProvider extends BaseProvider {
  constructor(options = {}) {
    super("google", options);
  }

  async chat(messages, options = {}) {
    // Convert messages to Gemini format
    const contents = messages
      .filter((m) => m.role !== "system")
      .map((m) => ({
        role: m.role === "assistant" ? "model" : "user",
        parts: [{ text: m.content }],
      }));

    const systemInstruction = messages.find((m) => m.role === "system");

    const body = {
      contents,
      generationConfig: {
        maxOutputTokens: options.maxTokens || 4096,
      },
    };

    if (systemInstruction) {
      body.systemInstruction = { parts: [{ text: systemInstruction.content }] };
    }

    const model = this.getModelId();
    const response = await this.request(
      `/models/${model}:generateContent`,
      body
    );

    return {
      content:
        response.candidates?.[0]?.content?.parts?.[0]?.text ||
        "",
      usage: {
        inputTokens: response.usageMetadata?.promptTokenCount || 0,
        outputTokens: response.usageMetadata?.candidatesTokenCount || 0,
      },
      model: model,
      provider: "google",
    };
  }

  async request(endpoint, body) {
    return new Promise((resolve, reject) => {
      const url = new URL(endpoint, this.baseUrl);
      url.searchParams.set("key", this.apiKey);

      const req = https.request(
        {
          hostname: url.hostname,
          path: url.pathname + url.search,
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
        },
        (res) => {
          let data = "";
          res.on("data", (chunk) => (data += chunk));
          res.on("end", () => {
            try {
              resolve(JSON.parse(data));
            } catch (e) {
              reject(new Error(`Invalid response: ${data}`));
            }
          });
        }
      );

      req.on("error", reject);
      req.write(JSON.stringify(body));
      req.end();
    });
  }
}

// ============================================================================
// Factory Functions (Lemmy-style)
// ============================================================================

/**
 * Create Anthropic provider
 */
function anthropic(options = {}) {
  return new AnthropicProvider(options);
}

/**
 * Create OpenAI provider
 */
function openai(options = {}) {
  return new OpenAIProvider(options);
}

/**
 * Create Google provider
 */
function google(options = {}) {
  return new GoogleProvider(options);
}

/**
 * Create provider by name
 */
function create(providerName, options = {}) {
  const factories = { anthropic, openai, google };
  const factory = factories[providerName];
  if (!factory) {
    throw new Error(`Unknown provider: ${providerName}`);
  }
  return factory(options);
}

/**
 * Get default provider
 */
function getDefault(options = {}) {
  return create(config.default, options);
}

// ============================================================================
// Fallback Chain
// ============================================================================

/**
 * Create a provider chain that tries fallback providers on failure
 */
class ProviderChain {
  constructor(options = {}) {
    this.providers = [config.default, ...(config.fallback || [])].map((name) =>
      create(name, options)
    );
    this.currentIndex = 0;
  }

  async chat(messages, options = {}) {
    let lastError;

    for (const provider of this.providers) {
      try {
        const response = await provider.chat(messages, options);
        this.currentIndex = this.providers.indexOf(provider);
        return response;
      } catch (error) {
        lastError = error;
        console.warn(
          `Provider ${provider.providerName} failed, trying next...`
        );
      }
    }

    throw new Error(`All providers failed. Last error: ${lastError?.message}`);
  }

  get currentProvider() {
    return this.providers[this.currentIndex];
  }
}

/**
 * Create provider chain with fallback
 */
function withFallback(options = {}) {
  return new ProviderChain(options);
}

// ============================================================================
// Exports
// ============================================================================

module.exports = {
  // Factory functions (Lemmy-style)
  anthropic,
  openai,
  google,
  create,
  getDefault,
  withFallback,

  // Classes (for advanced usage)
  BaseProvider,
  AnthropicProvider,
  OpenAIProvider,
  GoogleProvider,
  ProviderChain,

  // Config
  config,
  loadConfig,
  CONFIG_PATH,
};

// ============================================================================
// CLI
// ============================================================================

if (require.main === module) {
  const args = process.argv.slice(2);
  const command = args[0];

  if (command === "test") {
    const providerName = args[1] || "anthropic";
    const provider = create(providerName);

    console.log(`Testing ${providerName} provider...`);
    provider
      .chat([{ role: "user", content: "Say hello in one word." }])
      .then((response) => {
        console.log("Response:", response.content);
        console.log("Usage:", response.usage);
      })
      .catch(console.error);
  } else if (command === "config") {
    console.log(JSON.stringify(config, null, 2));
  } else {
    console.log("ATLAS Multi-Provider Abstraction");
    console.log("");
    console.log("Usage:");
    console.log("  node index.js test [provider]    - Test a provider");
    console.log("  node index.js config             - Show configuration");
    console.log("");
    console.log("Providers: anthropic, openai, google");
    console.log("");
    console.log("Environment:");
    console.log("  ANTHROPIC_API_KEY=sk-ant-...");
    console.log("  OPENAI_API_KEY=sk-...");
    console.log("  GOOGLE_API_KEY=...");
  }
}
