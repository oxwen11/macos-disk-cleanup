# Strategy: Browsers & On-Device ML Model Bloat

Modern desktop browsers and Electron tools increasingly ship with or download on-device AI models and heavy graphics shader caches that bypass standard browser cache-clearing dialogs.

---

## 1. Waste Mechanisms & Heuristics

### A. Chrome / Edge On-Device Model Downloads
* **Mechanism**: Feature packs like Gemini Nano, smart compose, and page optimization download complete LLM/multimodal weights into user Application Support folders.
* **Heuristic Location**:
  * `~/Library/Application Support/Google/Chrome [Beta]/OptGuideOnDeviceModel/`
  * `~/Library/Application Support/Google/Chrome [Beta]/optimization_guide_model_store/`
* **Typical Impact**: 4–8 GB per browser channel.
* **Safe Optimization Strategy**:
  * Removing `OptGuideOnDeviceModel` and related stores deletes outdated model checkpoints without affecting any user bookmarks, browser history, saved passwords, or login sessions.
  * The browser will automatically pull a fresh version only if the on-device AI feature is explicitly re-invoked.

### B. GPU & Shader Caches
* **Heuristic Location**:
  * `ShaderCache`, `GrShaderCache`, `GraphiteDawnCache` inside Application Support.
* **Safe Optimization Strategy**:
  * Safe to delete. Will be recompiled smoothly by the GPU driver when pages render.

### C. The Strict Profile Invariant (Never Delete User Data)
* **Under NO circumstances delete**:
  * `Default/Cookies`
  * `Default/Bookmarks`
  * `Default/History`
  * `Default/Login Data`
  * `Default/Extensions`
* Restrict cleanup strictly to cache subfolders, model weight stores, and shader stores.
