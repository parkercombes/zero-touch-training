# Zero-Touch Training

**AI-generated ERP training, compiled from the same assets that keep the system running.**

Zero-Touch Training replaces manual course authoring with an automated pipeline that generates training materials from automated test scripts, process models, and configuration data. When the system changes, training updates automatically.

## The Problem

ERP training today is expensive to create, slow to update, quickly outdated, and detached from how the system actually changes. At commercial distribution centers like GlobalMart SE-DC, this is amplified by site-specific processes (Opal overlays), multiple UI layers (SAP, Fiori, Appian), and high personnel turnover.

## The Approach

Training-as-Code, embedded in the DevSecOps pipeline. AI translates technical assets — test scripts, process models, UI metadata — into walkthroughs, explainer videos, job aids, and in-app guidance. No manual authoring from scratch.

See [`docs/concept.md`](docs/concept.md) for the full concept and layered training model.

## Pilot

- One role, one end-to-end process, one site (GlobalMart SE-DC, Atlanta, GA)
- ~1–2 weeks, one person
- Outputs: AI-generated process explainer video, role-specific job aids, optional WalkMe draft
