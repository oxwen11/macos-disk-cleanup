# Strategy: Virtualization, Containers & APFS Snapshots

Virtual machines, container engines, and macOS APFS local snapshots can silently consume tens of gigabytes that standard directory traversals miss.

---

## 1. Waste Mechanisms & Heuristics

### A. Docker & OrbStack Container Storage
* **The Symptom**: `df -h` shows significant space allocated to container volumes, or `~/Library/Group Containers/*.dev.orbstack` / `~/.docker` measures multiple gigabytes.
* **Underlying Bloat**:
  * **Build Cache**: Intermediate build steps (`docker buildx`) can accumulate tens of gigabytes of untracked cache layers.
  * **Unused/Dangling Images**: Previous versions of base images (e.g. `ubuntu:latest`, `node:alpine`) that are no longer referenced by active containers.
  * **Stopped Ephemeral Containers**: Test or evaluation harness runs that finished but were not launched with `--rm`.

### B. APFS Local Snapshots (Time Machine)
* **The Symptom**: Large discrepancy between `df -h` available space and Finder "Available" space.
* **Mechanism**: macOS creates local APFS snapshots when Time Machine backups are pending or system updates occur.
* **Inspection**:
  ```bash
  tmutil listlocalsnapshots /
  ```
* **Remediation**:
  ```bash
  # Delete specific local snapshot date if necessary
  tmutil deletelocalsnapshots <snapshot-date>
  ```

---

## 2. Safe Docker / OrbStack Recovery Workflow

1. **Inspect Reclaimable Space**:
   ```bash
   docker system df
   ```
2. **Safe Pruning (Zero Impact on Named Volumes)**:
   ```bash
   docker system prune -a -f
   ```
   * *What it removes*: All stopped containers, all unused networks, all dangling and unreferenced images, and build cache.
   * *What it protects*: Named volumes (persistent database storage or project mounts).
3. **Volume Pruning (Only with User Consent)**:
   ```bash
   docker volume prune -f
   ```
   * Only execute if the user confirms that anonymous/orphaned database volumes from past test runs are no longer required.
