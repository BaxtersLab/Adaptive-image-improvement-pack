# DEVNOTES — Adaptive Image Improvement Pack
> Carry this file into every future session. It is the handoff document.

---

## Current Status: BUG FIXES APPLIED — AWAITING FIRST TEST

Session 1 (2026-05-18) fixed four crash-level bugs in NexaPopupLoaderNode and two minor issues. The Nexa integration nodes depend on the external `nexa` CLI being installed. The arbiter and mutator nodes are stubs.

---

## What This Pack Does

Audio tag extraction pipeline with a browser-based dual-chat GUI for comparing two Nexa AI model responses side by side. Despite the repo name ("image improvement"), all nodes operate on audio and text.

Seven nodes:

| Key | Display | Purpose |
|---|---|---|
| `AIP_NexaTagAwarePopupLoader` | Nexa Tag-Aware Chat GUI | Launch local HTTP server + open browser dual-chat UI with audio tags injected into context |
| `AIP_NexaComparisonReader` | Nexa Response Comparison Reader | Read latest comparison result from `comparison_results.jsonl` |
| `AIP_AudioTagExtractorA` | Audio Tag Extractor A | Extract semantic tags (instruments, structure, vocals) via `nexa run audiosemantic` |
| `AIP_AudioTagExtractorB` | Audio Tag Extractor B | Extract style tags (genre, production, texture, mood) via `nexa run audiostyle` |
| `AIP_AudioImprovementArbiter` | Audio Improvement Arbiter | Combine semantic + style tags (stub) |
| `AIP_AudioPromptMutator` | Audio Prompt Mutator | Mutate tag string into prompt (stub) |
| `AIP_AudioLogger` | Audio Logger | Print log data to console |

---

## What Changed (Session 1 — 2026-05-18)

| File | Change |
|---|---|
| `nodes/NexaPopupLoaderNode.py` | **Fixed duplicate `do_GET`** — second definition called `super().do_GET()` which returns HTTP 501, so the main HTML page was never served. Merged into one method that routes `/tags` to JSON handler, everything else to HTML page. |
| `nodes/NexaPopupLoaderNode.py` | **Fixed duplicate `handle_chat`** — first definition was dead code, shadowed by the second. Removed the first (weaker) one. |
| `nodes/NexaPopupLoaderNode.py` | **Added `LocalGUIServer.url()`** — `run_gui` called `server.url()` which didn't exist, crashing on every execution. Added `url()` returning `f"http://{self.host}:{self.port}"`. |
| `nodes/NexaPopupLoaderNode.py` | **Fixed `restart()` deadlock** — held `self._lock` and then called `stop()` and `start()` which also try to acquire `self._lock` → deadlock. Removed the `with self._lock:` wrapper from `restart()`; each callee manages its own lock. |
| `nodes/NexaPopupLoaderNode.py` | **Fixed `_captured_responses` init** — was initialized inside a method using `if '_captured_responses' not in globals()`. Moved to module-level declaration. Removed the stale `import json` / `import time` lines that were inside `capture_response` (both already imported at top of file). |
| `nodes/AudioLoggerNode.py` | Added `OUTPUT_NODE = True` — side-effect node with no outputs would be skipped by ComfyUI if its outputs were unconnected. |
| `__init__.py` (root) | Added `AIP_` prefix to all 7 node keys to prevent collision in the global ComfyUI node registry. |
| `DEVNOTES.md` | Created this file. |

---

## Known Issues / What Still Needs Doing

### Nexa CLI dependency (Priority 1)

`AudioTagExtractorNodeA/B` and `NexaTagAwarePopupLoaderNode` all call the `nexa` CLI via `subprocess.run(['nexa', 'run', ...])`. This requires the Nexa SDK to be installed separately (`pip install nexaai` or similar). It is not listed in `requirements.txt` because it's not on PyPI under that name. Add installation instructions to README.

### AudioImprovementArbiterNode is a stub (Priority 2)

`arbitrate()` returns `f"improved: {semantic_tags} + {style_tags}"`. Intended behavior is to intelligently merge/prioritize the two tag streams. Implement using string processing, an LLM call, or rule-based logic.

### AudioPromptMutatorNode is a stub (Priority 2)

`mutate()` returns `f"mutated: {tags}"`. Intended to transform audio tags into a generation-ready prompt. Implement with a template or LLM-based expansion.

### NexaComparisonReader reads from CWD (Priority 2)

`comparison_results.jsonl` is read from the current working directory. This is fragile — depends on where ComfyUI was launched from. Should be anchored to `folder_paths.get_output_directory()` or a configured path.

### requirements.txt lists unused packages (Priority 3)

`tkinterdnd2` and `opencv-python` are listed but not imported anywhere in the codebase. Remove them to avoid confusion. Actual hard dependencies: `requests` (used in NexaPopupLoaderNode imports, though only indirectly via the file).

### `comparison_results.jsonl` never written (Priority 2)

`NexaComparisonReaderNode` reads from `comparison_results.jsonl` but nothing in this pack writes to it. The `capture_response` method stores data in the in-process `_captured_responses` dict. Either write captured responses to the JSONL file, or update `NexaComparisonReaderNode` to read from `_captured_responses` directly.

---

## Node Key Names

| Key (workflow JSON `type` field) | Display name |
|---|---|
| `AIP_NexaTagAwarePopupLoader` | Nexa Tag-Aware Chat GUI |
| `AIP_NexaComparisonReader` | Nexa Response Comparison Reader |
| `AIP_AudioTagExtractorA` | Audio Tag Extractor A |
| `AIP_AudioTagExtractorB` | Audio Tag Extractor B |
| `AIP_AudioImprovementArbiter` | Audio Improvement Arbiter |
| `AIP_AudioPromptMutator` | Audio Prompt Mutator |
| `AIP_AudioLogger` | Audio Logger |

---

## Session Log

| Date | What happened |
|---|---|
| 2026-01-20 | Initial build. Dual-chat browser GUI concept, Nexa CLI integration. Four crash-level bugs present. |
| 2026-05-18 | Fixed duplicate do_GET, duplicate handle_chat, missing url(), restart() deadlock, _captured_responses init. Added OUTPUT_NODE, AIP_ prefix. |
