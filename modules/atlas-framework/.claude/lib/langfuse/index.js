/**
 * ATLAS Framework - Langfuse Integration
 * LLM Observability for Claude Code sessions
 *
 * Usage:
 *   const langfuse = require('./langfuse');
 *   await langfuse.traceSession('start', { agent: 'ATLAS' });
 *   await langfuse.logUsage({ inputTokens: 1000, outputTokens: 500 });
 */

const https = require("https");
const http = require("http");
const fs = require("fs");
const path = require("path");

// Configuration from environment
const config = {
  enabled: process.env.LANGFUSE_ENABLED === "true",
  host: process.env.LANGFUSE_HOST || "http://localhost:3001",
  publicKey: process.env.LANGFUSE_PUBLIC_KEY || "",
  secretKey: process.env.LANGFUSE_SECRET_KEY || "",
};

/**
 * Send event to Langfuse API
 */
async function sendToLangfuse(payload) {
  if (!config.enabled || !config.publicKey || !config.secretKey) {
    return { success: false, reason: "Langfuse not configured" };
  }

  const url = new URL("/api/public/ingestion", config.host);
  const isHttps = url.protocol === "https:";
  const httpModule = isHttps ? https : http;

  const auth = Buffer.from(`${config.publicKey}:${config.secretKey}`).toString(
    "base64"
  );

  const options = {
    hostname: url.hostname,
    port: url.port || (isHttps ? 443 : 80),
    path: url.pathname,
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Basic ${auth}`,
    },
  };

  return new Promise((resolve) => {
    const req = httpModule.request(options, (res) => {
      let data = "";
      res.on("data", (chunk) => (data += chunk));
      res.on("end", () => {
        resolve({ success: res.statusCode === 200 || res.statusCode === 207 });
      });
    });

    req.on("error", (error) => {
      resolve({ success: false, error: error.message });
    });

    req.write(JSON.stringify(payload));
    req.end();
  });
}

/**
 * Generate unique trace ID
 */
function generateTraceId() {
  const timestamp = Date.now().toString(36);
  const random = Math.random().toString(36).substring(2, 8);
  return `atlas-${timestamp}-${random}`;
}

/**
 * Trace a session event (start, stop, checkpoint)
 */
async function traceSession(event, metadata = {}) {
  const traceId = metadata.sessionId || generateTraceId();

  const payload = {
    batch: [
      {
        type: "trace-create",
        body: {
          id: traceId,
          name: `atlas-${event}`,
          metadata: {
            event,
            agent: metadata.agent || process.env.ATLAS_CURRENT_AGENT || "ATLAS",
            project: metadata.project || path.basename(process.cwd()),
            timestamp: new Date().toISOString(),
            ...metadata,
          },
          tags: ["atlas", event, metadata.agent || "ATLAS"].filter(Boolean),
        },
      },
    ],
  };

  const result = await sendToLangfuse(payload);
  return { traceId, ...result };
}

/**
 * Log token usage for a session
 */
async function logUsage(traceId, usage) {
  const payload = {
    batch: [
      {
        type: "observation-create",
        body: {
          id: `obs-${Date.now()}`,
          traceId,
          type: "GENERATION",
          name: "claude-usage",
          model: usage.model || "claude-opus-4-5-20251101",
          usage: {
            input: usage.inputTokens || 0,
            output: usage.outputTokens || 0,
            total: (usage.inputTokens || 0) + (usage.outputTokens || 0),
          },
          metadata: {
            cacheRead: usage.cacheRead || 0,
            cacheWrite: usage.cacheWrite || 0,
            cost: usage.cost || 0,
          },
        },
      },
    ],
  };

  return sendToLangfuse(payload);
}

/**
 * Parse Claude Code JSONL transcript and extract usage
 */
function parseTranscript(transcriptPath) {
  if (!fs.existsSync(transcriptPath)) {
    return null;
  }

  const content = fs.readFileSync(transcriptPath, "utf-8");
  const lines = content.trim().split("\n");

  let totalInput = 0;
  let totalOutput = 0;
  let totalCacheRead = 0;
  let totalCacheWrite = 0;

  for (const line of lines) {
    try {
      const entry = JSON.parse(line);
      if (entry.usage) {
        totalInput += entry.usage.input_tokens || 0;
        totalOutput += entry.usage.output_tokens || 0;
        totalCacheRead += entry.usage.cache_read_input_tokens || 0;
        totalCacheWrite += entry.usage.cache_creation_input_tokens || 0;
      }
    } catch (e) {
      // Skip invalid lines
    }
  }

  return {
    inputTokens: totalInput,
    outputTokens: totalOutput,
    cacheRead: totalCacheRead,
    cacheWrite: totalCacheWrite,
    total: totalInput + totalOutput,
  };
}

/**
 * Sync a Claude transcript to Langfuse
 */
async function syncTranscript(transcriptPath, sessionId) {
  const usage = parseTranscript(transcriptPath);
  if (!usage) {
    return { success: false, reason: "Transcript not found" };
  }

  // Calculate cost (Opus 4.5 pricing)
  const cost =
    (usage.inputTokens * 5) / 1_000_000 + // $5/M input
    (usage.outputTokens * 25) / 1_000_000 + // $25/M output
    (usage.cacheRead * 0.5) / 1_000_000; // $0.50/M cache

  return logUsage(sessionId, { ...usage, cost, model: "claude-opus-4-5" });
}

// Export functions
module.exports = {
  config,
  traceSession,
  logUsage,
  parseTranscript,
  syncTranscript,
  generateTraceId,
};

// CLI usage
if (require.main === module) {
  const args = process.argv.slice(2);
  const command = args[0];

  if (command === "trace") {
    const event = args[1] || "start";
    traceSession(event)
      .then((result) => console.log(JSON.stringify(result)))
      .catch(console.error);
  } else if (command === "sync") {
    const transcriptPath = args[1];
    const sessionId = args[2] || generateTraceId();
    syncTranscript(transcriptPath, sessionId)
      .then((result) => console.log(JSON.stringify(result)))
      .catch(console.error);
  } else {
    console.log("ATLAS Langfuse Integration");
    console.log("");
    console.log("Usage:");
    console.log("  node index.js trace [event]       - Send trace event");
    console.log("  node index.js sync <path> [id]    - Sync transcript");
    console.log("");
    console.log("Environment:");
    console.log("  LANGFUSE_ENABLED=true");
    console.log("  LANGFUSE_HOST=http://localhost:3001");
    console.log("  LANGFUSE_PUBLIC_KEY=pk-...");
    console.log("  LANGFUSE_SECRET_KEY=sk-...");
  }
}
