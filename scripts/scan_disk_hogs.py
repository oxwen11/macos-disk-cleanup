#!/usr/bin/env python3
"""
Fast, parallel, timeout-safe disk usage inspector for macOS development machines.
Scans high-density planes without hanging, and checks APFS snapshots and container runtimes.
"""

import os
import glob
import subprocess
import concurrent.futures

KNOWN_DEVELOPER_TARGETS = [
    # Downloads & Trash
    '~/Downloads',
    '~/.Trash',
    # AI IDEs & Agent Runtimes
    '~/Library/Application Support/Cursor/snapshots',
    '~/Library/Application Support/Cursor/User/globalStorage/anysphere.cursor-agent-worker',
    '~/Library/Application Support/Claude/vm_bundles',
    '~/Library/Application Support/Google',
    # Virtualization & Containers
    '~/.docker',
    '~/.orbstack',
    # Package Managers & Toolchains
    '~/Library/Caches',
    '~/.cache',
    '~/.bun/install',
    '~/.npm',
    '~/.cargo',
    '~/.rustup',
    '~/.local/share',
    # Workspaces & Repositories
    '~/Work',
    '~/Code',
    '~/Projects',
    '~/GitHub',
    '/Applications',
]

def get_dynamic_targets():
    targets = list(KNOWN_DEVELOPER_TARGETS)
    gc_path = os.path.expanduser('~/Library/Group Containers')
    if os.path.exists(gc_path):
        for pattern in ['*orbstack*', '*docker*']:
            for match in glob.glob(os.path.join(gc_path, pattern)):
                targets.append(match)

    # Detect sibling worktree clusters in home directory (~/*-worktrees)
    home_dir = os.path.expanduser('~')
    for match in glob.glob(os.path.join(home_dir, '*-worktrees')):
        if os.path.isdir(match):
            targets.append(match)

    return targets

def check_path_size(path_str, timeout_sec=5):
    exp = os.path.expanduser(path_str)
    if not os.path.exists(exp):
        return None
    try:
        res = subprocess.run(
            ['du', '-sk', '-x', exp],
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            timeout=timeout_sec
        )
        kb = int(res.stdout.split()[0])
        return (kb, path_str)
    except subprocess.TimeoutExpired:
        return (-1, path_str)
    except Exception:
        return None

def main():
    print("=== macOS Developer Disk Usage Scan ===")

    # 1. Overall volume usage
    res = subprocess.run(['df', '-h', '/'], capture_output=True, text=True)
    for line in res.stdout.strip().split('\n'):
        print(line)
    print()

    # 2. Check APFS local snapshots
    try:
        snap_res = subprocess.run(['tmutil', 'listlocalsnapshots', '/'], capture_output=True, text=True, timeout=3)
        snapshots = [s for s in snap_res.stdout.strip().split('\n') if s.strip() and not s.startswith('Snapshots for')]
        if snapshots:
            print(f"  [!] Found {len(snapshots)} APFS Time Machine local snapshot(s) holding deleted blocks.")
    except Exception:
        pass

    # 3. Parallel scan of candidate targets
    all_targets = get_dynamic_targets()
    with concurrent.futures.ThreadPoolExecutor(max_workers=12) as executor:
        results = list(executor.map(check_path_size, all_targets))

    valid = [r for r in results if r is not None]
    valid.sort(key=lambda x: x[0], reverse=True)

    print("--- High-Yield Candidates (>500MB or Timeout) ---")
    for kb, p in valid:
        if kb == -1:
            print(f"  [TIMEOUT] {p} (High file density: inspect subdirectories)")
        elif kb > 500 * 1024:
            print(f"  {kb / 1024 / 1024:6.2f} GB : {p}")

if __name__ == '__main__':
    main()
