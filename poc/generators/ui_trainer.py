#!/usr/bin/env python3
"""
ui_trainer.py — Generic game-style interactive UI trainer engine.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Loads a scenario pack and generates a self-contained interactive HTML trainer.

TUTORIAL MODE — pulsing spotlight guides the user through each UI element.
MISSION MODE  — no hints; user must complete the full workflow unassisted.

Usage:
  python3 generators/ui_trainer.py                         # default SE-DC GR
  python3 generators/ui_trainer.py scenarios/pharma_gr     # pharma scenario
  python3 generators/ui_trainer.py scenarios/hazmat_gr     # hazmat scenario

Output:  poc/output/ui_trainer/{scenario_id}/
  ├── index.html   ← open in any browser, no server needed
  └── screens/     ← placeholder PNGs (swap with real screenshots)

Scenario pack contract
──────────────────────
Each scenario is a Python module (in generators/scenarios/) that exports:

  SCENARIO : dict
    id               str    — kebab-case identifier (used in output path)
    title            str    — displayed in browser tab + HUD
    site             str    — displayed in HUD subtitle
    role             str    — learner's job role
    handling_profile str    — "standard_dry" | "perishable" | "regulated_pharma"
                              | "hazmat" | "serialized"
    tutorial         list   — steps; each step:
        screen       str    — filename in screens/
        goal         str    — shown as the step objective
        instruction  str    — shown as the action instruction
        hint         str    — revealed on demand in tutorial mode
        hotspot      dict   — {x, y, w, h} pixel rect of the clickable target
        feedback     str    — shown after a correct click in tutorial mode
    mission          dict
        title        str
        briefing     str    — shown before mission starts
        par_clicks   int    — target click count for scoring

  generate_screens(screens_dir: Path) -> list[str]
    Generates placeholder PNGs into screens_dir.
    Returns list of filenames generated.

To create a new scenario, copy scenarios/sedc_goods_receipt.py and edit it.
"""

import sys, os, json, importlib
from pathlib import Path


# ── Resolve scenario module ───────────────────────────────────────────────────
def load_scenario(module_path: str):
    """
    Import scenario module from a dotted name or file path.
    Default: scenarios.sedc_goods_receipt
    """
    # Normalise: convert path separators + strip .py suffix
    module_path = module_path.replace("/", ".").replace("\\", ".").rstrip(".")
    if module_path.endswith(".py"):
        module_path = module_path[:-3]

    # Add generators/ to sys.path so relative imports work
    generators_dir = str(Path(__file__).parent)
    if generators_dir not in sys.path:
        sys.path.insert(0, generators_dir)

    return importlib.import_module(module_path)


# ── HTML player ───────────────────────────────────────────────────────────────
# All scenario-specific content is injected via __SCENARIO_JSON__ and
# __SCREENS_JSON__ placeholders.  Everything else is generic.

HTML_TEMPLATE = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title id="page-title">Interactive UI Trainer</title>
<style>
  *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
  body {
    background: #0a0a1a;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Arial, sans-serif;
    color: #fff;
    height: 100vh;
    overflow: hidden;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
  }

  /* ── Top HUD ── */
  #hud {
    position: fixed; top: 0; left: 0; right: 0; height: 52px;
    background: rgba(3, 61, 128, 0.95);
    backdrop-filter: blur(8px);
    display: flex; align-items: center; gap: 16px;
    padding: 0 20px; z-index: 100;
    border-bottom: 2px solid rgba(0,112,242,0.6);
  }
  #hud-title   { font-size: 14px; font-weight: 700; color: #fff; flex: 1; }
  #hud-mode    { font-size: 11px; font-weight: 700; letter-spacing: 1px;
                 background: #E87600; color: #fff; padding: 3px 10px;
                 border-radius: 12px; text-transform: uppercase; }
  #hud-step    { font-size: 13px; color: #a0c4ff; }
  #progress-bar-wrap { width: 200px; height: 6px; background: rgba(255,255,255,0.15);
                       border-radius: 3px; overflow: hidden; }
  #progress-bar      { height: 100%; background: #E87600; border-radius: 3px;
                       transition: width 0.4s ease; }
  #score-badge { font-size: 12px; background: rgba(255,255,255,0.1);
                 padding: 4px 12px; border-radius: 12px; color: #e0e0e0; }

  /* ── Screen container ── */
  #screen-wrap {
    position: relative; margin-top: 52px;
    width: 100%; max-width: 1280px; cursor: crosshair;
  }
  #screen-img  { display: block; width: 100%; height: auto;
                 user-select: none; -webkit-user-drag: none; }

  /* ── Overlays ── */
  #overlay     { position: absolute; inset: 0; pointer-events: none; }
  #overlay canvas { display: block; width: 100%; height: 100%; }
  #click-layer { position: absolute; inset: 0; cursor: crosshair; }

  /* ── Goal card ── */
  #goal-card {
    position: fixed; bottom: 20px; left: 50%; transform: translateX(-50%);
    width: min(680px, 90vw);
    background: rgba(3, 20, 50, 0.92);
    backdrop-filter: blur(12px);
    border: 1px solid rgba(0,112,242,0.5);
    border-radius: 12px; padding: 18px 22px; z-index: 200;
  }
  #goal-label      { font-size: 10px; font-weight: 700; letter-spacing: 2px;
                     color: #E87600; text-transform: uppercase; margin-bottom: 6px; }
  #goal-text       { font-size: 17px; font-weight: 600; color: #fff;
                     margin-bottom: 10px; line-height: 1.4; }
  #instruction-text{ font-size: 13px; color: #a0c4ff; margin-bottom: 12px; line-height: 1.5; }
  #card-footer     { display: flex; align-items: center; gap: 12px; }
  #hint-btn        { font-size: 12px; padding: 6px 14px; border-radius: 6px;
                     border: 1px solid rgba(255,255,255,0.2); background: transparent;
                     color: #a0c4ff; cursor: pointer; }
  #hint-btn:hover  { background: rgba(255,255,255,0.1); }
  #hint-text       { font-size: 12px; color: #ffd080; display: none; flex: 1; }
  #skip-btn        { margin-left: auto; font-size: 12px; padding: 6px 14px;
                     border-radius: 6px; border: 1px solid rgba(255,255,255,0.1);
                     background: transparent; color: #666; cursor: pointer; }
  #skip-btn:hover  { color: #999; background: rgba(255,255,255,0.05); }

  /* ── Feedback flash ── */
  #feedback-flash {
    position: fixed; inset: 0; pointer-events: none; z-index: 300;
    display: flex; align-items: center; justify-content: center;
    opacity: 0; transition: opacity 0.15s;
  }
  #feedback-flash.show { opacity: 1; }
  #feedback-flash.correct { background: rgba(16, 126, 62, 0.25); }
  #feedback-flash.wrong   { background: rgba(187,  0, 11, 0.25); }
  #feedback-msg {
    background: rgba(0,0,0,0.85); padding: 20px 32px; border-radius: 12px;
    font-size: 16px; font-weight: 600; max-width: 500px; text-align: center;
    line-height: 1.5; border: 2px solid transparent;
  }
  .correct #feedback-msg { border-color: #107E3E; color: #6ee7a8; }
  .wrong   #feedback-msg { border-color: #BB000B; color: #ff8080; }

  /* ── Mission briefing overlay ── */
  #mission-screen {
    position: fixed; inset: 0; background: rgba(5, 10, 30, 0.97);
    display: none; align-items: center; justify-content: center;
    z-index: 500; flex-direction: column; gap: 24px;
  }
  #mission-screen h2 { font-size: 32px; color: #E87600; letter-spacing: 2px; }
  #mission-briefing  { font-size: 16px; line-height: 1.8; color: #c0d4ff;
                       text-align: center; max-width: 600px;
                       background: rgba(255,255,255,0.05);
                       border: 1px solid rgba(255,255,255,0.1);
                       border-radius: 12px; padding: 24px 32px; white-space: pre-line; }

  /* ── Win screen ── */
  #win-screen {
    position: fixed; inset: 0; background: rgba(5, 20, 10, 0.97);
    display: none; align-items: center; justify-content: center;
    z-index: 600; flex-direction: column; gap: 20px;
  }
  #win-screen h1 { font-size: 48px; color: #6ee7a8; }
  #win-screen p  { font-size: 18px; color: #a0c4ff; text-align: center; max-width: 480px; }
  #win-stats     { font-size: 15px; color: #e0e0e0; text-align: center; }

  /* ── Shared button ── */
  .btn-primary {
    font-size: 16px; font-weight: 700; padding: 14px 40px; border-radius: 8px;
    border: none; background: #0070F2; color: #fff;
    cursor: pointer; transition: background 0.2s;
  }
  .btn-primary:hover  { background: #0060d0; }
  .btn-primary:active { transform: scale(0.97); }

  /* ── Mode switcher ── */
  #mode-select { position: fixed; top: 52px; right: 0; display: flex; z-index: 100; }
  .mode-btn {
    font-size: 11px; font-weight: 700; padding: 6px 16px;
    border: 1px solid rgba(255,255,255,0.15); cursor: pointer;
    letter-spacing: 0.5px; transition: background 0.2s;
  }
  .mode-btn.active     { background: #E87600; border-color: #E87600; color: #fff; }
  .mode-btn:not(.active){ background: rgba(0,0,0,0.6); color: #a0c4ff; }

  /* ── Profile badge ── */
  #profile-badge {
    font-size: 10px; font-weight: 700; letter-spacing: 1px;
    padding: 3px 10px; border-radius: 12px; text-transform: uppercase;
    border: 1px solid rgba(255,255,255,0.25); color: #c0d4ff;
  }
</style>
</head>
<body>

<!-- HUD -->
<div id="hud">
  <div id="hud-title">Loading…</div>
  <div id="profile-badge"></div>
  <div id="hud-mode">Tutorial</div>
  <div id="hud-step">Step 1</div>
  <div id="progress-bar-wrap"><div id="progress-bar" style="width:0%"></div></div>
  <div id="score-badge">Score: 0</div>
</div>

<!-- Mode selector -->
<div id="mode-select">
  <button class="mode-btn active" onclick="setMode('tutorial')">Tutorial</button>
  <button class="mode-btn"        onclick="setMode('mission')">Mission</button>
</div>

<!-- Screen -->
<div id="screen-wrap">
  <img id="screen-img" src="" alt="Application screen" draggable="false">
  <div id="overlay"><canvas id="overlay-canvas"></canvas></div>
  <div id="click-layer" onclick="handleClick(event)"></div>
</div>

<!-- Goal card -->
<div id="goal-card">
  <div id="goal-label">Objective</div>
  <div id="goal-text"></div>
  <div id="instruction-text"></div>
  <div id="card-footer">
    <button id="hint-btn" onclick="showHint()">💡 Hint</button>
    <div id="hint-text"></div>
    <button id="skip-btn" onclick="nextStep(true)">Skip →</button>
  </div>
</div>

<!-- Feedback flash -->
<div id="feedback-flash">
  <div id="feedback-msg"></div>
</div>

<!-- Mission briefing -->
<div id="mission-screen" style="display:none">
  <h2>⚡ MISSION BRIEFING</h2>
  <div id="mission-briefing"></div>
  <button class="btn-primary" onclick="startMissionSteps()">Start Mission</button>
</div>

<!-- Win screen -->
<div id="win-screen">
  <h1>✅ Complete!</h1>
  <p id="win-msg"></p>
  <div id="win-stats"></div>
  <button class="btn-primary" onclick="restartMode()">Play Again</button>
</div>

<script>
// ── Scenario data (injected by ui_trainer.py) ─────────────────────────────────
const SCENARIO = __SCENARIO_JSON__;
const SCREENS  = __SCREENS_JSON__;   // { "filename.png": "screens/filename.png" }

// ── Init page metadata ────────────────────────────────────────────────────────
document.title = `${SCENARIO.title} — Interactive Trainer`;
document.getElementById('hud-title').textContent =
  `${SCENARIO.title}  ·  ${SCENARIO.site}`;
document.getElementById('profile-badge').textContent =
  SCENARIO.handling_profile.replace(/_/g, ' ');

// ── State ─────────────────────────────────────────────────────────────────────
let mode        = 'tutorial';
let stepIdx     = 0;
let score       = 0;
let wrongClicks = 0;
let totalClicks = 0;

const steps   = SCENARIO.tutorial;
const mission = SCENARIO.mission;

// ── DOM refs ──────────────────────────────────────────────────────────────────
const screenImg     = document.getElementById('screen-img');
const overlayCanvas = document.getElementById('overlay-canvas');
const hudMode       = document.getElementById('hud-mode');
const hudStep       = document.getElementById('hud-step');
const progressBar   = document.getElementById('progress-bar');
const scoreBadge    = document.getElementById('score-badge');
const goalText      = document.getElementById('goal-text');
const instrText     = document.getElementById('instruction-text');
const hintText      = document.getElementById('hint-text');
const feedbackEl    = document.getElementById('feedback-flash');
const feedbackMsg   = document.getElementById('feedback-msg');
const missionScreen = document.getElementById('mission-screen');
const winScreen     = document.getElementById('win-screen');
const modeButtons   = document.querySelectorAll('.mode-btn');

// ── Scale factor ──────────────────────────────────────────────────────────────
function getScale() {
  return screenImg.getBoundingClientRect().width / 1280;
}

// ── Overlay drawing ───────────────────────────────────────────────────────────
function drawOverlay(step) {
  const rect = screenImg.getBoundingClientRect();
  overlayCanvas.width  = rect.width;
  overlayCanvas.height = rect.height;
  const ctx   = overlayCanvas.getContext('2d');
  const scale = getScale();

  if (mode === 'mission') {
    ctx.fillStyle = 'rgba(0,0,0,0.06)';
    ctx.fillRect(0, 0, overlayCanvas.width, overlayCanvas.height);
    return;
  }

  // Tutorial: dark overlay with spotlight cutout
  const hs  = step.hotspot;
  const hx  = hs.x * scale, hy = hs.y * scale;
  const hw  = hs.w * scale, hh = hs.h * scale;
  const pad = 12 * scale;

  ctx.fillStyle = 'rgba(0,0,0,0.62)';
  ctx.fillRect(0, 0, overlayCanvas.width, overlayCanvas.height);
  ctx.clearRect(hx - pad, hy - pad, hw + pad * 2, hh + pad * 2);

  ctx.strokeStyle = '#E87600';
  ctx.lineWidth   = 3;
  ctx.shadowColor = '#E87600';
  ctx.shadowBlur  = 18;
  ctx.beginPath();
  ctx.roundRect(hx - pad, hy - pad, hw + pad * 2, hh + pad * 2, 6);
  ctx.stroke();
  ctx.shadowBlur = 0;
}

// Pulse animation
let pulseAnim = null;
let pulsePhase = 0;

function startPulse(step) {
  stopPulse();
  const scale = getScale();
  const hs = step.hotspot;
  const cx = (hs.x + hs.w / 2) * scale;
  const cy = (hs.y + hs.h / 2) * scale;
  const rx = (hs.w / 2 + 16) * scale;
  const ry = (hs.h / 2 + 16) * scale;

  function frame() {
    pulsePhase = (pulsePhase + 0.04) % (Math.PI * 2);
    const s     = 1 + Math.sin(pulsePhase) * 0.08;
    const alpha = 0.5 + Math.sin(pulsePhase) * 0.3;
    drawOverlay(step);
    const ctx = overlayCanvas.getContext('2d');
    ctx.save();
    ctx.translate(cx, cy);
    ctx.scale(s, s);
    ctx.strokeStyle = `rgba(232,118,0,${alpha})`;
    ctx.lineWidth   = 2.5;
    ctx.beginPath();
    ctx.ellipse(0, 0, rx / s, ry / s, 0, 0, Math.PI * 2);
    ctx.stroke();
    ctx.restore();
    pulseAnim = requestAnimationFrame(frame);
  }
  pulseAnim = requestAnimationFrame(frame);
}

function stopPulse() {
  if (pulseAnim) { cancelAnimationFrame(pulseAnim); pulseAnim = null; }
}

// ── Load a step ───────────────────────────────────────────────────────────────
function loadStep(idx) {
  stepIdx = idx;
  hintText.style.display = 'none';
  const step  = steps[idx];
  const total = steps.length;

  screenImg.src     = SCREENS[step.screen];
  screenImg.onload  = () => {
    if (mode === 'tutorial') startPulse(step); else drawOverlay(step);
  };

  hudStep.textContent           = `Step ${idx + 1} of ${total}`;
  progressBar.style.width       = `${((idx + 1) / total) * 100}%`;
  scoreBadge.textContent        = `Score: ${score}`;
  goalText.textContent          = step.goal;
  instrText.textContent         = step.instruction;
  hintText.textContent          = step.hint;

  document.getElementById('hint-btn').style.display =
    mode === 'tutorial' ? '' : 'none';
  document.getElementById('skip-btn').style.display =
    mode === 'tutorial' ? '' : 'none';
}

// ── Click handler ─────────────────────────────────────────────────────────────
function handleClick(e) {
  const rect  = screenImg.getBoundingClientRect();
  const scale = getScale();
  const mx    = (e.clientX - rect.left) / scale;
  const my    = (e.clientY - rect.top)  / scale;
  const step  = steps[stepIdx];
  const hs    = step.hotspot;
  const tol   = 20;

  totalClicks++;
  const hit = mx >= hs.x - tol && mx <= hs.x + hs.w + tol &&
              my >= hs.y - tol && my <= hs.y + hs.h + tol;

  if (hit) {
    score += (mode === 'mission' ? 200 : 100) - (wrongClicks * 25);
    score  = Math.max(score, 0);
    wrongClicks = 0;
    showFeedback('correct', mode === 'mission' ? '✓ Correct!' : step.feedback);
    setTimeout(() => nextStep(false), mode === 'mission' ? 800 : 2200);
  } else {
    wrongClicks++;
    showFeedback('wrong', mode === 'tutorial'
      ? 'Not quite — look for the highlighted area.'
      : 'Wrong element. Try again.');
    if (mode === 'tutorial') {
      setTimeout(() => { hintText.style.display = 'block'; }, 400);
    }
  }
}

function showFeedback(type, msg) {
  feedbackEl.className  = `show ${type}`;
  feedbackMsg.textContent = msg;
  setTimeout(() => { feedbackEl.className = ''; },
    type === 'correct' ? 2000 : 1200);
}

function showHint() {
  hintText.style.display = hintText.style.display === 'block' ? 'none' : 'block';
}

function nextStep(skip) {
  stopPulse();
  if (!skip) score += 50;
  if (stepIdx + 1 >= steps.length) showWin();
  else loadStep(stepIdx + 1);
}

// ── Win ───────────────────────────────────────────────────────────────────────
function showWin() {
  stopPulse();
  winScreen.style.display = 'flex';
  const acc = totalClicks > 0
    ? Math.round((totalClicks - wrongClicks * 2) / totalClicks * 100)
    : 100;
  document.getElementById('win-msg').textContent = mode === 'tutorial'
    ? 'Tutorial complete! Switch to Mission mode and try it without hints.'
    : `${SCENARIO.title} — workflow complete.`;
  document.getElementById('win-stats').innerHTML =
    `Final Score: <strong>${score}</strong> &nbsp;|&nbsp; ` +
    `Accuracy: <strong>${Math.max(0, acc)}%</strong> &nbsp;|&nbsp; ` +
    `Mode: <strong>${mode === 'tutorial' ? 'Tutorial' : 'Mission'}</strong>`;
  scoreBadge.textContent = `Score: ${score}`;
}

function restartMode() {
  winScreen.style.display = 'none';
  score = 0; wrongClicks = 0; totalClicks = 0;
  loadStep(0);
}

// ── Mode switching ────────────────────────────────────────────────────────────
function setMode(m) {
  mode = m;
  winScreen.style.display = 'none';
  modeButtons.forEach(b =>
    b.classList.toggle('active', b.textContent.toLowerCase() === m));
  hudMode.textContent = m === 'tutorial' ? 'Tutorial' : 'Mission';
  score = 0; wrongClicks = 0; totalClicks = 0;
  scoreBadge.textContent = 'Score: 0';

  if (m === 'mission') {
    missionScreen.style.display = 'flex';
    document.getElementById('mission-briefing').textContent = mission.briefing;
  } else {
    missionScreen.style.display = 'none';
    loadStep(0);
  }
}

function startMissionSteps() {
  missionScreen.style.display = 'none';
  loadStep(0);
}

// ── Init ─────────────────────────────────────────────────────────────────────
window.addEventListener('resize', () => { if (steps[stepIdx]) loadStep(stepIdx); });
loadStep(0);
</script>
</body>
</html>
"""


# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    # Resolve scenario
    scenario_arg = sys.argv[1] if len(sys.argv) > 1 else "scenarios.sedc_goods_receipt"
    print(f"Loading scenario: {scenario_arg}")
    mod = load_scenario(scenario_arg)

    scenario = mod.SCENARIO
    sid = scenario["id"]
    print(f"  Title   : {scenario['title']}")
    print(f"  Site    : {scenario['site']}")
    print(f"  Profile : {scenario['handling_profile']}")
    print(f"  Steps   : {len(scenario['tutorial'])}")

    # Output paths
    base_out    = Path(__file__).parent.parent / "output" / "ui_trainer" / sid
    screens_dir = base_out / "screens"
    base_out.mkdir(parents=True, exist_ok=True)

    # Generate placeholder screens
    print("\nGenerating placeholder screens …")
    generated = mod.generate_screens(screens_dir)
    for fname in generated:
        print(f"  ✓  {fname}")

    # Build screens map (relative paths for HTML)
    screens_map = {fname: f"screens/{fname}" for fname in generated}

    # Inject data into HTML template
    html = HTML_TEMPLATE.replace(
        "__SCENARIO_JSON__", json.dumps(scenario, indent=2)
    ).replace(
        "__SCREENS_JSON__", json.dumps(screens_map, indent=2)
    )

    index_path = base_out / "index.html"
    index_path.write_text(html, encoding="utf-8")

    print(f"\n✅  Done!")
    print(f"   Trainer : {index_path}")
    print(f"   Screens : {screens_dir}/")
    print(f"\n   Open with:  open \"{index_path}\"")
    print(f"\nTo use real screenshots:")
    print(f"   Capture at 1280×720, name to match screens/*.png")
    print(f"   Drop into {screens_dir} — no other changes needed.")
    print(f"\nTo create a new scenario:")
    print(f"   cp generators/scenarios/sedc_goods_receipt.py generators/scenarios/my_scenario.py")
    print(f"   # edit SCENARIO dict + generate_screens()")
    print(f"   python3 generators/ui_trainer.py scenarios.my_scenario")


if __name__ == "__main__":
    main()
