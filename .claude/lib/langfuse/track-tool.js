#!/usr/bin/env node
/**
 * ATLAS Framework - Langfuse Tool Tracker
 * Tracks tool usage events for LLM observability
 *
 * Usage:
 *   node track-tool.js pre <tool_name>   - Before tool execution
 *   node track-tool.js post <tool_name>  - After tool execution
 */

const fs = require("fs");
const path = require("path");
const https = require("https");
const http = require("http");

// Auto-load env file
function loadEnvFile() {
  const envPath = path.join(process.env.HOME || "", ".atlas", "langfuse.env");
  if (fs.existsSync(envPath) && !process.env.LANGFUSE_PUBLIC_KEY) {
    try {
      const content = fs.readFileSync(envPath, "utf-8");
      content.split("\n").forEach((line) => {
        const match = line.match(/^export\s+(\w+)=(.*)$/);
        if (match) {
          process.env[match[1]] = match[2].replace(/^["']|["']$/g, "");
        }
      });
    } catch (e) {}
  }
}

loadEnvFile();

const config = {
  enabled: process.env.LANGFUSE_ENABLED === "true",
  host: process.env.LANGFUSE_HOST || "http://localhost:3001",
  publicKey: process.env.LANGFUSE_PUBLIC_KEY || "",
  secretKey: process.env.LANGFUSE_SECRET_KEY || "",
};

// Skip if not configured
if (!config.enabled || !config.publicKey || !config.secretKey) {
  process.exit(0);
}

// Get arguments
const [,, phase, toolName] = process.argv;
if (!phase || !toolName) {
  process.exit(0);
}

// Generate IDs
const timestamp = new Date().toISOString();
const batchId = `batch-${Date.now()}-${Math.random().toString(36).substring(2, 6)}`;
const traceId = `tool-${Date.now()}-${Math.random().toString(36).substring(2, 6)}`;

// Build payload
const payload = {
  batch: [{
    id: batchId,
    timestamp: timestamp,
    type: "trace-create",
    body: {
      id: traceId,
      name: `atlas-tool-${phase}`,
      timestamp: timestamp,
      metadata: {
        phase: phase,
        tool: toolName,
        project: path.basename(process.cwd()),
        agent: process.env.ATLAS_CURRENT_AGENT || "ATLAS",
      },
      tags: ["atlas", "tool", toolName, phase],
    },
  }],
};

// Send to Langfuse (non-blocking)
const url = new URL("/api/public/ingestion", config.host);
const isHttps = url.protocol === "https:";
const httpModule = isHttps ? https : http;
const auth = Buffer.from(`${config.publicKey}:${config.secretKey}`).toString("base64");

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

const req = httpModule.request(options, (res) => {
  // Drain response and exit
  res.on("data", () => {});
  res.on("end", () => process.exit(0));
});

req.on("error", () => process.exit(0));
req.write(JSON.stringify(payload));
req.end();

// Timeout fallback (max 2 seconds)
setTimeout(() => process.exit(0), 2000);
