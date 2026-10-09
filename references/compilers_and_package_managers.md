# Strategy: Compilers, Toolchains & Package Manager Caches

Developer machines accumulate superseded compiler toolchains, package manager caches, and runtime binaries. This guide provides a **"Value over Vanity" evaluation framework** to distinguish between high-value cleanups and counterproductive cache purges.

---

## 1. The "Value over Vanity" Matrix (Rebuild Cost Evaluation)

Never clean caches solely to report an artificially inflated gigabyte number. A cache that saves significant daily compilation or download time is worth more than the disk space it occupies.

| Tier | Category | Examples | Rebuild Cost | Recommendation |
| :--- | :--- | :--- | :--- | :--- |
| 🟢 **Safe / High-Yield** | Obsolete Toolchains | Older `rustup` versions (e.g. legacy 1.90/1.92 when stable is 1.95+) | Zero | **Uninstall immediately** via toolchain manager |
| 🟢 **Safe / High-Yield** | Download Tarballs | `~/.npm/_cacache`, `~/.cache/pip`, `yarn cache` | Low (Auto-re-downloaded on demand) | **Clean routinely** |
| 🟢 **Safe / High-Yield** | Dead Project Artifacts | `out/`, `dist/`, `.turbo/`, `target/debug` of inactive repos | Fast | **Prune safely** |
| 🟡 **Trade-off / Caution** | Test Browsers | Playwright/Puppeteer browser binaries (`ms-playwright`) | **High** (~1GB download, blocks CI/tests) | **Do not purge** unless test suites are no longer used locally |
| 🟡 **Trade-off / Caution** | Local Model Caches | HuggingFace (`~/.cache/huggingface`), ModelScope | **Very High** (Multi-GB downloads) | **Confirm with user** before touching any model cache |
| 🟡 **Trade-off / Caution** | Active IDE Indexes | JetBrains `caches/`, active workspace AST stores | **High** (Causes prolonged 100% CPU re-indexing) | **Preserve** unless corrupted |
| 🔴 **Strict Protected** | Credential Stores | Tool credentials, `.env`, local certificates | Irreplaceable | **NEVER touch** |

---

## 2. Toolchain Governance

### Rust Toolchain Version Stacking
* **Inspection**:
  ```bash
  rustup toolchain list
  ```
* **Strategy**:
  * Keep the active default (e.g., `stable-aarch64-apple-darwin`).
  * Remove legacy point-releases:
    ```bash
    rustup toolchain uninstall <old-toolchain-name>
    ```

### Package Manager Store Deduplication
* **npm**: `npm cache clean --force`
* **bun**: `bun pm cache rm`
* **pnpm**: `pnpm store prune` (removes only unreferenced packages from the global content-addressable store)
* **yarn**: `yarn cache clean`
* **uv / pip**: `uv cache clean` / `pip cache purge`
