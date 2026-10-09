---
name: macos-disk-cleanup
description: Audit and safely reclaim disk space on macOS developer machines.
metadata:
  disable-model-invocation: true
---

# macOS Developer Disk Space Governance & Optimization Strategies

This skill provides a **strategic, hypothesis-driven methodology** to diagnose, discover, and safely recover disk space on macOS developer machines.

Instead of hardcoding a fragile list of static paths, this skill uses **discovery heuristics, waste archetypes, and safety gates**. It guides the agent to locate where space is truly consumed, understand *why* it accumulated, and present a risk-tiered proposal for user confirmation.

---

## 1. Diagnostic Decision Tree

When invoked, follow this strategic workflow:

```
[ User Requests Disk Diagnosis / Space Recovery ]
                       │
                       ▼
         [ Phase 1: Read-Only Discovery ]
   • Check volume metrics (df -h /)
   • Parallel-probe candidate planes (ThreadPoolExecutor)
   • Identify "timeout" directories as high-density signals
                       │
                       ▼
       [ Phase 2: Archetype Classification ]
   • Match bloat to Developer Waste Archetypes
   • Load corresponding Strategy Reference
                       │
                       ▼
        [ Phase 3: Safety Gate Evaluation ]
   • Apply Three-Key Gate for Git worktrees
   • Segregate installer binaries from human documents
   • Verify running processes in ps aux
                       │
                       ▼
     [ Phase 4: Tiered Proposal to User ]
   • Tier 1: Zero-Risk Stateless Disposables
   • Tier 2: Git Worktrees & Monorepo Cleanup
   • Tier 3: AI IDEs & Agent Runtimes
   • Tier 4: Toolchains & Compilers
   • Tier 5: System Cleaners (Mole CLI)
                       │
                       ▼
      [ Phase 5: Execution Under Explicit Consent ]
```

---

## 2. Non-Blocking Discovery Strategy

macOS APFS file systems cause standard commands like `du -sh ~/*` to hang due to millions of small files in monorepos and AST databases.

### Key Heuristics:
1. **The Three-Plane Decomposition**:
   * **System & Container Plane**: Divergence between volume size and observable directories (`df -h` vs `du`). Points to Docker/OrbStack virtual disks or APFS local snapshots (`tmutil listlocalsnapshots /`).
   * **Workspace Plane**: Monorepos and checkouts (`~/Work`, `~/Code`, `~/GitHub`).
   * **User Runtime Plane**: Application support and tool caches (`~/Library/Application Support`, `~/Library/Caches`, `~/.<tool>`).
2. **Asynchronous Bounded Probing**:
   * Always pass `-x` to `du` (e.g., `du -sk -x <path>`) to stay on a single filesystem.
   * Run probes concurrently with a 3–5 second timeout using `scripts/scan_disk_hogs.py`.
   * **Treat timeouts as high-density signals**: Any directory that times out contains thousands of small files (`node_modules`, Git trees, or AST caches) and warrants targeted 1st-level subdivision.

---

## 3. Domain Strategy References

Load these dedicated reference documents based on where space is concentrated:

* **AI IDEs & Agent Runtimes**: See [references/ai_ides_and_agent_runtimes.md](references/ai_ides_and_agent_runtimes.md)
  * *Covers*: Shadow AST codebase snapshots (Cursor, Windsurf), agent worker version stacking, multi-agent multiplexer worktrees (`~/.<tool>/worktrees`), and desktop VM bundles.
* **Git Worktrees & Monorepos**: See [references/git_worktrees_and_monorepos.md](references/git_worktrees_and_monorepos.md)
  * *Covers*: Multi-worktree dependency duplication, clean & push verification protocol, and selective dependency stripping.
* **Virtualization & Containers**: See [references/virtualization_and_containers.md](references/virtualization_and_containers.md)
  * *Covers*: Docker / OrbStack build caches, dangling base images, stopped containers, and APFS Time Machine snapshots.
* **Compilers & Package Managers**: See [references/compilers_and_package_managers.md](references/compilers_and_package_managers.md)
  * *Covers*: Rustup toolchain version stacking, global npm/bun/pnpm/yarn stores, and UV/pip caches.
* **Browsers & On-Device Models**: See [references/browsers_and_on_device_models.md](references/browsers_and_on_device_models.md)
  * *Covers*: Chrome/Edge on-device LLM model weights (OptGuideOnDeviceModel), GPU shader caches, and strict profile data boundaries.
* **System Cleaners & Downloads**: See [references/system_cleaners_and_downloads.md](references/system_cleaners_and_downloads.md)
  * *Covers*: Mole CLI automation (`mole clean`), system logs/trash, and installer media vs. human document segregation.

---

## 4. Safety Invariants (Zero-Destruction Rules)

1. **Read-Only Inspection**: Zero deletions during analysis. Never run `rm` without prior user confirmation.
2. **The Three-Key Git Worktree Safety Gate**:
   A worktree directory is safe to delete **only if**:
   * `Key 1 (Clean)`: `git status --porcelain` returns 0 changes (no uncommitted edits or untracked files).
   * `Key 2 (Remote Presence)`: `git branch -r --contains <HEAD>` proves the commit exists on remote or has merged into a primary branch.
   * `Key 3 (Upstream Sync)`: No unpushed commits ahead of tracking branch.
   * *Use `scripts/verify_worktrees.py` to automate this check before recommending removal.*
3. **The Personal Asset Fence**:
   * Never bulk-delete `~/Downloads`. Filter specifically for application installers (`.dmg`, `.pkg`, application `.zip`, `.exe`).
   * Preserve all documents, PDFs, media, and notes.
4. **The Active Process Barrier**:
   * Cross-reference any candidate runtime directory against `ps aux`. Never delete files belonging to actively executing processes.

---

## 5. Bundled Scripts

* **`scripts/scan_disk_hogs.py`**: Parallel, timeout-safe scanner that scans major candidate planes without freezing.
* **`scripts/verify_worktrees.py`**: Audits a folder of Git worktrees, asserting cleanliness and remote sync before flagging for deletion.
