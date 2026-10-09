#!/usr/bin/env python3
"""
Verify Git worktrees before cleanup.
Checks:
1. Working tree cleanliness (no uncommitted edits/untracked files)
2. Upstream commit status (commits already pushed to remote or merged into origin)
Only worktrees that are 100% clean and pushed/merged are marked as SAFE TO DELETE.
"""

import os
import sys
import subprocess

def inspect_worktree(repo_path, main_repo_path=None):
    if not os.path.exists(repo_path):
        return None
    
    # Check if git directory or worktree gitlink exists
    git_indicator = os.path.join(repo_path, '.git')
    if not os.path.exists(git_indicator):
        return {
            'path': repo_path,
            'is_git': False,
            'safe': False,
            'reason': 'Not a Git repository or worktree'
        }

    try:
        # Branch or detached HEAD
        branch = subprocess.run(['git', '-C', repo_path, 'rev-parse', '--abbrev-ref', 'HEAD'], capture_output=True, text=True, timeout=3).stdout.strip()
        commit_sha = subprocess.run(['git', '-C', repo_path, 'rev-parse', 'HEAD'], capture_output=True, text=True, timeout=3).stdout.strip()
        last_log = subprocess.run(['git', '-C', repo_path, 'log', '-1', '--oneline'], capture_output=True, text=True, timeout=3).stdout.strip()

        # Dirty files
        status = subprocess.run(['git', '-C', repo_path, 'status', '--porcelain'], capture_output=True, text=True, timeout=3).stdout.strip()
        dirty_files = [line for line in status.split('\n') if line.strip()]

        # Check if commit exists on origin remote
        in_remote = False
        target_repo = main_repo_path if main_repo_path and os.path.exists(main_repo_path) else repo_path
        remote_branches = subprocess.run(
            ['git', '-C', target_repo, 'branch', '-r', '--contains', commit_sha],
            capture_output=True, text=True, timeout=5
        ).stdout.strip()
        if remote_branches:
            in_remote = True

        safe = (len(dirty_files) == 0) and in_remote

        return {
            'path': repo_path,
            'name': os.path.basename(repo_path),
            'branch': branch,
            'sha': commit_sha[:8],
            'last_log': last_log,
            'dirty_count': len(dirty_files),
            'dirty_files': dirty_files[:5],
            'in_remote': in_remote,
            'remote_branches': remote_branches.split('\n') if remote_branches else [],
            'safe': safe
        }
    except Exception as e:
        return {
            'path': repo_path,
            'is_git': True,
            'safe': False,
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
    safe_list = []
    unsafe_list = []

    for item in entries:
        full_path = os.path.join(parent_dir, item)
        if not os.path.isdir(full_path):
            continue
        res = inspect_worktree(full_path, main_repo)
        if not res or not res.get('is_git', True):
            continue
        if res.get('safe'):
            safe_list.append(res)
        else:
            unsafe_list.append(res)

    print(f"=== Worktree Audit in {parent_dir} ===\n")
    print(f"[SAFE TO DELETE] ({len(safe_list)} items - 100% clean & in remote):")
    for item in safe_list:
        print(f"  ✓ {item['name']:<40} [{item['branch']}] {item['last_log']}")

    print(f"\n[DO NOT DELETE] ({len(unsafe_list)} items - has uncommitted edits or unpushed commits):")
    for item in unsafe_list:
        reasons = []
        if item.get('dirty_count', 0) > 0:
            reasons.append(f"{item['dirty_count']} uncommitted files")
        if not item.get('in_remote'):
            reasons.append("commit not found on remote")
        print(f"  ✗ {item.get('name', item['path']):<40} -> {', '.join(reasons)}")
        if item.get('dirty_files'):
            for d in item['dirty_files'][:2]:
                print(f"      * {d}")

if __name__ == '__main__':
    main()
