# Zero-Touch Training — Demo Playbook

A working document for live demos and pitch conversations. The goal is to walk a stakeholder from "interesting concept" to "I see the artifact" in under ten minutes, and to give the presenter prepared answers for the objections that always come up.

This document grows. Section 2 (Drift Detection) is complete. Section 3 (Character Swap) is staged for the next demo build.

---

## 1. The Pitch

### The problem we're solving

Enterprise system training is broken in four places, and the buyer already knows all four:

1. **It takes too long to build.** A new SAP module, weapon system interface, or Defense Business System rollout requires three to nine months of training authoring before the first user sees a course. The system is in production before the training is.

2. **It goes stale immediately.** The day a transport lands in production, the training is wrong. Field IDs change, gateways move, approval thresholds get reconfigured. The training authors find out from the help desk tickets, weeks later.

3. **It's authored by the wrong people.** Training authors don't have access to the test scripts, process models, and configuration overlays that define how the system actually behaves. They write from spec documents that were already out of date when handed to them.

4. **It's boring, so nobody completes it.** Click-through SAP courses have completion rates that nobody puts in slide decks. The most common training outcome is "I'll figure it out when I have to do it."

### The reframe

The DBS team already has the assets that define how the system works:
- **Automated test scripts** (Tosca, Selenium, Playwright) — execution truth
- **Process models** (BPMN/Signavio) — semantic truth
- **Configuration overlays** (Opal, customizing tables) — site-specific truth

What if those *were* the training source? What if training was a **compiled artifact** — generated from the same files the test team and process team already maintain, regenerated automatically when those files change, gated through CI just like code?

That's Zero-Touch Training. We don't author training. We compile it.

### The differentiator

The market for system training tooling is mature. SAP Enable Now exists. WalkMe exists. Whatfix, Userlane, UKG's gamified system, all exist. Every one of them is an authoring platform — a fancy editor with templates and analytics. Every one of them has the same fundamental flaw: a human still has to update content when the system changes.

The agility layer — *the system changed → the training updates automatically* — is the gap. Nobody fills it. Drift detection (Layer 6) is what closes it.

### What we'll show

The demo proves three things in sequence:

1. **Layers 1–5 work today.** Five training products generated end-to-end from synthetic but realistic Tosca and BPMN: walkthroughs, video scripts, job aids, WalkMe drafts, process rationales. Plus an interactive React-based trainer with five SAP scenarios and two hardware scenarios.

2. **Layer 6 detects drift in seconds.** When a source asset changes, the system identifies exactly which scenarios are stale, which generated artifacts need regeneration, and emits a CI-gateable report. This is what no commercial product does.

3. **It runs on the buyer's existing pipeline.** No platform to host. No content management system to deploy. A Python CLI the buyer drops into their existing CI/CD — GitHub Actions, GitLab CI, Tosca CI, Jenkins, all the same.

### Build economics (truthful, not aspirational)

| Metric | Actual |
|---|---|
| Total dev hours | ~40–80 hours, off-hours, single contributor |
| API spend to date | <$200 |
| Lines of working code | ~5,000 |
| Working scenarios | 5 software + 2 hardware |
| Per-video generation cost | $3.60 (3-scene POC) to $41.60 (full 13-scene Veo 3) |
| Time to regenerate a full training set after source change | <60 seconds + LLM call time |

These numbers are unusual for the category. They are also the point. If a single person can build this in a basement, a real DBS team with real assets can deploy it in a quarter.

---

## 2. Demo: Drift Detection (Layer 6)

The headline demo. Eight to ten minutes wall-clock. The narrative arc: *training in sync → developer changes a test → training automatically flagged stale → here's exactly what's stale and why → CI gate fails → done.*

### 2.1 Setup (do this once before the demo)

From a clean clone of the repo:

```bash
cd zero-touch-training/poc
pip install -r requirements.txt
python detect_changes.py snapshot
```

Expected output:
```
Capturing baseline snapshot of 4 source files...
  ✓ data/tosca/purchase_requisition.xml → snapshots/...
  ✓ data/tosca/goods_receipt.xml → snapshots/...
  ✓ data/bpmn/purchase_to_pay.xml → snapshots/...
  ✓ data/opal_overlay.yaml → snapshots/...

Baseline captured. Run `python detect_changes.py check` after source changes.
```

The snapshots are committed to the repo. They represent the "current sync point" — the last known-good state of source assets relative to generated training. In a buyer's environment, snapshots are updated whenever the team accepts that the system and training are in sync.

### 2.2 The narrative

What you say while you're sharing the screen, in order. Read it aloud once before the demo so the timing feels natural; cue cards in italics.

> *Open `docs/drift-detection-demo.md` or just talk over the terminal.*
>
> "Training-as-Code makes a specific claim: when the system changes, the training knows. Let me show you what that actually looks like.
>
> First, here's the current state — five SAP scenarios, two hardware scenarios, all generated from these four source files." *Show `poc/config.yaml` sources block.*
>
> "These are the kinds of files your team already has. Tosca test scripts that drive your regression suite. BPMN process models from Signavio. The overlay file that captures the site-specific configuration. We don't author training. We point at these files and compile training from them.
>
> Now — say a developer on your SAP team changes one of these tests. Maybe the Fiori shell got upgraded and the search box has a new ID. Watch."

### 2.3 The drift demo

Show the current state is clean:

```bash
python detect_changes.py status
```

Then check — clean:

```bash
python detect_changes.py check
echo "Exit code: $?"
```

Expected:
```
Drift report written to output/drift_report.json and output/drift_report.md
  ✓ No drift detected. All training assets in sync with sources.
Exit code: 0
```

> "Exit zero. Everything in sync. Now I'll change one thing in one Tosca file — exactly the kind of change a developer would make after a Fiori upgrade."

Make the change live. Open `poc/data/tosca/goods_receipt.xml` in the editor.
Two lines need to change inside STEP_002 — they're at **lines 47 and 50** specifically (there are several other "Post Goods Receipt" matches in the file; do not let your editor's find-next jump to those):

```diff
  47:          <Identifier>id://searchInput</Identifier>
+ 47:          <Identifier>id://globalSearchField</Identifier>
```

```diff
  50:        <Value>Post Goods Receipt</Value>
+ 50:        <Value>MIGO</Value>
```

If you'd rather not edit live (or if your editor jumps to the wrong line), use this one-liner — it targets line numbers exactly:

```bash
cp data/tosca/goods_receipt.xml /tmp/gr_backup.xml
sed -i.bak '47s|id://searchInput|id://globalSearchField|; 50s|<Value>Post Goods Receipt</Value>|<Value>MIGO</Value>|' data/tosca/goods_receipt.xml
```

Then run the check:

```bash
python detect_changes.py check
echo "Exit code: $?"
```

Expected:
```
Drift report written to output/drift_report.json and output/drift_report.md
  ⚠  Drift detected in 1 source(s).
     Stale scenarios: hazmat, regulated_pharma, sedc_goods_receipt, serialized, standard_dry
     Stale artifacts: goods_receipt
Exit code: 1
```

> "Exit one. That non-zero is what makes this work in CI — your pipeline gates on it. The build fails until the team explicitly accepts the new state. No silent drift. Now let's look at *why* it's stale."

Open `poc/output/drift_report.md` and read aloud:

> "One source changed. Inside that source, exactly one step — STEP_002. Two fields modified — element_id and value. Five scenarios are now stale, and one generated artifact bundle. The system isn't guessing. It parsed both versions, diffed the structural fingerprint, and traced the dependency graph through the scenario deps file."

### 2.4 The reset

Restore the original file (from git, the `/tmp/gr_backup.xml` you copied above, or your editor's undo). Run check again:

```bash
# If you used the sed one-liner:
mv /tmp/gr_backup.xml data/tosca/goods_receipt.xml
rm -f data/tosca/goods_receipt.xml.bak

# Or just:
git checkout data/tosca/goods_receipt.xml

python detect_changes.py check
```

Expected: clean, exit 0.

> "Back in sync. In a real workflow, this is what happens after the team regenerates and accepts the new training state."

### 2.5 The CI integration moment

Open `poc/ci_examples/training-drift.yml`.

> "And here's what it looks like in your CI. Push or PR touches a Tosca, BPMN, or overlay file → workflow runs → drift check executes → report uploaded as artifact → comment posted on the PR with the affected scenarios → build fails until resolved.
>
> There's also a scheduled scan — runs nightly — that catches drift introduced by upstream merges into long-lived branches.
>
> The auto-regenerate step is commented out intentionally. Most teams want a human gate the first six months. Flip that comment when the team is ready."

### 2.6 Total demo time

| Beat | Time |
|---|---|
| Setup explanation (config.yaml, sources) | 90 sec |
| Status + clean check | 30 sec |
| Make the source change | 60 sec |
| Run check, walk through report | 2 min |
| Reset, demonstrate CI workflow YAML | 2 min |
| Q&A buffer | rest |

Eight minutes if the audience is quiet. Ten if they're engaged.

### 2.7 What this demo specifically proves

Map each beat to the underlying business claim. When a stakeholder pushes back on a slide later, this is the evidence:

| Claim | Demo evidence |
|---|---|
| "Training stays in sync with the system" | The check command identifies stale scenarios within seconds of a source change |
| "Drops into your existing pipeline" | The CI YAML is 113 lines of standard GitHub Actions; nothing custom |
| "We don't author training" | All five SAP scenarios + the GR artifact bundle are flagged automatically — no human decided that |
| "Granular enough to be useful" | The report names the specific step and the specific fields changed, not "something changed" |
| "Auditable" | JSON + Markdown reports, both checked into CI artifacts; full diff trail |

---

## 3. Demo: Character Swap (placeholder — to be expanded)

> Status: planned. This section will document the parameter-driven swap between the Bigfoot character cast and the blue-collar warehouse worker character, including:
> - Why the same script renders in both styles (cost-as-value-prop, not character-as-gimmick)
> - The swap command and side-by-side video output
> - How to handle the in-room "this is goofy" objection in real time
> - Cost comparison: $3.60 POC cut in either character set
>
> Build target: alongside Phase 2 development.

---

## 4. Talking Points & Objections

The questions you will be asked, and concise answers calibrated to defense and enterprise audiences. These are not slogans — they're prepared answers that match what the demo actually shows.

### "Don't we already have CI that catches breaking changes?"

Yours catches functional regressions. The Tosca run fails when the system breaks. It does not flag that *training* is now out of date. That's a different signal — it's "the system still works, but what we taught users no longer matches what they see." Drift detection is that second signal. Your CI gate is for code; this is the CI gate for training.

### "How is this different from SAP Enable Now / WalkMe / Whatfix?"

Those are authoring platforms. They have an editor, templates, an analytics dashboard, and they assume a human keeps content current. This isn't an authoring platform — it's a generator. The training never existed as an authored document; it was compiled from the test scripts. When the test scripts change, recompile. Compare to: "Word document of API documentation" vs. "OpenAPI spec auto-rendered to a docs site." Same pattern, different layer.

### "How do we trust AI-generated training?"

Three gates, all configurable:
1. **Drift detection runs first** and tells the team exactly what changed and why. No regeneration runs against a black-box change.
2. **Human review on regenerate** — the workflow YAML stages auto-regenerate, but the team enables it explicitly. Default state is "regenerate on demand, gated by review."
3. **SME validation cycle** in Phase 1 establishes the accuracy baseline; subsequent regenerations are deltas against an SME-approved version.

The AI doesn't write training that goes to users without a human in the loop. The AI writes the *first draft* and identifies *what changed.* Humans approve.

### "What about classified environments / GovCloud / RMF?"

The drift detection logic is plain Python with no external calls. It runs anywhere. The LLM step is separate and pluggable — Anthropic API, self-hosted Claude, or any other LLM endpoint your environment authorizes. We're not bringing in a new ATO surface; we're a Python script that emits artifacts.

### "What if our test scripts aren't structured the way your parser expects?"

Then we adapt the parser. The parsers are 300–400 lines each, isolated to two files, and any structured XML or JSON test format can be supported. The hard work is the architecture, not the parser. We've handled namespaced and plain Tosca XML in the PoC; Selenium and Playwright are next-easiest because they're already structured.

### "Won't this over-flag?"

Today, yes — the deps file maps each scenario to the *whole* Tosca file rather than to specific steps. A change in a hazmat-only step would flag the standard_dry scenario as stale. That's a Phase 2 refinement: per-step deps, so the map is finer-grained. The reason we haven't done it yet is that premature precision against synthetic data is worse than honest coarseness against real data. Once we point at your real Tosca files, we calibrate the deps to your scenario coverage.

### "What scale does this support?"

The drift check is O(n) in source files and O(steps) within each source. Hundreds of sources and tens of thousands of steps run in single-digit seconds. The bottleneck at scale is not detection — it's SME review of regenerated content. Which is exactly the bottleneck you have today, except the work is now in the SME's wheelhouse (review accuracy) rather than the trainer's wheelhouse (re-author from scratch).

### "What does this cost to operate?"

Drift detection: zero marginal cost. Pure Python, no LLM calls. Regeneration on drift: dollars per full training set at current Anthropic API pricing. The Bigfoot/character-swap video pipeline runs $3.60 for a 3-scene POC up to $41.60 for a 13-scene full Veo 3 render. For comparison, contracted training authoring runs $50–$250/hour at three to twelve months per major process.

### "Who owns it after Phase 4?"

Your operations team. The whole point of Phase 4 (Operationalize) is handoff. The system is a Python codebase, a YAML deps file, and a CI workflow. There's no proprietary platform, no vendor lock-in. The team that maintains the test automation can maintain this in the same workflow.

### "What are you not telling us?"

What's currently synthetic and needs to be validated against real data:
- Tosca samples are realistic but constructed. Has not been validated against a real DBS Tosca repo.
- BPMN samples are realistic but constructed. Same.
- The five SAP scenarios use plausible but fictional sites (GlobalMart, Cardinal Health DC, etc.). Real Anniston/site data has not been integrated.
- SME accuracy validation has not yet been completed — that's the immediate next step on the customer side.

What's working today, no caveats:
- The pipeline runs end-to-end, parses, generates, renders, and regenerates.
- Drift detection works as demoed.
- Both video pipelines (DALL-E 3 and Veo 3) produce real output at the stated cost.
- The React trainer engine handles all seven scenarios with no engine-level branching.

The synthetic-data question is the honest one to flag early. Don't wait for them to ask.

---

## 5. The Decision the Buyer Is Making

After the demo, the buyer is choosing between three paths. Help them name the path they want.

### Path A: Status quo

Keep doing what they're doing. Authored training, manual updates, six-to-nine month build cycles, drift handled reactively when help-desk tickets spike. Cost is hidden in headcount and rework.

### Path B: Buy a commercial authoring platform

SAP Enable Now, WalkMe, or Whatfix. Faster authoring, better analytics, still requires a human to keep content current when the system changes. Reduces some pain, doesn't address drift.

### Path C: Compile training from existing assets

What we just demoed. The agility layer. Training as a CI-gated artifact of the same source files the test and process teams already maintain. Highest infrastructure investment up front (small, but real); lowest sustaining cost; only path that closes the drift gap.

The buyer almost never picks A and B exclusively. The realistic decision is "C plus an authoring overlay (B) for content that doesn't have source assets." That's fine. Suggest it before they have to.

---

## 6. After the Demo

Follow-up artifacts to leave with the stakeholder:

- This document (`docs/drift-detection-demo.md`)
- The executive summary (`docs/Zero-Touch-Training-Executive-Summary.docx`)
- The roadmap (`docs/roadmap.md`)
- A link to the GitHub repo with the specific commit they just saw

Concrete asks to consider, depending on the level of the stakeholder:

- **Technical stakeholder:** "Can we get one real Tosca file from your environment, run our parser against it, and report back?"
- **Program-office stakeholder:** "What's the right contracting vehicle for a 90-day pilot — SBIR Phase II, OTA, or CSO?"
- **Training-lead stakeholder:** "Who's the right SME to validate the SE-DC Goods Receipt scenario? Thirty minutes, recorded, written up."

If the stakeholder isn't ready for any of those, the next-best ask is the smallest possible: "Who else should see this?"

---

## Appendix A: Demo Failure Modes & Recovery

What can go wrong during the demo and how to handle it on stage.

| Failure | Recovery |
|---|---|
| `python detect_changes.py snapshot` shows missing files | You forgot to `cd poc/`. Common. Just `cd poc/` and rerun. |
| Editor doesn't show the right lines for STEP_002 | Use `grep -n "STEP_002" data/tosca/goods_receipt.xml` first to find the line range. |
| Check passes when you expected drift | You didn't save the file in the editor. Save and rerun. |
| Audience asks for the live regenerate | Be honest: "Regeneration calls the LLM and takes 30–90 seconds; happy to run it after Q&A or send the output. The drift detection itself is the demoable piece." |
| Network/API issue mid-demo | Drift detection has zero network calls — should never fail for connectivity reasons. If it does, you have a code problem, not a network problem. |

---

## Appendix B: Document Change Log

| Date | Section | Change |
|---|---|---|
| 2026-05-01 | Initial | Sections 1, 2, 4, 5, 6 + appendices written. Section 3 (character swap) staged. |
