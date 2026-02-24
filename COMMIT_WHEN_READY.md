# Pending Commits — Run in iTerm2 When .md Files Are Unlocked

Close any open .md files in your editor first (DEVELOPER_SUMMARY.md,
README.md, docs/layers/*.md), then run these commands.

---

## Commit 1 — Enhanced video renderers

```bash
git add poc/generators/video_render_v2.py
git add poc/generators/video_render_bigfoot.py
git commit -m "$(cat <<'EOF'
Add enhanced video renderers (v2 + Bigfoot)

video_render_v2.py — sandbox-runnable, zero external API cost
  - ffmpeg libflite TTS narration per slide (slt voice)
  - xfade crossfade + acrossfade audio chain between all 15 slides
  - Ambient Am-F-C-G background music synthesized with numpy
  - Improved slide designs: progress dots, card layouts, section
    colour-coding, stats cards, soundbite quote styling
  - Path fixed to use Path(__file__) — runs on Mac and in sandbox
  - Output: 720x1280, 12fps, H.264, ~105s, ~4MB

video_render_bigfoot.py — runs locally on Mac with OpenAI key
  - DALL-E 3 (1024x1792 portrait) cinematic scene image per slide
  - OpenAI TTS tts-1-hd / nova voice narration per slide
  - Pillow overlay: headline, bullets, gradient, ZTT watermark
    composited over each DALL-E image
  - xfade + acrossfade + numpy music assembly (same as v2)
  - Auto-loads OPENAI_API_KEY from env or poc/.env
  - Estimated cost: ~$0.90 per full video run (15 images + TTS)
  - Usage: OPENAI_API_KEY=sk-... python3 video_render_bigfoot.py

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>
EOF
)"
```

---

## Commit 2 — Layer 5: Process Rationale & Consequence

```bash
git add docs/layers/layer-5-process-rationale.md
git add poc/data/consequences.yaml
git add poc/prompts/process_rationale.txt
git add poc/generators/process_rationale.py
git commit -m "$(cat <<'EOF'
Add Layer 5: Process Rationale & Consequence

New training layer addressing the institutional knowledge gap: users
who know HOW to execute a process but not WHY it is designed that way,
when to use it versus alternatives, and what breaks downstream if they
choose incorrectly.

docs/layers/layer-5-process-rationale.md
  - Full layer specification and design rationale
  - Content structure: decision map, anti-pattern gallery,
    consequence matrix, compliance context
  - Source asset requirements and generation approach
  - SME review requirements (higher bar than Layers 1-4)
  - Renumbers former Layer 5 (drift) to Layer 6

poc/data/consequences.yaml
  - New data file: per-process anti-patterns, consequence mappings,
    and compliance context (source of truth for Layer 5 generation)
  - Fully documented example: Goods Receipt against PO
    - Anti-patterns: free GR without PO, wrong movement type (103),
      wrong storage location — each with empathetic explanation,
      immediate/downstream consequences, and recovery steps
  - Second example: Purchase Requisition / unauthorized verbal PO
  - Schema designed for extensibility: add processes as needed

poc/prompts/process_rationale.txt
  - AI prompt template for Layer 5 generation
  - Instructs Claude to write with empathy (not blame)
  - Enforces four-section output: decision map, anti-patterns,
    compliance story, quick reference card
  - Style guidance: no "simply/just", active voice, plain language

poc/generators/process_rationale.py
  - ProcessRationaleGenerator class extending BaseGenerator
  - Loads consequences.yaml, BPMN gateways, Tosca test cases,
    Opal overlay site constraints
  - generate_for_process() and generate_all() methods
  - Adds SME review header to every output file
  - Integrates with existing pipeline (run.py --layer 5)

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>
EOF
)"
```

---

## Also update concept.md — add this section before "Pilot Approach"

Open docs/concept.md and add after the Layer 4 section:

```markdown
### Layer 5 — Process Rationale & Consequence

**Goal:** "I understand *why* we do it this way."

Training that addresses the institutional knowledge gap: people who know
how to execute a process but not why it is designed that way, when to use
it versus alternatives, and what breaks if they choose incorrectly.

- Decision maps: when to use this process vs. similar alternatives
- Anti-pattern gallery: common wrong approaches with empathetic explanation
  of why they feel right and what actually breaks downstream
- Consequence matrix: who notices, when, and what the audit/operational impact is
- Compliance context: the business control the process enforces and what
  an auditor looks for in the transaction record

Sourced from: BPMN decision gateways, Tosca negative test cases, Opal overlay
validation rules, and a new `consequences.yaml` data file maintained by the
SME team.

SME review and Finance/Compliance sign-off required before publication.
```

Also update the numbered list at the top (Layer 5 was "Continuous Update"):
- Layer 5 → Process Rationale & Consequence (new)
- Layer 6 → Continuous Update & Drift Control (renumbered)

---

## Also update DEVELOPER_SUMMARY.md — add this section after Step 5 (Video)

```markdown
## Step 6 — Layer 5: Process Rationale & Consequence

New training layer and generator for consequence-based learning.

### New files

| File | Purpose |
|---|---|
| `docs/layers/layer-5-process-rationale.md` | Full layer specification |
| `poc/data/consequences.yaml` | Anti-patterns, consequences, compliance context |
| `poc/prompts/process_rationale.txt` | AI prompt template |
| `poc/generators/process_rationale.py` | Generator class |

### Running Layer 5

```bash
python3 poc/run.py --layer 5
```

Or with the full pipeline:

```bash
python3 poc/run.py
```

### Adding new processes

Edit `poc/data/consequences.yaml`. For each process add:
- `anti_patterns` — wrong approaches with empathetic framing
- `consequences` — per-category impact (financial, audit, operational, cold_chain)
- `compliance` — regulation, control name, audit question

Every generated output includes a `<!-- SME REVIEW REQUIRED -->` header.
Finance/Compliance sign-off is required before any Layer 5 content is published.
```
