# Strategy: Git Worktrees & Monorepo Governance

In large repositories and monorepos, each working directory checkout duplicates heavy dependencies (`node_modules`) and build artifacts (`out/`, `dist/`, `.next/`), multiplying disk usage by 2–4 GB per branch.

---

## 1. Waste Mechanisms & Heuristics

* **Worktree Proliferation**: Teams using `git worktree add` for parallel reviews, release stabilization, or bug fixing often leave old worktrees behind after branches are merged or abandoned.
* **Hidden Dependency Duplication**: Even when code is identical, package managers instantiate separate node modules trees in each worktree checkout unless configured with shared pnpm stores.

---

## 2. The Three-Key Verification Strategy

Never delete a worktree directory without proving all three safety conditions:

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

### Detailed Check Commands:
```bash
# 1. Cleanliness Check
git -C <path> status --porcelain
# Must return empty. If any file is listed (even untracked), DO NOT DELETE.

# 2. Remote Survival Check
COMMIT=$(git -C <path> rev-parse HEAD)
git -C <main-repo> branch -r --contains "$COMMIT"
# If output is non-empty, the commit exists on remote or has merged into a tracked branch.
```

---

## 3. Safe Pruning Workflow

1. **Remove Directory via Git**:
   ```bash
   git -C <main-repo> worktree remove --force <worktree-path>
   ```
2. **Fallback to Direct Removal**:
   If Git reports metadata divergence or detached states, verify cleanliness and delete via `rm -rf <worktree-path>`.
3. **Prune Stale Worktree Metadata**:
   ```bash
   git -C <main-repo> worktree prune
   ```
4. **Selective Dependency Pruning (Alternative)**:
   If a worktree is still needed occasionally for reference, delete only its `node_modules` and build directories:
   ```bash
   rm -rf <worktree-path>/node_modules <worktree-path>/dist <worktree-path>/out
   ```
   This retains 99% of the disk savings while keeping source code and local Git status intact.
