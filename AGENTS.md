# OmniDraw Agent Working Guidelines

This repository combines **Ponytail (Minimalist Senior Dev Discipline)** for software engineering and **Academic Research Skills (ARS)** for scientific research and publication.

---

## 1. Engineering Discipline (Ponytail)
*Channels the mindset of the laziest, most pragmatic senior developer: "The best code is the code you never wrote."*

### The 7-Rung YAGNI Ladder (Ascend before writing any code):
1. **Does this need to exist at all?** (YAGNI) — If speculative or unnecessary, skip it.
2. **Already in this codebase?** — Reuse existing helpers, utilities, and components.
3. **Does the standard library do it?** — Use built-in standard library functions.
4. **Does a native platform feature cover it?** — Native HTML/CSS/browser APIs before JavaScript libraries, database constraints over application loops.
5. **Does an already-installed dependency solve it?** — Never add a new package when existing ones or a few lines suffice.
6. **Can it be one line?** — Make it one line.
7. **Only then:** Write the minimum necessary code that works.

### Engineering Rules:
- **Root-Cause Bug Fixing**: Fix bugs at the shared root cause, not symptom patching across callers.
- **Minimal Diffs**: Shortest working diff wins. Deletion over addition. Boring over clever.
- **Zero Unrequested Abstractions**: No factories with one product, no interfaces with one class, no speculative config.
- **Safety & Quality Non-Negotiables**: Never cut security, validation at trust boundaries, data loss prevention, or accessibility.

---

## 2. Scientific & Academic Research Discipline (ARS)
*Channels the rigor of top-tier peer review: "AI is your copilot, not the pilot."*

### Research Guidelines:
- **Zero Citation Hallucination**: Every cited reference must be a real, verifiable publication (via Semantic Scholar, arXiv, DOI). Never guess authors, dates, or venues.
- **Faithful Claims**: Citations must accurately represent what the authors actually discovered.
- **Writing Quality Check**: Strip AI buzzwords, empty qualifiers, and throat-clearing openings. Keep academic prose crisp, precise, and evidence-driven.
- **Peer Review & Devil's Advocate**: Evaluate methodology, threats to validity, baseline fairness, and ablation completeness with constructive skepticism.

---

## 3. Solo vs. Duo Execution Mode Policy

- **Default Execution (Solo Antigravity)**: Antigravity operates 100% autonomously on all tasks (coding, debugging, refactoring, planning, reviewing, testing) using built-in capabilities. Do NOT call the external DeepSeek API (`scripts/deepseek_bridge.py` or any external LLM endpoints).
- **Duo Mode (Dual-Agent Trigger)**: ONLY invoke `scripts/deepseek_bridge.py` (via `plan`, `review`, or `ask`) when the user EXPLICITLY requests it using trigger phrases such as:
  - `"mô hình duo"`
  - `"dùng duo"`
  - `"duo mode"`
  - `"dual-agent"`
- **Strict Budget & Cost Protection**: DeepSeek API incurs monetary costs and is subject to a hard budget cap (`$1.95 USD` in `.deepseek_usage.json`). Never make speculative, background, or unprompted calls to external APIs without explicit user instruction.

