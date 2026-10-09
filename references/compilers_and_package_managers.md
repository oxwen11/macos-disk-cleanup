# Strategy: Compilers, Toolchains & Package Manager Caches

Developer machines accumulate superseded compiler toolchains and duplicated global package caches that are completely safe to flush or deduplicate.

---

## 1. Waste Mechanisms & Heuristics

### A. Rust Toolchain Version Stacking
* **Mechanism**: `rustup` installs independent ~1.2 GB toolchains for every requested compiler version (e.g. `1.90.0`, `1.92.0`, `1.97.0`, `nightly`, `stable`).
* **Inspection**:
  ```bash
  rustup toolchain list
  ```
* **Remediation Strategy**:
  * Preserve the default/active toolchain (typically `stable`).
  * Uninstall superseded historical versions:
    ```bash
    rustup toolchain uninstall <old-toolchain-name>
    ```

### B. Node & Bun Global Stores
* **Global npm cache**: Accumulates tarballs in `~/.npm` or configured package caches.
  * Safe cleanup: `npm cache clean --force`
* **Bun global store**: `~/.bun/install/global/node_modules` and `cache/`.
  * Check size and clean old packages: `bun pm cache rm`
* **pnpm content-addressable store**:
  * Clean unreferenced packages: `pnpm store prune`
* **Yarn cache**:
  * Clean cache: `yarn cache clean`

### C. Python & UV Caches
* **UV Cache**: `~/.cache/uv` or `~/.local/share/uv` can hold gigabytes of wheels and source checkouts.
  * Safe cleanup: `uv cache clean`
* **Pip cache**:
  * Safe cleanup: `pip cache purge`
