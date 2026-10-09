# Strategy: System Cleaners, Downloads & Ghost Residues

This guide covers system-level maintenance with Mole CLI, safe downloads segregation, and cautious detection of orphaned application leftovers.

---

## 1. System Cleaners (Mole CLI) Strategy

`mole` (`/opt/homebrew/bin/mole` or `brew install mole`) is a high-performance macOS optimization CLI with built-in whitelisting for developer workflows (Surge, Playwright, Ollama, Gradle, JetBrains).

### Safe Invocation:
1. **Preview First (`--dry-run`)**:
   ```bash
   mole clean --dry-run
   ```
2. **Execute User-Level Cleanup**:
   ```bash
   echo "y" | mole clean
   ```
   * *Reclaims*: User app caches (`~/Library/Caches`), system & application logs (`~/Library/Logs`), Trash (`~/.Trash`), package manager temporary buffers, and old agent CLI binary duplicates.

---

## 2. Downloads Directory Asset Segregation

Developer download directories mix transient installers with active personal work products. Never purge `~/Downloads` wholesale.

### The Segregation Matrix:
| Class | Target Extensions | Treatment |
| :--- | :--- | :--- |
| **Disposable Installers** | `.dmg`, `.pkg`, `.zip` (containing `.app`), `.tar.gz` (binaries), `.exe` | Enumerate explicitly, present file table with sizes/dates, delete upon user confirmation |
| **Protected Assets** | `.pdf`, `.docx`, `.xlsx`, `.png`, `.jpg`, `.mp4`, `.mov`, `.md`, `.txt` | **NEVER bulk delete.** Keep intact under all circumstances |

Always display the exact installer table before deleting so the user can retain specific offline installation media.

---

## 3. The Root-Owned Trash Pitfall (`~/.Trash`)

When emptying Trash via CLI (`rm -rf ~/.Trash/*`), operations may fail with `Permission denied`.
* **The Root Cause**: Applications or packages originally installed via PKG installers or system helpers (e.g. Remote Desktop, hypervisors) often retain files owned by `root:wheel` when moved to Trash.
* **The Protocol**:
  * Clean user-owned trash items via standard CLI commands.
  * For remaining root-owned application bundles, **do not prompt for risky `sudo rm`**.
  * Instruct the user to perform standard macOS Finder "Empty Trash" (which triggers native macOS Touch ID / admin password elevation securely).

---

## 3. Orphaned App Residue (Ghost Residue) Detection — Advisory Only

When macOS applications are deleted via drag-to-trash, data in `~/Library/Application Support` and `~/Library/Caches` frequently remains orphaned.

### ⚠️ Critical Developer Caveat: The CLI / Headless Trap
**Never implement blind name-matching deletion.**
On developer machines, dozens of critical command-line tools, background daemons, Python libraries, and utilities store configuration and state in `~/Library/Application Support` without ever having a corresponding GUI application bundle in `/Applications`.

### Safe Advisory Workflow:
1. Identify heavy folders (>1GB) under `~/Library/Application Support/`.
2. Check if the folder represents a known GUI application name that was previously installed and deleted.
3. **Strict Gate**:
   * Do NOT flag folders known to belong to CLI tools (e.g. `uv`, `cargo`, `docker`, `git`, `homebrew`, `node`, `pnpm`).
   * Check `ps aux` to ensure no active process or daemon is attached to the directory.
   * **Present as an interactive advisory question**:
     > *"Found ~/Library/Application Support/<App> consuming X GB. If you have permanently uninstalled this application, its remaining support files can be safely removed. Would you like to keep or delete this folder?"*
