# Strategy: System Cleaners (Mole CLI) & Downloads Filtering

This reference covers safe system-level and user cache purges using native tools like Mole CLI, alongside automated discrimination between disposable software installers and protected user files.

---

## 1. System Cleaners (Mole CLI) Strategy

`mole` (Homebrew formula: `brew install mole` or `/opt/homebrew/bin/mole`) is a high-performance macOS optimization CLI with built-in whitelisting for critical developer services.

### Safe Mole Invocation:
1. **Preview First (`--dry-run`)**:
   ```bash
   mole clean --dry-run
   ```
   * Verifies that whitelists (Surge, Playwright, Ollama, Gradle, JetBrains, etc.) are active.
2. **Execute User-Level Cleanup**:
   ```bash
   echo "y" | mole clean
   ```
   * Automatically reclaims:
     * User app caches (`~/Library/Caches`)
     * System & application logs (`~/Library/Logs`)
     * Emptying Trash (`~/.Trash`)
     * Temporary developer caches (npm, bun, pip, uv, clang)
     * Superseded Cursor Agent CLI versions

---

## 2. Downloads Directory Asset Segregation

Never delete `~/Downloads` wholesale. Developer download directories mix transient installers with active personal work products.

### The Segregation Strategy:
Scan and classify every item by extension and MIME structure:

| Class | Target Extensions | Treatment |
| :--- | :--- | :--- |
| **Disposable Installers** | `.dmg`, `.pkg`, `.zip` containing `.app`, `.tar.gz` with binaries, `.exe` | Enumerate explicitly, present file list with sizes and dates, delete upon confirmation |
| **Protected Assets** | `.pdf`, `.docx`, `.xlsx`, `.png`, `.jpg`, `.mp4`, `.mov`, `.md`, `.txt` | **NEVER** bulk delete. Keep intact under all circumstances |

Always display the exact installer table before deleting so the user can flag any rare offline installer they wish to retain.
