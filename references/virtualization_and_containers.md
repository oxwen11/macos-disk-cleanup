# Strategy: Virtualization, Containers & APFS Snapshots

Virtual machines, container engines, and macOS APFS local snapshots can silently consume tens of gigabytes that standard directory traversals miss.

---

## 1. APFS Mechanics & The "System Data" Mystery

macOS Finder often classifies massive disk usage as opaque **"System Data" (系统资料)**. Understanding the underlying APFS mechanics prevents diagnostic confusion:

### A. The "I Deleted Files but Available Space Didn't Increase" Phenomenon
* **The Cause: APFS Local Snapshots**: When Time Machine backups are pending or system updates occur, macOS creates invisible APFS volume snapshots. Because APFS is a Copy-on-Write (CoW) filesystem, deleting files merely unlinks them from the active volume; **the blocks remain allocated in the snapshot until the snapshot itself is purged**.
* **Diagnostic Command**:
  ```bash
  tmutil listlocalsnapshots /
  ```
* **Remediation**:
  If snapshots are holding deleted gigabytes captive:
  ```bash
  # Delete a specific snapshot
  tmutil deletelocalsnapshots <snapshot-date>
  ```

### B. Dynamic Swap & Virtual Memory (`/System/Volumes/VM`)
* Under heavy memory pressure, macOS expands swapfiles in `/System/Volumes/VM/swapfile*`. These can balloon to 15GB–25GB and shrink only after memory pressure subsides or upon reboot.

### C. The 10%–15% System Headroom Threshold (Health Red Line)
* **Rule**: macOS requires **at least 10%–15% free disk headroom (typically 20GB–35GB minimum)** to function reliably.
* **Why**:
  1. APFS Copy-on-Write requires free space to perform safe block reallocations.
  2. Memory swapping degrades drastically when free disk drops below 10%, causing UI micro-stutters and memory allocator panics.
  3. System updates require 15GB–20GB of transient staging space in `/System/Volumes/Update`.
* **Guideline**: If free space drops below 10%, treat disk cleanup as a critical system priority.

---

## 2. Docker & OrbStack Container Governance

### A. Waste Archetypes
* **Build Cache**: Intermediate build layers (`docker buildx`) accumulate silently over months.
* **Unreferenced Base Images**: Older versions of base containers (e.g. `ubuntu`, `node`, `python`) left behind after Dockerfile bumps.
* **Stopped Ephemeral Containers**: Test or evaluation harness containers that were not started with `--rm`.

### B. Safe Recovery Workflow
1. **Inspect Reclaimable Space**:
   ```bash
   docker system df
   ```
2. **Safe Prune (Protects Persistent Named Volumes)**:
   ```bash
   docker system prune -a -f
   ```
   * *Reclaims*: Stopped containers, dangling/unused images, unused networks, and build cache.
   * *Preserves*: Named volumes (database storage and shared data mounts).
3. **Volume Pruning (Requires Explicit Confirmation)**:
   ```bash
   docker volume prune -f
   ```
   * Only execute if the user explicitly confirms that test/database volumes are disposable.
