# Zero-Touch Training

**AI-generated training — compiled from the same assets that keep the system running.**

Zero-Touch Training replaces manual course authoring with an automated pipeline that generates training materials from automated test scripts, process models, and configuration data. When the system changes, training updates automatically. The platform now supports two training domains: **software** (ERP workflows like SAP MIGO) and **hardware** (equipment maintenance and assembly like AR-15 field strip).

## The Problem

Training today is expensive to create, slow to update, quickly outdated, and detached from how the system actually changes. In ERP environments this is amplified by site-specific processes, multiple UI layers, and high turnover. In hardware/maintenance environments the problem is different but parallel: procedures are taught person-to-person, institutional knowledge walks out the door, and mistakes during maintenance have real safety consequences.

## The Approach

Training-as-Code, embedded in the DevSecOps pipeline. AI translates technical assets — test scripts, process models, UI metadata — into walkthroughs, explainer videos, job aids, and in-app guidance. No manual authoring from scratch.

The interactive UI trainer is built as a **React single-page application** (~1,645 lines) with a game-inspired four-level progression system. A single domain-agnostic game engine drives both software and hardware scenarios — only the screen generation layer and branding differ.

See [`docs/concept.md`](docs/concept.md) for the full concept and layered training model.

## What's Built

**Two training domains, one engine:**

| Domain | Scenarios | Example |
|---|---|---|
| Software (SAP) | 5 handling profiles | Standard dry, perishable, pharma, hazmat, serialized |
| Hardware | 2 pilot scenarios | AR-15 field strip & cleaning, F-150 shift lever & seal service |

**Interactive UI trainer features (all built):**

- Four-level progression: Explore → Guided → On Your Own → Challenge (software) / OBSERVE → FOLLOW ALONG → DO IT → SPEED RUN (hardware)
- Consequence-based error feedback ("here's what would break in production")
- Timer with audio cues in challenge mode
- Confetti celebration on completion
- Narrative premise cards with rotating scenarios
- Decoy fields on higher levels for realistic decision-making
- Post-level debrief screens
- Review mode (scrambled steps from the win screen)
- Auto-generated scenario selector with domain grouping

**Also includes:** AI-generated walkthroughs, job aids, video scripts, WalkMe flow drafts, and social media explainer videos (Veo 3 lip-synced Bigfoot characters).

## Pilot

- One role, one end-to-end process, one site (GlobalMart SE-DC, Atlanta, GA)
- ~1–2 weeks, one person
- Outputs: AI-generated process explainer video, role-specific job aids, interactive UI trainers, optional WalkMe draft
