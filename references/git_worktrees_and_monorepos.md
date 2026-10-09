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
  (git worktree remove --force)          (rm -rf node_modules dist out)
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
For branches that must be retained or have uncommitted scratch files:
1. Identify dependencies:
   ```bash
   rm -rf <worktree-path>/node_modules <worktree-path>/dist <worktree-path>/out <worktree-path>/.next
   ```
2. **Outcome**:
   * Reclaims ~95% of the disk footprint (2GB–4GB per worktree).
   * 100% preserves uncommitted work, scratch notes, and Git branch pointer.
   * Can be re-hydrated in minutes via `pnpm install` / `npm install` when reactivated.
