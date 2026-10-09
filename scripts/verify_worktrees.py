#!/usr/bin/env python3
"""
Verify Git worktrees before cleanup using Dual-Track Governance.
Checks:
1. Working tree cleanliness (no uncommitted edits/untracked files)
2. Upstream commit status (commits already pushed to remote or merged into origin)

Outputs actionable dual-track recommendations:
- Track A (Full Archive): 100% clean & in remote -> Safe to delete entire directory.
- Track B (Dormant Stripping): Dirty, drafts, or WIP -> Keep code/drafts intact, strip only heavy dependencies (node_modules/dist/out).
"""

import os
import sys
import subprocess

def inspect_worktree(repo_path, main_repo_path=None):
    if not os.path.exists(repo_path):
        return None

    git_indicator = os.path.join(repo_path, '.git')
    if not os.path.exists(git_indicator):
        return {
            'path': repo_path,
            'is_git': False,
            'safe_full': False,
            'reason': 'Not a Git repository or worktree'
        }

    try:
        branch = subprocess.run(['git', '-C', repo_path, 'rev-parse', '--abbrev-ref', 'HEAD'], capture_output=True, text=True, timeout=3).stdout.strip()
        commit_sha = subprocess.run(['git', '-C', repo_path, 'rev-parse', 'HEAD'], capture_output=True, text=True, timeout=3).stdout.strip()
        last_log = subprocess.run(['git', '-C', repo_path, 'log', '-1', '--oneline'], capture_output=True, text=True, timeout=3).stdout.strip()

        status = subprocess.run(['git', '-C', repo_path, 'status', '--porcelain'], capture_output=True, text=True, timeout=3).stdout.strip()
        dirty_files = [line for line in status.split('\n') if line.strip()]

        in_remote = False
        target_repo = main_repo_path if main_repo_path and os.path.exists(main_repo_path) else repo_path
        remote_branches = subprocess.run(
            ['git', '-C', target_repo, 'branch', '-r', '--contains', commit_sha],
            capture_output=True, text=True, timeout=5
        ).stdout.strip()
        if remote_branches:
            in_remote = True

        safe_full = (len(dirty_files) == 0) and in_remote

        # Check for heavy dependency directories
        heavy_dirs = []
        for d in ['node_modules', 'dist', 'out', '.next', 'target']:
            dp = os.path.join(repo_path, d)
            if os.path.exists(dp):
                heavy_dirs.append(d)

        return {
            'path': repo_path,
            'name': os.path.basename(repo_path),
            'branch': branch,
            'sha': commit_sha[:8],
            'last_log': last_log,
            'dirty_count': len(dirty_files),
            'dirty_files': dirty_files[:5],
            'in_remote': in_remote,
            'safe_full': safe_full,
            'heavy_dirs': heavy_dirs
        }
    except Exception as e:
        return {
            'path': repo_path,
            'is_git': True,
            'safe_full': False,
            'reason': f'Error executing git command: {e}'
        }

def main():
    if len(sys.argv) < 2:
        print("Usage: verify_worktrees.py <directory-containing-worktrees> [main-repo-path]")
        sys.exit(1)

    parent_dir = os.path.abspath(os.path.expanduser(sys.argv[1]))
    main_repo = os.path.abspath(os.path.expanduser(sys.argv[2])) if len(sys.argv) > 2 else None

    if not os.path.isdir(parent_dir):
        print(f"Error: {parent_dir} is not a directory")
        sys.exit(1)

    entries = sorted(os.listdir(parent_dir))
    track_a = []
    track_b = []

    for item in entries:
        full_path = os.path.join(parent_dir, item)
        if not os.path.isdir(full_path):
            continue
        res = inspect_worktree(full_path, main_repo)
        if not res or not res.get('is_git', True):
            continue
        if res.get('safe_full'):
            track_a.append(res)
        else:
            track_b.append(res)

    print(f"=== Dual-Track Worktree Audit in {parent_dir} ===\n")
    print(f"--- TRACK A: Full Archive & Removal ({len(track_a)} items - 100% clean & in remote) ---")
    if not track_a:
        print("  (None found)")
    for item in track_a:
        print(f"  ✓ {item['name']:<38} [{item['branch']}] {item['last_log']}")

    print(f"\n--- TRACK B: Dormant Stripping ({len(track_b)} items - has uncommitted edits/unpushed code) ---")
    print("  * Preserves 100% of user code and drafts. Safely strip heavy directories to reclaim ~95% space:")
    if not track_b:
        print("  (None found)")
    for item in track_b:
        reasons = []
        if item.get('dirty_count', 0) > 0:
            reasons.append(f"{item['dirty_count']} uncommitted files")
        if not item.get('in_remote'):
            reasons.append("commit not on remote")
        heavy = f" [contains: {', '.join(item['heavy_dirs'])}]" if item.get('heavy_dirs') else ""
        print(f"  • {item['name']:<38} -> {', '.join(reasons)}{heavy}")
        if item.get('heavy_dirs'):
            targets = ' '.join([os.path.join(item['path'], d) for d in item['heavy_dirs']])
            print(f"      Strip command: rm -rf {targets}")

if __name__ == '__main__':
    main()
