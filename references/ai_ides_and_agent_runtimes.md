# Strategy: AI IDEs & Agent Runtimes Bloat

Modern AI editors (Cursor, Windsurf, Trae, etc.) and coding agent harnesses (Claude Code, Codex, OpenHands, Aider, Cline, etc.) introduce new, aggressive storage consumption patterns that standard cleaners ignore.

---

## 1. Waste Mechanisms & Heuristics

### A. Shadow Workspaces & Codebase Snapshots
* **Why it accumulates**: To power local semantic search, AST indexing, and checkpoint rollbacks without polluting your Git working tree, AI IDEs clone full file trees into internal shadow stores.
* **Heuristic Location**:
  * `~/Library/Application Support/<Editor>/snapshots/`
  * `~/Library/Application Support/<Editor>/User/globalStorage/`
* **Typical Impact**: 10–30 GB across multiple monorepo checkouts.
* **Safe Optimization Strategy**:
  * Deleting snapshot trees (`snapshots/`, `codebases/`, `stores/`) is **completely safe** for active code, Git history, user settings, and extensions.
  * **Trade-off**: The editor will cleanly re-index active projects on next launch (creating a lean, current index). Checkpoint rollback for conversations older than the cleanup will be unavailable.

### B. Agent Worker Version Stacking
* **Why it accumulates**: Agent background workers (e.g. `cursor-agent`, custom daemon CLI bundles) update automatically every few days. The updater frequently retains every previously downloaded binary bundle (~500MB–800MB each) in historical version folders.
* **Heuristic Location**:
  * `~/Library/Application Support/<Editor>/User/globalStorage/<agent-worker>/.../versions/`
  * `~/.<agent-cli>/versions/` or `~/.local/share/<tool>/versions/`
* **Safe Optimization Strategy**:
  1. Inspect active processes via `ps aux | grep <worker-name>`.
  2. Identify the active running version.
  3. Purge all superseded version subdirectories.

### C. Agent Multiplexer Ephemeral Worktrees
* **Why it accumulates**: Multi-agent runners and autonomous coding scripts spawn temporary Git worktrees in dedicated hidden locations to run parallel coding or evaluation tasks. Over time, dozens of abandoned worktrees remain on disk with full `node_modules` and build trees.
* **Heuristic Location**:
  * `~/.<tool>/worktrees/` (e.g., `~/.<agent-cli>/worktrees`, `~/.cursor/worktrees`, `~/.codex/worktrees`)
* **Safe Optimization Strategy**:
  * Check for running agent jobs (`ps aux`).
  * For idle agent tools, verify if worktrees contain uncommitted human changes.
  * Prune finished tasks and ephemeral scratch directories.

### D. Bundled Desktop VMs & Container Images
* **Why it accumulates**: Desktop AI applications may ship or download full Linux rootfs VM bundles or sandbox containers for terminal execution isolation.
* **Heuristic Location**:
  * `~/Library/Application Support/<App>/vm_bundles/`
* **Safe Optimization Strategy**:
  * Check file timestamps and application usage. Stale VM images (large `rootfs.img` disk images) from deprecated or unused features can be discarded with zero impact on CLI or standard app usage.

### E. Telemetry Traces & Sqlite Wal Files
* **Why it accumulates**: Agent sessions generate extensive streaming event logs and sqlite audit databases (e.g., `network-logs/`, `*.sqlite-wal`).
* **Safe Optimization Strategy**:
  * Purge historical network request traces and rotation logs exceeding 1 GB.
