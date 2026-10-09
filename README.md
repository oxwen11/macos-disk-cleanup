# macOS Developer Disk Space Governance & Optimization (`macos-disk-cleanup`)

A systematic, strategy-driven agent skill to diagnose, discover, and safely reclaim storage on macOS developer machines without risking personal assets, active code, or configuration settings.

---

## Why this Skill?

Developer machines on macOS uniquely suffer from silent, massive storage bloat caused by modern workflows:
1. **AI IDEs & Agent Runtimes**: Shadow AST codebase snapshots (e.g. Cursor snapshots reaching tens of gigabytes), accumulated background agent worker versions, and ephemeral multi-agent multiplexer worktrees.
2. **Git Worktree Dependency Multiplication**: In monorepos, each worktree checkout duplicates full `node_modules` and build trees (2GB–4GB per branch).
3. **Container & VM Residue**: Stale Docker / OrbStack build layer caches, unreferenced base images, and forgotten rootfs VM bundles.
4. **Toolchain Stacking**: Rustup compiler versions, redundant Node/Bun package stores, and on-device ML model weights (e.g. Gemini Nano in Chrome).

Standard cleaning tools often blindly purge or ignore these developer-specific assets. This skill codifies **discovery heuristics, developer waste archetypes, and strict safety gates** so that an AI agent or human can safely analyze and reclaim storage.

---

## Skill Architecture

```
macos-disk-cleanup/
├── SKILL.md                                 # Master diagnostic decision tree, discovery heuristics & safety gates
├── agents/
│   └── openai.yaml                          # Skill metadata & invocation policy
├── scripts/
│   ├── scan_disk_hogs.py                    # Fast parallel, timeout-safe scanner across candidate planes
│   └── verify_worktrees.py                  # Automated Three-Key Git worktree safety gate verification
└── references/
    ├── ai_ides_and_agent_runtimes.md        # Shadow AST codebase snapshots, agent worker versions, agent worktrees
    ├── git_worktrees_and_monorepos.md       # Multi-worktree node_modules multiplication, clean & push verification protocol
    ├── virtualization_and_containers.md     # Docker/OrbStack build cache, dangling base images, APFS local snapshots
    ├── compilers_and_package_managers.md    # Rust toolchain stacking, global npm/bun/pnpm/yarn stores, UV/pip caches
    ├── browsers_and_on_device_models.md     # On-device LLM/multimodal models, GPU shader caches, strict profile boundaries
    └── system_cleaners_and_downloads.md     # Mole CLI invocation, whitelist safeguards, installer vs document segregation
```

---

## Core Safety Invariants

* **Read-Only Phase**: Zero deletions during analysis. Never run destructive commands without explicit user confirmation.
* **The Three-Key Git Worktree Safety Gate**:
  * `Key 1 (Clean)`: `git status --porcelain == 0` (no uncommitted edits, no untracked files).
  * `Key 2 (Remote Presence)`: Commit SHA exists in remote repository or has been merged into a primary branch.
  * `Key 3 (Upstream Sync)`: No unpushed commits ahead of tracking branch.
* **The Personal Asset Fence**: Software installer bundles (`.dmg`, `.pkg`, `.zip`, `.exe`) are strictly segregated from user work products (`.pdf`, `.docx`, images, media, notes).
* **The Active Process Barrier**: Cross-reference candidate runtime directories against `ps aux` to protect actively running daemons or editors.

---

## Installation

### Method 1: Using `skill-installer`
```bash
python3 scripts/install-skill-from-github.py --repo oxwen11/macos-disk-cleanup
```

### Method 2: Manual Clone
Clone directly into your Agent skills directory (e.g., `~/.agents/skills/`):
```bash
git clone https://github.com/oxwen11/macos-disk-cleanup.git ~/.agents/skills/macos-disk-cleanup
```

---

## Invocation

This skill is configured with `disable-model-invocation: true` to prevent unsolicited background model loading and preserve context window space.

Trigger it explicitly when needed:
```bash
/macos-disk-cleanup
```
or ask your agent:
> *"Run $macos-disk-cleanup to inspect disk usage and prepare a safe cleanup plan."*

---

## License

MIT License. See [LICENSE](LICENSE) for details.
