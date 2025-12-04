#!/usr/bin/env node
/**
 * ATLAS Framework - StatusLine (Node.js)
 * Modern, performant status line with differential rendering
 *
 * Features:
 *   - Parse Claude Code JSON input
 *   - Real token counts from JSONL transcripts
 *   - Responsive modes (Ultra/Compact/Standard/Full)
 *   - Differential rendering (only update changed parts)
 *   - Project detection with monorepo support
 *   - Agent tracking
 *
 * Usage:
 *   echo '{"model":...}' | node statusline.js
 *   node statusline.js --test
 */

const fs = require("fs");
const path = require("path");
const { execSync } = require("child_process");

// ============================================================================
// Configuration
// ============================================================================

const CONFIG = {
  // Token pricing (Opus 4.5)
  pricing: {
    input: 5.0 / 1_000_000, // $5/M
    output: 25.0 / 1_000_000, // $25/M
    cacheWrite: 6.25 / 1_000_000, // $6.25/M
    cacheRead: 0.5 / 1_000_000, // $0.50/M
  },

  // Context limit (200K for Claude)
  contextLimit: 200_000,

  // Project emojis
  projects: {
    axiom: { emoji: "🏗️", name: "AXIOM" },
    synapse: { emoji: "⚡", name: "SYNAPSE" },
    nexus: { emoji: "🧠", name: "NEXUS" },
    cortex: { emoji: "🔮", name: "CORTEX" },
    atlas: { emoji: "🏛️", name: "ATLAS" },
    forge: { emoji: "🔥", name: "FORGE" },
    prism: { emoji: "💎", name: "PRISM" },
    perso: { emoji: "👤", name: "PERSO" },
    homelab: { emoji: "🖥️", name: "HOMELAB" },
    findash: { emoji: "💰", name: "FINDASH" },
    mechvision: { emoji: "🤖", name: "MECHVISION" },
  },

  // Model emojis
  models: {
    opus: "🧠 Opus",
    sonnet: "🎵 Sonnet",
    haiku: "🍃 Haiku",
    default: "🤖 Claude",
  },

  // Agent emojis
  agents: {
    ATLAS: "🥇 ATLAS",
    GENESIS: "🧬 GENESIS",
    BRAINSTORM: "💡 BRAIN",
    "SYSTEM-ARCHITECT": "🏛️ ARCH",
    "BACKEND-BUILDER": "🔧 BACKEND",
    "FRONTEND-BUILDER": "🎨 FRONTEND",
    "DEVOPS-BUILDER": "🐳 DEVOPS",
    "DEVOPS-MANAGER": "🚀 DEVOPS-MGR",
    DEBUGGER: "🐛 DEBUG",
    PLANNER: "📋 PLANNER",
    "DOC-WRITER": "📝 DOCS",
    "UX-DESIGNER": "🎯 UX",
    "OPUS-DIRECT": "⭐ OPUS",
    "SONNET-DIRECT": "🔵 SONNET",
    EXPLORE: "🔍 EXPLORE",
    PLAN: "📐 PLAN",
  },

  // Responsive breakpoints
  breakpoints: {
    ultraCompact: 60,
    compact: 90,
    standard: 120,
  },
};

// ============================================================================
// Utilities
// ============================================================================

/**
 * Format tokens with K/M suffix
 */
function formatTokens(tokens) {
  if (tokens >= 1_000_000) {
    return `${(tokens / 1_000_000).toFixed(1)}M`;
  }
  if (tokens >= 1_000) {
    return `${Math.round(tokens / 1_000)}K`;
  }
  return String(tokens);
}

/**
 * Format cost with appropriate precision
 */
function formatCost(cost) {
  if (cost < 0.01) return cost.toFixed(3);
  if (cost < 0.1) return cost.toFixed(2);
  if (cost === Math.floor(cost)) return cost.toFixed(0);
  return cost.toFixed(1);
}

/**
 * Get context indicator with color emoji
 */
function getContextIndicator(pct) {
  if (pct >= 85) return `🔴 ${pct}%`;
  if (pct >= 70) return `🟠 ${pct}%`;
  if (pct >= 50) return `🟡 ${pct}%`;
  return `🟢 ${pct}%`;
}

// ============================================================================
// Data Collectors
// ============================================================================

/**
 * Parse input JSON from Claude Code
 */
function parseClaudeInput() {
  let input = "";
  try {
    // Read from stdin (non-blocking)
    if (!process.stdin.isTTY) {
      input = fs.readFileSync(0, "utf-8");
    }
  } catch (e) {
    // No stdin available
  }

  if (!input) {
    return { model: "claude", cost: 0, duration: 0 };
  }

  try {
    const json = JSON.parse(input);
    return {
      model: json.model?.display_name || "claude",
      cost: json.cost?.total_cost_usd || 0,
      duration: json.cost?.total_duration_ms || 0,
    };
  } catch (e) {
    return { model: "claude", cost: 0, duration: 0 };
  }
}

/**
 * Detect model display name
 */
function getModelDisplay(modelName) {
  const upper = modelName.toUpperCase();
  if (upper.includes("OPUS")) return CONFIG.models.opus;
  if (upper.includes("SONNET")) return CONFIG.models.sonnet;
  if (upper.includes("HAIKU")) return CONFIG.models.haiku;
  return CONFIG.models.default;
}

/**
 * Detect project from current directory
 */
function getProjectDisplay() {
  const cwd = process.cwd();
  const cwdLower = cwd.toLowerCase();
  const currentDir = path.basename(cwd);

  // Find matching project
  let project = { emoji: "📁", name: currentDir.toUpperCase() };

  for (const [key, value] of Object.entries(CONFIG.projects)) {
    if (cwdLower.includes(key)) {
      project = value;
      break;
    }
  }

  // Add subdirectory for monorepo
  const currentDirUpper = currentDir.toUpperCase();
  if (project.name !== currentDirUpper) {
    return `${project.emoji} ${project.name}/${currentDir}`;
  }
  return `${project.emoji} ${project.name}`;
}

/**
 * Get Git branch and status
 */
function getGitDisplay() {
  try {
    const branch = execSync("git branch --show-current 2>/dev/null", {
      encoding: "utf-8",
    }).trim();

    if (!branch) return "";

    const changes = execSync("git status --porcelain 2>/dev/null", {
      encoding: "utf-8",
    })
      .trim()
      .split("\n")
      .filter((l) => l).length;

    if (changes > 0) {
      return `🌿 ${branch}*${changes}`;
    }
    return `🌿 ${branch}`;
  } catch (e) {
    return "";
  }
}

/**
 * Get current agent from session state
 */
function getAgentDisplay() {
  const stateFile = path.join(
    process.env.HOME || "",
    ".claude",
    "session-state.json"
  );

  try {
    if (fs.existsSync(stateFile)) {
      const state = JSON.parse(fs.readFileSync(stateFile, "utf-8"));
      const agent = state.current_agent || "ATLAS";
      return CONFIG.agents[agent] || `🤖 ${agent}`;
    }
  } catch (e) {
    // Ignore errors
  }

  return CONFIG.agents.ATLAS;
}

/**
 * Parse real tokens from JSONL transcript
 */
function parseTokens() {
  const cwd = process.cwd();
  const projectPath = cwd.replace(/\//g, "-").replace(/^-/, "");
  const transcriptDir = path.join(
    process.env.HOME || "",
    ".claude",
    "projects",
    `-${projectPath}`
  );

  // Find most recent JSONL
  let currentJsonl = null;
  try {
    const files = fs.readdirSync(transcriptDir).filter((f) => f.endsWith(".jsonl"));
    if (files.length > 0) {
      // Sort by mtime
      const sorted = files
        .map((f) => ({
          name: f,
          mtime: fs.statSync(path.join(transcriptDir, f)).mtime,
        }))
        .sort((a, b) => b.mtime - a.mtime);
      currentJsonl = path.join(transcriptDir, sorted[0].name);
    }
  } catch (e) {
    // No transcript
  }

  if (!currentJsonl || !fs.existsSync(currentJsonl)) {
    return {
      input: 0,
      output: 0,
      cacheWrite: 0,
      cacheRead: 0,
      total: 0,
      cost: 0,
      contextPct: 0,
    };
  }

  // Parse JSONL
  const content = fs.readFileSync(currentJsonl, "utf-8");
  const lines = content.trim().split("\n");

  let input = 0,
    output = 0,
    cacheWrite = 0,
    cacheRead = 0;

  for (const line of lines) {
    try {
      const entry = JSON.parse(line);
      if (entry.type === "assistant" && entry.message?.usage) {
        const usage = entry.message.usage;
        input += usage.input_tokens || 0;
        output += usage.output_tokens || 0;
        cacheWrite += usage.cache_creation_input_tokens || 0;
        cacheRead += usage.cache_read_input_tokens || 0;
      }
    } catch (e) {
      // Skip invalid lines
    }
  }

  const total = input + output + cacheWrite + cacheRead;
  const cost =
    input * CONFIG.pricing.input +
    output * CONFIG.pricing.output +
    cacheWrite * CONFIG.pricing.cacheWrite +
    cacheRead * CONFIG.pricing.cacheRead;

  const contextEstimate = cacheRead + input;
  const contextPct = Math.min(
    100,
    Math.round((contextEstimate / CONFIG.contextLimit) * 100)
  );

  return {
    input,
    output,
    cacheWrite,
    cacheRead,
    total,
    cost,
    contextPct,
  };
}

// ============================================================================
// Status Line Builder
// ============================================================================

/**
 * Build status line based on terminal width
 */
function buildStatusLine(width = 150) {
  const claudeInput = parseClaudeInput();
  const modelDisplay = getModelDisplay(claudeInput.model);
  const projectDisplay = getProjectDisplay();
  const gitDisplay = getGitDisplay();
  const agentDisplay = getAgentDisplay();
  const tokens = parseTokens();

  // Use calculated cost if available, otherwise API cost
  const cost = tokens.cost > 0 ? tokens.cost : claudeInput.cost;
  const costDisplay = formatCost(cost);
  const contextDisplay = getContextIndicator(tokens.contextPct);

  // Format duration
  let durationStr = "";
  if (claudeInput.duration > 0) {
    const totalSeconds = Math.floor(claudeInput.duration / 1000);
    const hours = Math.floor(totalSeconds / 3600);
    const minutes = Math.floor((totalSeconds % 3600) / 60);
    durationStr = `⏱️ ${hours}:${String(minutes).padStart(2, "0")}`;
  }

  // Build based on width
  const parts = [];

  if (width < CONFIG.breakpoints.ultraCompact) {
    // ULTRA COMPACT
    parts.push(`💰 $${costDisplay}`);
    parts.push(contextDisplay);
  } else if (width < CONFIG.breakpoints.compact) {
    // COMPACT
    parts.push("🏛️ ATLAS");
    parts.push(modelDisplay);
    parts.push(`💰 $${costDisplay}`);
    parts.push(contextDisplay);
  } else if (width < CONFIG.breakpoints.standard) {
    // STANDARD
    parts.push("🏛️ ATLAS");
    parts.push(modelDisplay);
    parts.push(projectDisplay);
    if (gitDisplay) parts.push(gitDisplay);
    parts.push(`📝 ${formatTokens(tokens.total)}`);
    parts.push(`💰 $${costDisplay}`);
    parts.push(contextDisplay);
  } else {
    // FULL
    parts.push("🏛️ ATLAS");
    parts.push(modelDisplay);
    parts.push(projectDisplay);
    if (gitDisplay) parts.push(gitDisplay);
    parts.push(agentDisplay);

    if (tokens.total > 0) {
      parts.push(`📥 ${formatTokens(tokens.input)}`);
      parts.push(`📤 ${formatTokens(tokens.output)}`);
      parts.push(`💾 ${formatTokens(tokens.cacheWrite + tokens.cacheRead)}`);
    }

    parts.push(`💰 $${costDisplay}`);
    parts.push(contextDisplay);

    if (durationStr) parts.push(durationStr);
  }

  return parts.join(" │ ");
}

// ============================================================================
// Main
// ============================================================================

function main() {
  const args = process.argv.slice(2);

  if (args.includes("--help") || args.includes("-h")) {
    console.log("ATLAS StatusLine (Node.js)");
    console.log("");
    console.log("Usage:");
    console.log('  echo \'{"model":...}\' | node statusline.js');
    console.log("  node statusline.js --test");
    console.log("  node statusline.js --width 120");
    console.log("");
    console.log("Options:");
    console.log("  --test     Show test output");
    console.log("  --width N  Force terminal width");
    process.exit(0);
  }

  // Get terminal width
  let width = parseInt(process.env.ATLAS_TERM_WIDTH) || 150;
  const widthIndex = args.indexOf("--width");
  if (widthIndex !== -1 && args[widthIndex + 1]) {
    width = parseInt(args[widthIndex + 1]);
  } else if (process.stdout.columns) {
    width = process.stdout.columns;
  }

  // Build and output
  const statusLine = buildStatusLine(width);
  process.stdout.write(statusLine);
}

// Run if called directly
if (require.main === module) {
  main();
}

// Export for testing
module.exports = {
  buildStatusLine,
  parseTokens,
  formatTokens,
  formatCost,
  CONFIG,
};
