/**
 * ATLAS Framework - Context Serialization
 * Inspired by Lemmy's Context.serialize() / Context.deserialize()
 *
 * Saves and restores session context for:
 *   - Recovery after /compact
 *   - Session persistence across restarts
 *   - Sharing context between sessions
 *
 * Usage:
 *   const context = require('./context');
 *   await context.save({ note: 'Feature complete' });
 *   const restored = await context.restore();
 */

const fs = require("fs");
const path = require("path");
const { execSync } = require("child_process");

// ============================================================================
// Configuration
// ============================================================================

const CONFIG = {
  // Context storage location
  contextDir:
    process.env.ATLAS_CONTEXT_DIR ||
    path.join(process.env.HOME || "", ".atlas", "context"),

  // Max checkpoints to keep
  maxCheckpoints: 10,

  // Schema version
  version: 1,
};

// ============================================================================
// Utilities
// ============================================================================

/**
 * Ensure directory exists
 */
function ensureDir(dir) {
  if (!fs.existsSync(dir)) {
    fs.mkdirSync(dir, { recursive: true });
  }
}

/**
 * Get current git info
 */
function getGitInfo() {
  try {
    const branch = execSync("git branch --show-current 2>/dev/null", {
      encoding: "utf-8",
    }).trim();
    const commit = execSync("git rev-parse --short HEAD 2>/dev/null", {
      encoding: "utf-8",
    }).trim();
    const changes = execSync("git status --porcelain 2>/dev/null", {
      encoding: "utf-8",
    })
      .trim()
      .split("\n")
      .filter((l) => l).length;

    return { branch, commit, changes };
  } catch (e) {
    return null;
  }
}

/**
 * Get session info from state file
 */
function getSessionInfo() {
  const stateFile = path.join(
    process.env.HOME || "",
    ".claude",
    "session-state.json"
  );

  try {
    if (fs.existsSync(stateFile)) {
      return JSON.parse(fs.readFileSync(stateFile, "utf-8"));
    }
  } catch (e) {
    // Ignore
  }

  return { current_agent: "ATLAS", agent_stack: ["ATLAS"] };
}

/**
 * Get token usage from transcript
 */
function getTokenUsage() {
  const cwd = process.cwd();
  const projectPath = cwd.replace(/\//g, "-").replace(/^-/, "");
  const transcriptDir = path.join(
    process.env.HOME || "",
    ".claude",
    "projects",
    `-${projectPath}`
  );

  try {
    const files = fs.readdirSync(transcriptDir).filter((f) => f.endsWith(".jsonl"));
    if (files.length === 0) return null;

    // Get most recent
    const sorted = files
      .map((f) => ({
        name: f,
        mtime: fs.statSync(path.join(transcriptDir, f)).mtime,
      }))
      .sort((a, b) => b.mtime - a.mtime);

    const transcriptFile = path.join(transcriptDir, sorted[0].name);
    const content = fs.readFileSync(transcriptFile, "utf-8");
    const lines = content.trim().split("\n");

    let input = 0,
      output = 0,
      cacheRead = 0,
      cacheWrite = 0;
    let messageCount = 0;

    for (const line of lines) {
      try {
        const entry = JSON.parse(line);
        if (entry.type === "assistant" && entry.message?.usage) {
          const usage = entry.message.usage;
          input += usage.input_tokens || 0;
          output += usage.output_tokens || 0;
          cacheRead += usage.cache_read_input_tokens || 0;
          cacheWrite += usage.cache_creation_input_tokens || 0;
          messageCount++;
        }
      } catch (e) {
        // Skip
      }
    }

    // Calculate cost
    const cost =
      (input * 5) / 1_000_000 +
      (output * 25) / 1_000_000 +
      (cacheRead * 0.5) / 1_000_000 +
      (cacheWrite * 6.25) / 1_000_000;

    return {
      inputTokens: input,
      outputTokens: output,
      cacheReadTokens: cacheRead,
      cacheWriteTokens: cacheWrite,
      totalTokens: input + output + cacheRead + cacheWrite,
      messageCount,
      cost: Math.round(cost * 100) / 100,
      transcriptFile: sorted[0].name,
    };
  } catch (e) {
    return null;
  }
}

/**
 * Get recent files modified in session
 */
function getRecentFiles() {
  try {
    const result = execSync(
      'find . -type f -mmin -60 -not -path "./.git/*" -not -path "./node_modules/*" 2>/dev/null | head -20',
      { encoding: "utf-8" }
    );
    return result.trim().split("\n").filter((f) => f);
  } catch (e) {
    return [];
  }
}

// ============================================================================
// Context Class
// ============================================================================

class Context {
  constructor(data = {}) {
    this.version = CONFIG.version;
    this.timestamp = new Date().toISOString();
    this.id = data.id || `ctx-${Date.now()}`;

    // Session info
    this.session = data.session || getSessionInfo();
    this.project = data.project || path.basename(process.cwd());
    this.cwd = data.cwd || process.cwd();

    // Git state
    this.git = data.git || getGitInfo();

    // Token usage
    this.usage = data.usage || getTokenUsage();

    // Custom metadata
    this.note = data.note || "";
    this.decisions = data.decisions || [];
    this.todos = data.todos || [];
    this.recentFiles = data.recentFiles || getRecentFiles();

    // Hot context (summary for quick recovery)
    this.hotContext = data.hotContext || "";
  }

  /**
   * Serialize context to JSON
   */
  serialize() {
    return JSON.stringify(
      {
        version: this.version,
        timestamp: this.timestamp,
        id: this.id,
        session: this.session,
        project: this.project,
        cwd: this.cwd,
        git: this.git,
        usage: this.usage,
        note: this.note,
        decisions: this.decisions,
        todos: this.todos,
        recentFiles: this.recentFiles,
        hotContext: this.hotContext,
      },
      null,
      2
    );
  }

  /**
   * Deserialize context from JSON
   */
  static deserialize(json) {
    const data = typeof json === "string" ? JSON.parse(json) : json;
    return new Context(data);
  }

  /**
   * Generate summary for display
   */
  getSummary() {
    const lines = [];

    lines.push(`📋 Context: ${this.id}`);
    lines.push(`📅 Saved: ${this.timestamp}`);
    lines.push(`📁 Project: ${this.project}`);

    if (this.git) {
      lines.push(`🌿 Git: ${this.git.branch} (${this.git.commit})`);
    }

    if (this.session) {
      lines.push(`🤖 Agent: ${this.session.current_agent}`);
    }

    if (this.usage) {
      lines.push(
        `📊 Tokens: ${this.usage.totalTokens} (${this.usage.messageCount} messages)`
      );
      lines.push(`💰 Cost: $${this.usage.cost}`);
    }

    if (this.note) {
      lines.push(`📝 Note: ${this.note}`);
    }

    if (this.todos.length > 0) {
      lines.push(`✅ Todos: ${this.todos.length} items`);
    }

    return lines.join("\n");
  }
}

// ============================================================================
// Save / Restore Functions
// ============================================================================

/**
 * Save current context to file
 */
async function save(options = {}) {
  ensureDir(CONFIG.contextDir);

  const context = new Context({
    note: options.note,
    decisions: options.decisions,
    todos: options.todos,
    hotContext: options.hotContext,
  });

  const filename = options.name || `checkpoint-${Date.now()}.json`;
  const filepath = path.join(CONFIG.contextDir, filename);

  fs.writeFileSync(filepath, context.serialize());

  // Also save as "latest"
  fs.writeFileSync(
    path.join(CONFIG.contextDir, "latest.json"),
    context.serialize()
  );

  // Cleanup old checkpoints
  cleanupOldCheckpoints();

  return {
    success: true,
    id: context.id,
    filepath,
    summary: context.getSummary(),
  };
}

/**
 * Restore context from file
 */
async function restore(options = {}) {
  const filename = options.name || "latest.json";
  const filepath = path.join(CONFIG.contextDir, filename);

  if (!fs.existsSync(filepath)) {
    return {
      success: false,
      error: "No context found",
      searchedPath: filepath,
    };
  }

  const json = fs.readFileSync(filepath, "utf-8");
  const context = Context.deserialize(json);

  return {
    success: true,
    context,
    summary: context.getSummary(),
  };
}

/**
 * List available checkpoints
 */
async function list() {
  ensureDir(CONFIG.contextDir);

  const files = fs.readdirSync(CONFIG.contextDir).filter((f) => f.endsWith(".json"));

  const checkpoints = files.map((f) => {
    const filepath = path.join(CONFIG.contextDir, f);
    const stat = fs.statSync(filepath);
    let context = null;

    try {
      context = Context.deserialize(fs.readFileSync(filepath, "utf-8"));
    } catch (e) {
      // Invalid
    }

    return {
      name: f,
      mtime: stat.mtime,
      size: stat.size,
      id: context?.id,
      project: context?.project,
      note: context?.note,
    };
  });

  return checkpoints.sort((a, b) => b.mtime - a.mtime);
}

/**
 * Cleanup old checkpoints
 */
function cleanupOldCheckpoints() {
  const files = fs
    .readdirSync(CONFIG.contextDir)
    .filter((f) => f.startsWith("checkpoint-") && f.endsWith(".json"));

  if (files.length <= CONFIG.maxCheckpoints) return;

  // Sort by mtime
  const sorted = files
    .map((f) => ({
      name: f,
      mtime: fs.statSync(path.join(CONFIG.contextDir, f)).mtime,
    }))
    .sort((a, b) => b.mtime - a.mtime);

  // Delete oldest
  for (let i = CONFIG.maxCheckpoints; i < sorted.length; i++) {
    fs.unlinkSync(path.join(CONFIG.contextDir, sorted[i].name));
  }
}

// ============================================================================
// Exports
// ============================================================================

module.exports = {
  Context,
  save,
  restore,
  list,
  CONFIG,
};

// ============================================================================
// CLI
// ============================================================================

if (require.main === module) {
  const args = process.argv.slice(2);
  const command = args[0];

  if (command === "save") {
    const note = args.slice(1).join(" ");
    save({ note })
      .then((result) => {
        if (result.success) {
          console.log("✅ Context saved!");
          console.log(result.summary);
        } else {
          console.error("❌ Failed to save:", result.error);
        }
      })
      .catch(console.error);
  } else if (command === "restore") {
    const name = args[1];
    restore({ name })
      .then((result) => {
        if (result.success) {
          console.log("✅ Context restored!");
          console.log(result.summary);
        } else {
          console.error("❌ Failed to restore:", result.error);
        }
      })
      .catch(console.error);
  } else if (command === "list") {
    list()
      .then((checkpoints) => {
        if (checkpoints.length === 0) {
          console.log("No checkpoints found.");
          return;
        }
        console.log("📋 Available Checkpoints:\n");
        for (const cp of checkpoints) {
          const date = new Date(cp.mtime).toLocaleString();
          console.log(`  ${cp.name}`);
          console.log(`    📅 ${date}`);
          if (cp.project) console.log(`    📁 ${cp.project}`);
          if (cp.note) console.log(`    📝 ${cp.note}`);
          console.log("");
        }
      })
      .catch(console.error);
  } else {
    console.log("ATLAS Context Serialization");
    console.log("");
    console.log("Usage:");
    console.log("  node index.js save [note]     - Save current context");
    console.log("  node index.js restore [name]  - Restore context");
    console.log("  node index.js list            - List checkpoints");
    console.log("");
    console.log("Storage: ~/.atlas/context/");
  }
}
