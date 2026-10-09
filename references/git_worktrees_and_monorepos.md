# Strategy: Git Worktrees & Monorepo Governance

In large repositories and monorepos, each working directory checkout duplicates heavy dependencies (`node_modules`) and build artifacts (`out/`, `dist/`, `.next/`), multiplying disk usage by 2–4 GB per branch.

---

## 1. Waste Mechanisms & Heuristics

* **Worktree Proliferation**: Teams using `git worktree add` for parallel reviews, release stabilization, or bug fixing often leave old worktrees behind after branches are merged or abandoned.
* **Hidden Dependency Duplication**: Even when code is identical, package managers instantiate separate node modules trees in each worktree checkout unless configured with shared global stores.

---

## 2. The Three-Key Verification Strategy

Before removing an entire worktree directory, prove all three safety conditions:

```
                  [ Worktree Directory ]
                             │
         ┌───────────────────┴───────────────────┐
         ▼                                       ▼
    [Key 1: Clean]                          [Key 2: Pushed/Merged]
    git status --porcelain == 0             git branch -r --contains HEAD
         │                                  (or commit is in origin/master)
         └───────────────────┬───────────────────┘
                             ▼
                    [Key 3: Upstream Sync]
                    git log @{u}..HEAD is empty
                             │
                             ▼
                     [ SAFE TO DELETE ]
```

### Verification Commands:
```bash
# 1. Cleanliness Check
git -C <path> status --porcelain
# Must return empty. If any file is listed (even untracked), DO NOT DELETE the whole worktree.

# 2. Remote Survival Check
COMMIT=$(git -C <path> rev-parse HEAD)
git -C <main-repo> branch -r --contains "$COMMIT"
# If output is non-empty, the commit exists on remote or has merged into a tracked branch.
```

---

## 3. The Dual-Track Governance Strategy

Developers frequently have worktrees with uncommitted draft notes, WIP experiments, or historical code they cannot delete outright. Address this with **Dual-Track Governance**:

```
                 [ Candidate Worktree ]
                           │
       ┌───────────────────┴───────────────────┐
       ▼                                       ▼
  [All 3 Keys Pass]                      [Any Key Fails]
  (Clean & Pushed/Merged)                (Dirty, Drafts, or WIP)
       │                                       │
       ▼                                       ▼
  Track A: Complete Archive              Track B: Dormant Stripping
  Remove entire directory tree           Delete only dependencies & build caches
  (git worktree remove --force)          (rm -rf node_modules, target/, dist/, out/)
       │                                       │
       ▼                                       ▼
  Reclaims 100% of space                 Reclaims ~95% of space,
                                         PRESERVES 100% of code & drafts!
```

### Track A: Complete Archive & Deletion
For branches confirmed merged or archived remotely:
1. `git -C <main-repo> worktree remove --force <worktree-path>`
2. Fallback if git metadata diverges: `rm -rf <worktree-path>`
3. Prune stale worktree tracking: `git -C <main-repo> worktree prune`

### Track B: Dormant Stripping (Safe for Dirty / Uncommitted Worktrees)
For branches that must be retained or have uncommitted scratch files across multiple ecosystems:
1. **Frontend / Node**: `rm -rf <path>/node_modules <path>/dist <path>/out <path>/.next <path>/.turbo`
2. **Rust / Cargo**: `rm -rf <path>/target` (or `cargo clean`)
3. **Python**: `rm -rf <path>/.venv <path>/__pycache__`
4. **Outcome**:
   * Reclaims ~95% of the disk footprint (2GB–4GB per worktree).
   * 100% preserves uncommitted work, scratch notes, and Git branch pointers.
   * Can be re-hydrated in minutes on demand.

---

## 4. Operational Invariant: The APFS Inode Deletion Trap

When deleting deep directories like `node_modules` (often containing 150,000+ files and symlinks), macOS APFS performs synchronous journaling and extended attribute checks.
* **The Pitfall**: A single synchronous `rm -rf` can take 20–50+ seconds, causing tool timeouts in agent harnesses.
* **Remediation**:
  * Execute large directory removals concurrently across candidate folders.
  * When executing from an agent shell, do not panic on a 30s timeout; verify remaining item counts or allow background completion rather than assuming an error.

---

## 5. Sibling Worktree Discovery Heuristic

Do not only inspect subdirectories of standard project paths. Multi-agent tools and developers frequently instantiate worktree clusters as sibling directories under home (e.g. `~/*-worktrees/`).
* **Detection Heuristic**: Check whether `~/<folder>/*` contains a `.git` file with `gitdir:` pointers rather than a standard `.git/` directory.

