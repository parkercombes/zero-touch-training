# Zero-Touch Training — UX Design Guide

**Version:** 1.0 · April 2026
**Audience:** Design, engineering, product — anyone building or reviewing UX surfaces in this project
**Scope:** Every learner-facing screen in the current PoC build, critically evaluated

---

## Purpose of This Document

This document walks through every UX surface in the Zero-Touch Training platform as it exists today, explains the design rationale behind each decision, and flags anywhere the rationale is weak, missing, or contradicted by the implementation. If a design choice cannot be defended on its own terms, this document says so and provides a recommendation.

This is not a style guide. It is not a component library. It is the design argument for the product — the "why" layer that sits between the code and the user's experience. If something here doesn't hold up under scrutiny, it shouldn't ship.

---

## Design Context

The platform trains warehouse workers to use SAP and perform hands-on procedures (firearms maintenance, vehicle service) through an interactive click-through simulation. Learners click directly on screenshots of real software or photos of real equipment. Four difficulty levels progressively remove scaffolding. The audience ranges from day-one warehouse hires to experienced technicians brushing up before a certification.

Two training domains exist: **software** (SAP ERP screens) and **hardware** (physical equipment photos). They share the same game engine but diverge in visual treatment and interaction patterns.

---

## Surface 1: Scenario Selector (index.html)

### What It Does

Landing page. Shows all available training scenarios as cards, grouped by domain (Software / Hardware). The learner picks a scenario to enter.

### Design Decisions

**Domain grouping with section headers.** Software scenarios appear under "Software Training" and hardware under "Hardware Training." This is justified — the two domains use different visual languages, different annotation styles, and different learning objectives. A flat mixed list would force learners to parse the difference themselves.

**Domain-colored left stripe on each card.** Blue (#0070F2) for software, orange (#FF8C00) for hardware. This works because the stripe color is redundant with the section header — it reinforces the grouping without relying on the learner to decode it. A color-only signal without the header would fail. The current pairing is self-evident and needs no legend.

**Difficulty sort within domain.** Cards within each section are sorted beginner → intermediate → advanced. This is correct. A new learner scanning the page top-to-bottom encounters the simplest scenario first. No action needed.

**Card content: title, site, role, tags.** Each card shows a title (e.g., "Standard Goods Receipt — SAP MIGO"), a site name, a role, a difficulty badge, and up to four keyword tags. The tags summarize what the scenario covers at a glance. This is dense but justified — the alternative is forcing the learner to open a scenario to learn what's inside.

**⚠ Problem: Titles are still system-centered.** The `ux-design-intent.md` document explicitly calls for task-first learner language — "Receiving a Regular Shipment" instead of "Standard Goods Receipt — SAP MIGO." The current titles violate this principle. The SAP transaction reference is useful for supervisors and trainers, but it should be secondary.

> **Recommendation:** Split the title into a primary label in plain task language and a subtitle in technical language. Example:
> - Primary: **Receiving a Regular Shipment**
> - Subtitle: Standard Goods Receipt — SAP MIGO
>
> This serves both audiences. The technical subtitle can be styled smaller and lower-contrast.

**⚠ Problem: No "Help Now" vs. "Practice" entry mode.** The `ux-design-intent.md` calls for two top-level modes — a quick-reference step-list for someone mid-shift and the full game experience for someone learning. The current build has only the game path. This isn't a bug — the PoC is focused on the game engine — but the design intent exists and the selector page should at minimum reserve space for it.

> **Recommendation:** For PoC: no change needed, but add a comment in `generate_index.py` marking where the mode switch would go. For production: implement the two-mode split as the first interaction on the page, before scenario cards appear.

**⚠ Problem: No situation-based navigation.** The design intent calls for a "What do you have in front of you?" decision tree. The current build presents cards directly. Again, acceptable for PoC scope, but the card-grid approach won't scale past 10-12 scenarios without becoming a wall of options.

> **Recommendation:** Defer to production. The card grid works at the current 7-scenario scale. Flag for redesign when scenario count exceeds 12.

**Page subtitle copy.** "Each scenario has four levels that progressively remove guidance and add pressure. Start with a beginner scenario to learn the flow, then move to specialized handling profiles." This is clear and sets expectations. No change needed.

### Verdict

The selector page is functional and internally consistent at current scale. The two biggest gaps — task-first titles and dual entry modes — are documented design intent that hasn't been implemented yet. Neither blocks the PoC, but both should be addressed before any pilot with real learners.

---

## Surface 2: Level Select

### What It Does

After picking a scenario, the learner chooses one of four difficulty levels. Presented as a vertical stack of four cards, each with a colored left border, level number, level name, and one-sentence description.

### Design Decisions

**Vertical stack layout.** Cards are stacked top-to-bottom, easiest to hardest. This is the correct layout. It creates a natural reading order that matches the intended progression. The previous 2×2 grid treated all four levels as equal options — it didn't communicate sequence. The stack does.

**Colored left border per level.** Green (Explore) → Blue (Guided) → Orange (On Your Own) → Red (Challenge). This color sequence maps to a natural escalation metaphor (cool → warm → hot). The left border is a minimal accent that doesn't overwhelm the card content. Justified.

**Level descriptions.** Each card has a single sentence explaining what that level does:
- Explore: "Learn the screen. No pressure. Click around and see what everything does."
- Guided: "Follow the prompts. Each step is highlighted. Build the right habits."
- On Your Own: "No highlights. Hints cost XP. Wrong clicks show you what would have gone wrong."
- Challenge: "Timer on. No help. Real scenario. Score goes on the board."

These are well-written. They use imperative voice, they're short, and each one names the key differentiator. No change needed.

**Hover interaction: translateX(4px) slide.** On hover, the card slides 4px right and the border/background subtly change. This provides clear interactive affordance on desktop without being distracting.

**⚠ Problem: No touch equivalent for hover.** On a touchscreen (tablet on a warehouse floor), the hover state never triggers. The card is still tappable, but there's no visual feedback that it's interactive until you tap it. This violates the floor-friendly affordance principle.

> **Recommendation:** Add an `:active` state or a tap-triggered visual response (e.g., brief background flash on touchstart). The `onMouseEnter`/`onMouseLeave` approach is desktop-only. Consider adding `onTouchStart`/`onTouchEnd` handlers that apply the same visual shift.

**⚠ Problem: No progress indication.** The `ux-design-intent.md` calls for completed levels to show a checkmark and for the system to guide learners toward the next uncompleted level. The current build shows all four levels as equal, every time. A first-time learner sees four doors with no indication of which one to walk through.

> **Recommendation:** For PoC: add a "Recommended" badge on Level 0 if no localStorage progress exists. For production: implement per-scenario progress tracking and display completed/current/locked states.

**Back link ("← All Scenarios").** Present and correctly positioned. Gives the learner an escape hatch. No change needed.

### Verdict

The vertical stack is a clear improvement over the grid. The descriptions are strong. The two gaps — touch feedback and progress awareness — matter for production but are acceptable in PoC scope.

---

## Surface 3: Briefing Screen

### What It Does

Shown between level select and play. Two-panel layout: left panel has scenario title, briefing text, step list, learning objectives, and a level-specific tip; right panel shows either a 3D exploded view (hardware) or a preview screenshot (software).

### Design Decisions

**Split-panel layout (400px left / flex right).** The left panel is text-heavy (scenario context, procedure overview, objectives, tip, CTA). The right panel is visual (3D model or screenshot). This is a standard briefing layout — text on one side, visual on the other. It works on desktop and large tablets.

**⚠ Problem: Not responsive below ~800px.** The left panel is `flex: 0 0 400px`. On a tablet in portrait mode (~768px viewport), this leaves only 368px for the 3D view, and on a phone it's completely broken. The `ux-design-intent.md` acknowledges warehouse tablets as a primary device class.

> **Recommendation:** Add a breakpoint. Below 800px, stack the panels vertically — visual on top (capped at 40vh), briefing text below with scroll. This is the single highest-impact responsive fix in the entire application.

**Procedure overview (numbered step list).** Shows all N steps of the procedure with their goal text. This gives the learner a mental model of the full workflow before they start. Strong design choice — it reduces the anxiety of not knowing how long the task is or what comes next.

**Learning objectives per level.** Shown in a tinted box matching the level color. These are optional (not all scenarios define them). When present, they set clear success criteria. When absent, the tip text fills the gap adequately.

**Level-specific tip.** An italic gold callout explaining what this specific level feels like. Examples: "Explore mode: Click around freely. No scoring, no pressure." and "Challenge mode: 3-minute timer. No hints. No help. Go." These are excellent — they set emotional expectations, not just mechanical ones.

**"Begin Training →" button.** Styled in the level's color, positioned at the bottom of the left panel. Clear, prominent, and uses the right verb ("Begin" not "Start" or "Play"). Minor nitpick: the `→` arrow is good affordance but the button could be larger on touch devices.

**3D exploded view (hardware only).** An interactive Three.js scene showing the equipment's components in exploded arrangement. The learner can rotate and zoom. This is a strong differentiator for hardware scenarios — it gives spatial context that a flat photo cannot. Auto-explodes after 800ms with a smooth cubic-ease animation.

**⚠ Problem: "Drag to rotate · Scroll to zoom" label at bottom of 3D view.** This instruction uses desktop-centric language. On touch, it should say "Pinch to zoom · Swipe to rotate." The current implementation only handles mouse events (mousedown, mousemove, mouseup, wheel). Touch events are not wired up.

> **Recommendation:** Add touch event handlers (touchstart, touchmove, touchend) with two-finger rotation and pinch-to-zoom. Update the instruction label to be device-aware. If touch support is deferred, at minimum change the label to "Interactive — rotate and zoom the model."

**Software fallback (screenshot preview).** When there's no 3D model, the right panel shows the first step's screenshot. This is acceptable but bland — it's just a static image. The hardware side gets an interactive 3D toy and the software side gets a thumbnail.

> **Recommendation:** Consider showing a scrollable filmstrip of all step screenshots, or an animated crossfade between steps. Even a simple 2-up layout showing the first and last step would communicate the scope of the procedure better than a single static image.

### Verdict

The briefing screen is the strongest-designed surface in the application. The information hierarchy is correct, the content is well-structured, and the 3D view is a genuine differentiator. The responsive layout is the critical gap. Fix that and this screen is production-ready.

---

## Surface 4: HUD (Heads-Up Display)

### What It Does

Fixed top bar during gameplay. Shows: back arrow, scenario title + site, handling profile badge, level badge, step counter, progress bar, XP (L2+), timer (L3), and score.

### Design Decisions

**52px fixed height with backdrop blur.** The HUD is a dark bar with blur, which lets the underlying screenshot peek through slightly at the edges. This is a standard game HUD pattern. The 52px height is minimal enough to not eat too much of the 1280px-wide screenshot below.

**Information density.** The HUD packs 7-9 pieces of information into a single row. On desktop at 1280px+ viewport, this works — there's enough horizontal space. On a narrower viewport, the items will likely wrap or collide.

> **Recommendation:** Set a minimum width on the HUD or implement a condensed mode that drops lower-priority items (handling profile badge, site name) on narrow viewports. The step counter, progress bar, level badge, and score are essential; the rest can be truncated or hidden.

**Handling profile badge.** Shows "standard dry", "hazmat", etc. in a small pill. This is useful context for the learner — it reminds them which scenario variant they're in. Justified.

**Level badge with color coding.** Shows the current level name (EXPLORE, GUIDED, etc.) in the level's color. This is the single strongest orientation cue during gameplay — the learner always knows what mode they're in. Justified.

**Progress bar.** A 200px-wide bar showing completion percentage. Uses the accent color (SAP orange). This is essential — without it, the learner has no sense of how far through the procedure they are. Justified.

**Timer (Level 3 only).** Shows remaining time with escalating urgency colors: default red → amber at 60s → bright red at 30s. The `tabular-nums` font variant prevents the timer from jiggling as digits change width. Both are correct design choices.

**Score display.** Always visible, all levels. On Level 0 (Explore), the score is always 0, which is confusing — why show a score counter in a mode with no scoring?

> **Recommendation:** Hide the score display on Level 0. It sends a mixed signal. Explore mode's entire pitch is "no pressure, no scoring." Showing "Score: 0" undermines that message. Similarly, consider hiding XP on levels that don't award XP.

**Back arrow (← to scenario selector).** Present at far left. This is an essential escape hatch. No change needed, but the tap target is just the `←` character — about 18px wide. That's below the 48px minimum for touch.

> **Recommendation:** Wrap the back arrow in a 48px×48px touch target. The visual can stay small; the hit area should be large.

### Verdict

The HUD works well on desktop. Its information hierarchy is correct — most important items (level, step counter, progress) are most prominent. The three issues are: narrow viewport behavior, score visibility on Level 0, and touch target size on the back arrow. All are fixable without layout changes.

---

## Surface 5: Play Screen — Level 0 (Explore)

### What It Does

Free exploration mode. The learner sees a full screenshot with a dashed green outline around the current target element. They can click anywhere. Clicking the target shows a tooltip confirming what it is. Navigation arrows at the bottom move between steps.

### Design Decisions

**Dashed outline (not solid).** The dashed green outline signals "this is informational, not mandatory." It's visually distinct from the solid orange border used in Level 1 (Guided). This differentiation is important — it tells the learner that Level 0 is low-stakes. Justified.

**"▶ Target element" label above the hotspot.** A small green text label sitting above the dashed outline. This is redundant with the Explore Panel description below, but redundancy is acceptable for orientation — the learner's eyes are on the screenshot, not the panel. Justified.

**Tooltip on click.** When the learner clicks the correct element, a tooltip appears saying "✓ [goal text] — this is the correct element for this step." This gives immediate confirmation without a scoring event. Good feedback design.

**No penalty for wrong clicks.** Clicking anywhere other than the target does nothing — no error message, no visual feedback, no sound. This is correct for Explore mode. Adding negative feedback here would undermine the "no pressure" promise.

**Explore Panel at bottom.** See Surface 6.

**Crosshair cursor.** The play area uses `cursor: crosshair`. This signals that clicking is the primary interaction. However, crosshair has a precision connotation (image editing, map tools) that may feel unfamiliar to warehouse workers.

> **Recommendation:** Consider `cursor: pointer` instead. It's more universally understood as "click here." The crosshair is more honest about the interaction model (you're clicking on a specific pixel region), but the learner doesn't need to know that.

### Verdict

Level 0 is well-designed for its purpose. It's low-pressure, clearly different from the other levels visually, and provides enough guidance to orient the learner without handholding. No critical issues.

---

## Surface 6: Explore Panel (Level 0 Bottom Card)

### What It Does

A bottom-anchored card that shows the current step's goal and detailed element descriptions. Also contains forward/back navigation and a "Done Exploring" exit button.

### Design Decisions

**Bottom anchoring with rounded top corners.** The panel sits flush at the bottom of the viewport and extends upward. This is a standard mobile pattern (bottom sheet) and works well on tablets. Justified.

**Max height 40vh with overflow scroll.** Prevents the panel from covering more than 40% of the screen, even if the step has many element descriptions. This ensures the screenshot above is always at least 60% visible. Justified.

**Element description formatting.** Each description is parsed for an em-dash separator. Text before the dash is styled as a bold orange label (the element name), and text after is the explanation. Example: "**Movement Type** — The SAP code that defines what kind of goods movement this is." This is a smart micro-formatting choice — it makes the descriptions scannable without requiring a full table layout.

**Forward/back navigation with step counter.** "← Prev Screen" and "Next Screen →" with a "1 / 8" counter in between. Clear and minimal. The "Done Exploring" button is set apart with an orange border, signaling that it's a different kind of action (exit) rather than navigation (next/prev).

**⚠ Problem: "Done Exploring" returns to level select, not to Level 1.** The natural next step after exploring is to try Guided mode. Returning to the level select screen adds a click and breaks the flow.

> **Recommendation:** Change "Done Exploring" to "Continue to Guided Mode →" (dispatching `SELECT_LEVEL` with level 1). Keep a secondary "Back to Level Select" option as a text link, not a button. This creates the progressive path that `ux-design-intent.md` calls for.

### Verdict

The Explore Panel is clean and functional. The single issue — exit behavior — is a flow problem, not a design problem. Fixing it requires a one-line dispatch change.

---

## Surface 7: Play Screen — Level 1 (Guided)

### What It Does

Step-by-step guided mode. A dark overlay dims the entire screenshot except for a spotlight cutout around the target element. An orange border and pulsing ellipse draw attention to the click target. A Goal Card at the bottom shows the current objective with a free hint button and a skip option.

### Design Decisions

**Dark overlay (62% opacity) with spotlight cutout.** This is the signature visual of Level 1. It works because it eliminates distraction — the learner's attention is forced to the one element that matters. The 62% opacity is a good balance: dark enough to suppress the background but light enough to maintain context about where on the screen the target sits.

**Orange border around cutout (software only).** For software scenarios, a glowing orange border with `shadowBlur: 18` highlights the cutout edge. This is skipped for hardware scenarios because the PNG screenshots already have baked-in highlight annotations. The `IS_HARDWARE` conditional is a correct domain-aware adaptation.

**Pulsing ellipse animation (software only).** A breathing ellipse animation on the cutout boundary. Again skipped for hardware. The pulse rate (`0.04` radians per frame at 60fps ≈ 2.4s cycle) is slow enough to be noticed without being nauseating. Justified.

**12px padding around hotspot.** The cutout extends 12px beyond the hotspot bounds in each direction. This prevents the spotlight from feeling claustrophobically tight. Justified.

**Auto-hint on wrong click.** If the learner clicks wrong in Level 1, a hint is automatically shown after 400ms. This is the right call for a guided mode — the learner shouldn't have to figure out that they need to click a hint button when they're already lost.

**Skip button.** Allows the learner to advance without clicking the correct element. Earns no points. This is important because a learner might understand the step conceptually but struggle with the exact click target (especially if the hotspot is small or ambiguous). Forcing them to stay stuck would create frustration, not learning.

**⚠ Problem: Feedback for correct clicks is text-only, no visual anchor.** When the learner clicks correctly, a green-tinted full-screen overlay appears with the step's feedback text. But the overlay doesn't point back to the element they just clicked. The spatial relationship between "what I clicked" and "what happened" is lost.

> **Recommendation:** Consider adding a brief visual anchor — a small checkmark or highlight on the clicked element before the feedback overlay appears, or position the feedback text near the clicked element rather than centered on screen. This reinforces spatial memory of where elements are.

### Verdict

Level 1 is the most polished play experience. The spotlight mechanic is effective, the progressive hint system is well-calibrated, and the hardware/software domain split is handled correctly. The feedback anchoring issue is a refinement, not a blocker.

---

## Surface 8: Play Screen — Level 2 (On Your Own)

### What It Does

No spotlight, no highlights. The learner sees the neutral (un-annotated) screenshot and must find the correct element from memory. Hints are available but cost 50 XP with a 10-second delay. Wrong clicks trigger consequence panels explaining what would go wrong in production.

### Design Decisions

**Neutral screenshots.** Level 2 uses `SCREENS_NEUTRAL` instead of `SCREENS`. This means the PNG has no baked-in highlights or annotations. The learner sees exactly what they'd see in the real application. This is the core pedagogical point of Level 2 — transfer from guided to independent performance. Justified.

**Costly hints (−50 XP, 10-second delay).** The XP penalty discourages overuse. The 10-second delay adds friction so the learner has time to try again before the hint appears. This is a well-designed hint economy — it doesn't block hints entirely (which would cause frustration) but it makes them expensive enough that learners will try to work without them.

**Adaptive free hints after 3 consecutive errors.** If the learner gets three wrong clicks in a row, the hint button changes to "Free Hint (struggling)" and the 50 XP cost is waived. This is a compassionate design choice — it prevents the learner from getting stuck in a death spiral where they're losing XP on every click and can never recover. Justified.

**Consequence panels on wrong clicks.** Instead of a simple "wrong" message, Level 2 shows a panel explaining the real-world consequence of the mistake. Header: "Wrong Element" with the target name. Body: "What would happen in production" followed by the consequence text. This is the most valuable learning moment in the entire system — it ties abstract click-accuracy to concrete operational outcomes.

**⚠ Problem: Consequence panel display time is 5 seconds (hardcoded).** Some consequence texts are long and complex (e.g., multi-sentence explanations of compliance violations). Five seconds may not be enough to read them. There's no way for the learner to keep the panel open longer.

> **Recommendation:** Add a "Dismiss" button to consequence panels and only auto-dismiss after the learner clicks it or after 15 seconds (whichever comes first). Alternatively, pause the auto-dismiss timer if the learner is hovering/touching the panel.

**Generic instruction text.** Level 2 replaces the step-specific instruction with "You know this process. Find the right element." This is intentional — withholding the instruction forces recall. But the phrasing assumes the learner has already completed Level 1 for this scenario. If they jumped straight to Level 2, the message is presumptuous.

> **Recommendation:** No change for PoC. In production, if progress tracking exists, adjust the copy based on whether the learner has actually completed Level 1: "You've done this before. Find the right element." vs. "Can you find the right element without guidance?"

### Verdict

Level 2 is where the real learning happens, and the design supports that. The hint economy is well-balanced, the consequence panels are the product's best pedagogical feature, and the adaptive hint system is a smart safety net. The consequence panel timing is the only issue worth fixing now.

---

## Surface 9: Play Screen — Level 3 (Challenge)

### What It Does

Timed run with no hints, no instruction text, and minimal feedback. A narrative premise is shown before play begins. The timer counts down. Wrong clicks show only "Wrong Element" with no consequence detail. The goal is speed and accuracy under pressure.

### Design Decisions

**Narrative screen before play.** A full-screen interstitial shows a randomly selected narrative from the scenario's narrative pool, followed by the briefing text and a "Begin" button. The narrative sets an emotional frame — "you just got a call that..." — to make the challenge feel contextualized rather than arbitrary. This is good game design; it gives the speed run a reason to exist.

**Timer with escalating urgency.** The timer display in the HUD shifts color at 60s and 30s remaining. An audio tick plays in the last 10 seconds. These are standard gamification urgency cues. They work.

**No hints, no instruction text.** The Goal Card shows only the step objective — no instruction, no hint button. This is correct for a challenge mode. Showing help options would undermine the "test yourself" framing.

**Minimal feedback on correct clicks.** Level 3 shows "✓ Correct!" instead of the step-specific feedback text. This is correct — in a timed run, a long feedback message would waste seconds. The learner doesn't need to learn here; they need to perform.

**800ms delay on correct click before advancing.** In Level 3, the delay between a correct click and advancing to the next step is 800ms (vs. 1200ms in L2, 2200ms in L1). The shorter delay matches the urgency of timed play. Justified.

**⚠ Problem: No wrong-click consequence detail in Level 3.** Level 2 shows consequence panels; Level 3 shows only "Wrong Element." This makes sense for pacing, but it means the learner gets less feedback when they need it most (under pressure, making mistakes). The current approach prioritizes speed over learning, which is correct for a challenge mode — but it means Level 3 is a test, not a teaching tool.

> **Recommendation:** No change. This is a deliberate design choice and it's the right one. Level 3 is assessment, not instruction. If the learner needs to learn from their mistakes, they should review the debrief or drop to Level 2.

**⚠ Problem: Timeout message is generic.** "You made it to step X of Y. Try again!" doesn't tell the learner what went wrong or where they lost time. It doesn't differentiate between "you got stuck on one step" and "you were clicking wrong elements everywhere."

> **Recommendation:** Add one line of diagnostic: "You spent the most time on step X: [goal text]." This gives the learner a specific target for improvement on their next attempt. The data is available in the state (stepIdx tells you where they were when time ran out).

### Verdict

Level 3 is clean and purposeful. The narrative framing elevates it beyond a generic speed run. The timeout diagnostic is a low-effort improvement that would make retries more intentional.

---

## Surface 10: Goal Card (Levels 1–3)

### What It Does

Fixed bottom card showing the current step's objective, optional instruction text, hint button (L1–L2), and skip button (L1 only).

### Design Decisions

**"Objective" label above goal text.** An uppercase, letter-spaced label in the accent color. This is a consistent signpost — the learner always knows where to look for what they're supposed to do. Justified.

**Goal text at 17px, 600 weight.** The largest text on the card. This is the primary information the learner needs, and it's sized accordingly. Justified.

**Instruction text at 13px, blue tint.** Secondary information, visually subordinate to the goal. On Level 1, this is the step-specific instruction. On Level 2, it's the generic "You know this process." On Level 3, it's absent entirely. The progressive removal of this text across levels mirrors the progressive removal of scaffolding. Justified.

**Card width: min(680px, 90vw).** This prevents the card from being wider than the screenshot above it on most viewports. On very narrow viewports, the 90vw cap keeps it usable. Justified.

**Background blur (12px).** The card sits over the screenshot and the blur effect makes the text readable without a fully opaque background. The 92% opacity is high enough that contrast is never an issue. Justified.

### Verdict

The Goal Card is well-designed and appropriately minimal. No changes needed.

---

## Surface 11: Feedback Flash

### What It Does

A full-screen overlay that appears momentarily when the learner clicks correctly or incorrectly. Two variants: a simple centered message (correct clicks, L0/L1 wrong clicks) and an elaborated consequence panel (L2+ wrong clicks).

### Design Decisions

**Full-screen tint.** Green tint (25% opacity) for correct, red tint (25% opacity) for wrong. This is a visceral, unmistakable signal. Even in peripheral vision, the learner knows immediately whether they got it right. Justified.

**Simple feedback: centered pill.** A rounded rectangle with a 2px colored border and the feedback text centered inside. Clean, readable, and out of the way quickly (1.2–2s). Justified.

**Consequence panel: bottom-aligned card.** For Level 2+ wrong clicks, the feedback shifts to a structured card with a header ("Wrong Element" + target name) and body ("What would happen in production" + consequence text). The bottom alignment prevents it from covering the area the learner just clicked, maintaining spatial context. Good decision.

**Audio cues on feedback.** Correct clicks play a short ascending sine tone. Wrong clicks play a low square-wave buzz. These are subtle enough to not be startling but distinct enough to register. The audio cue fires before the visual overlay renders, so feedback feels instantaneous. Justified.

### Verdict

The Feedback Flash is one of the best-designed components. It's fast, clear, and the consequence panel variant is genuinely educational. No changes needed.

---

## Surface 12: Debrief Screen

### What It Does

Shown after completing Levels 1 and 2. Lists every step that has a defined consequence, presented as expandable accordion items. The learner clicks each step to reveal "If done wrong: [consequence text]."

### Design Decisions

**Accordion interaction.** The learner actively chooses which steps to review. This is better than a static wall of text — it gives the learner agency over their review and forces them to engage with each step individually. Justified.

**Only steps with consequences.** Steps that don't have a defined consequence are omitted from the debrief. This prevents the list from being cluttered with "nothing bad happens" entries. Justified.

**Shown after L1 and L2, skipped for L0 and L3.** L0 is exploration (no consequences to review). L3 is a timed run (the learner wants to see their score, not review). L1 and L2 are the learning levels where consequence review adds value. This mapping is correct.

**Step number badge in accent color.** Each accordion item shows the step number in a small pill. This maintains the connection between the debrief and the procedure the learner just completed. Justified.

**⚠ Problem: "Why Each Step Matters" heading is good; "Continue →" button is ambiguous.** The button advances to the Win Screen, but the learner might expect it to continue to the next level or replay. The label doesn't say where "Continue" goes.

> **Recommendation:** Change the button label to "See Your Results →" to make the destination clear.

### Verdict

The Debrief Screen is a well-conceived pedagogical feature. The accordion pattern is the right choice for this content. The button label is the only issue.

---

## Surface 13: Win Screen

### What It Does

Completion screen. Shows "Complete!" heading, a level-specific message, stats line, and three action buttons: Play Again, Review (Scrambled), and Change Level.

### Design Decisions

**Level-specific completion messages.** Each level gets a tailored message that points toward the next level:
- L0: "Nice exploring! Ready to try Guided mode?"
- L1: "Tutorial complete! Try 'On Your Own' next."
- L2: "Great work without the safety net! Ready for the Challenge?"
- L3: "[Scenario title] — challenge crushed!"

These are well-written. They celebrate the accomplishment and create forward momentum. Justified.

**Stats line.** Shows level name, score, accuracy (L1+), XP (L2+), and elapsed time (L3 with time remaining). The accuracy formula `max(0, round((total - wrong * 2) / total * 100))` penalizes wrong clicks at 2× weight, which prevents a "spray and pray" strategy from yielding high accuracy. Smart.

**Confetti animation (L2+ only).** 60 DOM elements with CSS `confetti-fall` animation in the level's color palette. Triggered only on Level 2 and above — Explore and Guided don't get confetti because they're low-stakes. The confetti pieces are cleaned up on unmount. This is a proportionate reward — confetti on every completion would dilute its meaning. Justified.

**Three action buttons.** "Play Again" (same level), "Review (Scrambled)" (available L1+), and "Change Level." This gives the learner clear next-step options. The "Review (Scrambled)" button is purple (#6B21A8), visually distinct from the other two, signaling that it's a different kind of activity. Justified.

**⚠ Problem: No direct "Next Level" button.** The completion message suggests the next level ("Ready to try Guided mode?") but the only way to get there is "Change Level" → re-select from the level list. This is a two-click path for what should be a one-click action.

> **Recommendation:** Add a primary "Next Level →" button that advances directly to the briefing screen for level N+1. Make it the most prominent button. "Play Again" and "Change Level" become secondary options. On Level 3 completion, replace "Next Level" with "Change Level" since there's no Level 4.

### Verdict

The Win Screen does its job but misses the opportunity to push learners forward with a single click. The "Next Level" button is the most impactful UX improvement available anywhere in the application — it removes friction from the exact moment where the learner's motivation is highest.

---

## Surface 14: Timeout Screen (Level 3)

### What It Does

Shown when the Level 3 timer reaches zero. Displays "Time's Up!", the step the learner reached, score, XP, and two buttons: Try Again and Change Level.

### Design Decisions

**Red heading, consistent with failure state.** "Time's Up!" in `#ff8080` matches the wrong-click color language. This is correct — timeout is a failure state and should look like one. Justified.

**Step progress indicator.** "You made it to step X of Y." This gives the learner a concrete measure of how close they got. Justified.

**Audio cue (low sawtooth tone).** A buzzy, downward tone that's distinct from the wrong-click sound. The timeout sound is lower and longer, signaling a different kind of failure (ran out of time, not wrong element). Justified.

**No "Review" button.** Unlike the Win Screen, the Timeout Screen doesn't offer a review option. This makes sense — the learner didn't complete the procedure, so there's nothing complete to review. Justified.

### Verdict

Clean and functional. The diagnostic improvement (suggested in Surface 9) would benefit this screen. Otherwise, no changes needed.

---

## Surface 15: Review Mode

### What It Does

An optional mode accessible from the Win Screen (L1+). Takes up to 5 steps from the completed procedure, shuffles their order, and presents them using Level 2 mechanics (neutral screenshots, no spotlight). The learner must find the correct element for each step out of sequence.

### Design Decisions

**Scrambled order.** The core idea: can the learner find elements when they're not following the procedure's natural sequence? This tests spatial memory rather than procedural memory. It's a genuinely clever pedagogical feature — most training systems only test sequential recall.

**Cap at 5 steps.** For procedures with 8+ steps, reviewing all of them would be tedious. Five is enough to test breadth without exhausting the learner. Justified.

**Level 2 mechanics.** Neutral screenshots, no spotlight, no free hints. The review is meant to be challenging. Using L2 mechanics rather than L1 mechanics is the right choice — if the learner just completed L1, reviewing at L1 difficulty would be too easy. Justified.

**Purple badge in HUD.** Review mode has its own color (#6B21A8) in the HUD level badge, visually distinct from all four standard levels. This prevents confusion — the learner knows they're in a special mode, not a regular level. Justified.

**"Review X of 5" counter.** The HUD shows review progress rather than step numbers. This correctly reflects that the review order doesn't match the procedure order. Justified.

### Verdict

Review mode is one of the most thoughtful features in the application. No changes needed.

---

## Surface 16: Audio System

### What It Does

Web Audio API synthesis — no external audio files. Five cue types: correct (ascending sine), wrong (low square), tick (1kHz pip for last 10s of timer), win (ascending four-note arpeggio), timeout (low sawtooth).

### Design Decisions

**Synthesized audio, no external files.** This means the trainer works completely offline with no CDN dependency for audio. Each HTML file is self-contained. Justified for the PoC architecture (standalone HTML files served from local filesystem).

**Distinct timbres per cue type.** Sine for positive feedback, square/sawtooth for negative. This isn't arbitrary — sine waves are perceived as "clean" and "pleasant" while square/sawtooth waves are perceived as "buzzy" and "harsh." The timbre mapping reinforces the feedback semantics. Justified.

**Quiet default gain (0.06–0.15).** The audio cues are subtle. They won't startle someone in a quiet warehouse, and they won't be heard in a noisy one. This is the right default — audio is supplementary to the visual feedback, not the primary signal.

**⚠ Problem: No volume control or mute toggle.** The learner cannot adjust or silence audio. On a shared terminal, audio cues from one learner's session may be disruptive to nearby workers.

> **Recommendation:** Add a mute toggle to the HUD. A small speaker icon in the top bar. Persist the setting in localStorage per-browser so the learner doesn't have to re-mute every session.

### Verdict

The audio system is well-designed for its purpose. The mute toggle is the only gap.

---

## Cross-Cutting Issues

### Color System

The application uses five branding colors (shell, accent, four level colors) with derived RGB values for alpha transparency operations. These come from the scenario's branding configuration with SAP defaults as fallback.

The color system is internally consistent: green = safe/explore, blue = guided/informational, orange = caution/intermediate, red = danger/challenge. This maps to a universally understood severity scale (traffic light + escalation). No issues.

However, the system assumes all learners can distinguish these four colors. Red-green color blindness would make Level 0 (green) and Level 3 (red) hard to differentiate.

> **Recommendation:** Add a secondary differentiator to level indicators — for example, an icon or pattern in addition to color. The level names (EXPLORE, GUIDED, etc.) already serve this purpose in most contexts, but the small colored badges and borders rely on color alone.

### Typography

The application uses the system font stack (`-apple-system, BlinkMacSystemFont, "Segoe UI", Arial, sans-serif`). This is correct for a PoC — it renders natively on every platform, loads instantly, and matches the OS's visual language. No change needed.

Font sizes range from 10px (labels) to 48px (win/timeout headings). The smallest text (10px uppercase labels) may be below readable size on lower-density displays or at arm's length on a warehouse tablet.

> **Recommendation:** Audit all instances of `fontSize: 10` and increase to `fontSize: 11` minimum. The WCAG recommendation is 12px minimum for body text, with labels allowed to be slightly smaller. 10px is pushing it.

### Animation and Motion

Animations include: pulse ellipse (L1), hover slide (level select cards), feedback fade-in, confetti fall (win), and Three.js rotate/explode. All animations are subtle and purposeful — none are purely decorative. The pulse and confetti have cleanup functions (`cancelAnimationFrame`, `remove()`). No motion sickness concerns at current intensities.

There is no `prefers-reduced-motion` media query anywhere in the application.

> **Recommendation:** Add a `prefers-reduced-motion` check that disables the pulse animation, confetti, and auto-rotation of the 3D model. These are the three animations that run continuously and could trigger vestibular discomfort.

### State Persistence

There is none. Every page load starts from the level select screen with a clean state. No progress is saved. The learner cannot resume a partially completed level, and there's no record of which levels they've completed.

This is acceptable for the PoC but it's the single largest gap between the current build and a production-ready product. The `ux-design-intent.md` document explicitly calls for progress-aware level selection, which requires persistence.

> **Recommendation:** For PoC: use localStorage to save the highest completed level per scenario. Display completed levels with a checkmark on the level select screen. This is a minimal implementation that would dramatically improve the returning-learner experience. For production: implement server-side progress tracking with user authentication.

---

## Priority Summary

The following table ranks every recommendation in this document by impact and effort. "Impact" is how much the change improves the learner's experience. "Effort" is implementation complexity.

| Priority | Recommendation | Surface | Impact | Effort |
|---|---|---|---|---|
| 1 | Add "Next Level →" button on Win Screen | Win Screen | High | Low |
| 2 | Briefing screen responsive layout (<800px) | Briefing | High | Medium |
| 3 | LocalStorage progress tracking | Cross-cutting | High | Medium |
| 4 | Task-first scenario titles (primary + subtitle) | Selector | High | Low |
| 5 | Consequence panel dismiss button | Level 2 Play | Medium | Low |
| 6 | "Done Exploring" → "Continue to Guided" flow | Explore Panel | Medium | Low |
| 7 | Debrief "Continue" → "See Your Results" label | Debrief | Low | Trivial |
| 8 | Timeout diagnostic (slowest step) | Timeout | Medium | Low |
| 9 | Mute toggle in HUD | Audio | Medium | Low |
| 10 | Hide score on Level 0 | HUD | Low | Trivial |
| 11 | Touch event handlers for 3D view | Briefing | Medium | Medium |
| 12 | Touch feedback on level select cards | Level Select | Low | Low |
| 13 | Back arrow 48px touch target | HUD | Low | Trivial |
| 14 | `prefers-reduced-motion` support | Cross-cutting | Low | Low |
| 15 | Minimum font size audit (10px → 11px) | Cross-cutting | Low | Trivial |
| 16 | Color-blind secondary differentiators | Cross-cutting | Low | Medium |
| 17 | HUD condensed mode for narrow viewports | HUD | Medium | Medium |

Items 1–6 should be addressed before any pilot with real learners. Items 7–10 are quick wins that can be done in a single pass. Items 11–17 are production hardening.

---

## What's Working

To be clear about what doesn't need to change: the four-level progression is the right pedagogical model. The spotlight-to-unguided arc maps directly to how skill acquisition works (guided practice → independent practice → assessment). The consequence panels are the product's best feature — they transform wrong clicks from punishment into learning moments. The debrief screen reinforces this by letting the learner review consequences in a low-pressure post-game context. The review mode tests spatial memory independent of procedural sequence, which is a genuine pedagogical innovation. The audio system is tasteful and non-intrusive. The 3D exploded view for hardware scenarios is a differentiator that no click-through trainer competitor offers.

The design is sound. This document identifies where the implementation hasn't caught up to the intent, and where a few targeted improvements would close the gap.
