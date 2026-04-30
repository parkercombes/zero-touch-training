# Layer 6: Continuous Update & Drift Control

**Goal:** "Training is never outdated."

## Purpose

Layers 1-4 describe how training is created. Layer 5 describes how training stays current. In traditional training systems, courses become stale when systems change. Users read outdated guides, get confused, and lose trust in the training.

Layer 5 eliminates this problem through continuous monitoring and automated regeneration. The system constantly watches for changes to source materials (test scripts, process models, system configuration). When changes are detected, affected training is automatically flagged as stale and regenerated. Training is published only when it has been validated against current system state.

The key principle: **Training is assumed stale until proven current.** Every time a source asset changes, all training derived from it is flagged as out-of-date until regeneration is complete and approved.

## Source Inputs for Change Detection

Layer 5 monitors multiple sources for changes:

### Tosca Test Script Changes
- New test scripts (new functionality to document)
- Modified test scripts (steps changed, selectors updated, validation rules altered)
- Deleted test scripts (functions no longer available, training no longer needed)
- Test script version changes in configuration management system
- Failed regression tests (test failed, meaning system behavior changed unexpectedly)

**Change Detection Method:**
- Automated comparison of Tosca script versions (Git hash, file modification timestamp)
- Regression test runs: if tests that previously passed now fail, change is detected
- Tosca continuous integration pipeline: hooks notify training system when tests are updated

### Configuration Transport (SAP Change Pipeline)
- New transaction codes or apps deployed to production
- Field configurations changed (field visibility, default values, validation rules)
- Approval workflow changes in IMG (SAP Customizing)
- Menu structure reorganizations (new menus, removed menu items)
- Authorization matrix changes (new roles, modified role permissions)
- Business rule changes (SLA changes, new validation logic)

**Change Detection Method:**
- Monitor SAP change request fulfillment: when transport request is deployed to production, notify training system
- Periodic snapshot of system configuration (menu, fields, authorizations) vs. previous snapshot
- SAP audit logs: detecting changes to critical configuration tables (RFTAB, RFSYS, etc.)
- Transport request metadata: when change orders are moved from DEV → QA → PROD

### UI Snapshot Comparison
- Screen layout changes (field moved, button repositioned, form reorganized)
- New fields added to existing screens
- Fields deleted or hidden
- Visual styling changes (fonts, colors, icons that affect user recognition)
- Fiori app tile changes or new app deployments
- Appian workspace configuration changes

**Change Detection Method:**
- Automated screenshot captures of key screens at regular intervals (daily or on-demand)
- Image comparison: detect pixel-level changes to identify layout changes
- DOM structure comparison: detect HTML/CSS changes affecting element selectors
- Fiori app catalog API: monitor app versions and deployments
- Appian process definition API: monitor workspace changes

### Signavio Process Model Version Changes
- New process models (new business processes requiring documentation)
- Modified BPMN models (process flow changed, roles altered, decision gates added/removed)
- Process model version bumps in Signavio
- Swim lane reorganizations (role assignments changed)
- SLA or performance metric changes

**Change Detection Method:**
- Signavio API polling: check version numbers of all published process models
- Git repository (if BPMN exported to Git): detect file changes via Git hooks
- Signavio event notifications: subscribe to model modification events
- Periodic hash comparison: store hash of model XML, detect changes

### Site-Specific Configuration Changes
- Role assignments changed at a specific site
- Approval workflows differ at a site
- Field defaults changed for a site
- Business rules applied differently at a site
- Site-specific transaction codes or functions enabled/disabled

**Change Detection Method:**
- Monitor Opal metadata system for site-specific configuration changes
- Periodic site-level configuration snapshot comparison
- Change request tracking: when a site-specific change is deployed
- Survey-based detection: SMEs at each site report configuration changes

## The Staleness Model: A Key Principle

The zero-touch training system operates on a strict staleness principle:

**Assumption: All training is stale until proven current against the live system.**

This approach inverts the traditional model where training is considered valid until proven wrong. Instead:

1. **Training is generated** from source assets (Tosca, BPMN, UI metadata, configuration)
2. **Metadata tags training** with source asset versions: "Generated from Tosca v2.1, BPMN v3.4, SAP config snapshot v1.8"
3. **Continuous monitoring** detects when source assets change
4. **Change detection triggers staleness flag:** Any training derived from the changed asset is immediately flagged as out-of-date
5. **Regeneration pipeline** starts: AI regenerates training from updated sources
6. **Validation gates** verify regenerated training is accurate
7. **Approval gates** require human sign-off before publishing
8. **Only approved, current training** is published to users

**Benefit:** Users never encounter stale training. If a system change occurred, users see either:
- Current training reflecting the change, or
- A clear notice that training is being updated and unavailable temporarily

Users never see outdated training because stale training is never published.

## Change Detection and Notification

### Automated Change Detection Pipeline

```
┌─────────────────────────────────────────────────────────────┐
│ Change Detection Sources                                      │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌─────────────┐  ┌──────────────┐  ┌──────────────┐       │
│  │   Tosca     │  │ SAP Config   │  │   UI/Fiori   │  ...  │
│  │Test Scripts │  │  Transport   │  │  Snapshots   │       │
│  └─────────────┘  └──────────────┘  └──────────────┘       │
│         │                │                  │                │
│         └────────────────┼──────────────────┘                │
│                          │                                    │
└──────────────────────────┼────────────────────────────────────┘
                           │
                           ▼
        ┌──────────────────────────────────┐
        │  Change Detection Service        │
        ├──────────────────────────────────┤
        │  • Hash comparison               │
        │  • Version checking              │
        │  • Diff analysis                 │
        │  • Screenshot comparison         │
        │  • Regression test monitoring    │
        └──────────────────────────────────┘
                           │
                           ▼
        ┌──────────────────────────────────┐
        │  Change Log & Notification       │
        ├──────────────────────────────────┤
        │  Asset: Tosca/Create_PR v2.1    │
        │  Change: Step 5 UI selector     │
        │          changed from ID to CSS │
        │  Timestamp: 2024-01-15T09:30Z   │
        │  Status: DETECTED               │
        └──────────────────────────────────┘
                           │
                           ▼
        ┌──────────────────────────────────┐
        │  Training Staleness Tagger       │
        ├──────────────────────────────────┤
        │  Query: Training derived from   │
        │          Tosca/Create_PR v2.1   │
        │  Result: 5 training materials   │
        │           now stale             │
        │  Action: Flag all 5 as STALE    │
        └──────────────────────────────────┘
                           │
                           ▼
        ┌──────────────────────────────────┐
        │  Regeneration Pipeline Start     │
        │  (see next section)              │
        └──────────────────────────────────┘
```

### Staleness Flagging Rules

When a source asset changes, determine which training is affected:

**Rule 1: Direct Derivation**
- If Tosca script T1 changes → Flag all Layer 3 job aids derived from T1
- If BPMN model M1 changes → Flag all Layer 2 process videos derived from M1
- If UI element E1 changes → Flag all Layer 4 in-app flows using E1

**Rule 2: Dependency-Based Staleness**
- If Tosca T1 changes and Layer 3 job aid A uses T1, then:
  - A is stale (direct)
  - All Layer 4 in-app flows that reference A are also stale (indirect)
  - All site-specific overlays of A are stale

**Rule 3: Transitive Staleness**
- If SAP transaction code T changes → Layer 1 navigation guides referencing T are stale
- If layer 1 guide is stale → Prerequisite for Layer 2 process context may be affected
- Cascade check: if Layer 1 stale, check if Layer 2 depends on Layer 1

**Rule 4: Site-Specific Staleness Independence**
- If enterprise-level configuration changes, all sites are affected
- If site-specific configuration changes (e.g., SE-DC role changes), only that site's training is stale
- Allow enterprise and site-specific staleness to be tracked independently

### Notification System

When training is flagged stale:

1. **Dashboard Update:** Drift reporting dashboard (Layer 5 visibility) shows training as "STALE"
2. **Email Notification:** Training coordinators are notified
3. **User-Facing Notice:** If users try to access stale training, they see: "This training is being updated and will be available shortly"
4. **Halt Publishing:** Stale training is removed from active publication (users don't see it)
5. **Regeneration Trigger:** Automated regeneration starts immediately

## Trigger → Regenerate → Validate → Publish Flow

### Detailed Pipeline

```
PHASE 1: TRIGGER (Change Detected)
┌─────────────────────────────────────┐
│ Source asset changed:               │
│ - New version deployed              │
│ - Tosca test modified               │
│ - SAP config transported to PROD    │
│ - Screenshot shows layout change    │
└─────────────────────────────────────┘
          │
          ▼
┌─────────────────────────────────────┐
│ Change Detection Service            │
│ Generates change record:            │
│ - Asset name & ID                   │
│ - Change type (added/modified/etc)  │
│ - Timestamp                         │
│ - Affected training (5 items)       │
└─────────────────────────────────────┘
          │
          ▼
┌─────────────────────────────────────┐
│ Staleness Tagger                    │
│ Marks affected training as STALE    │
│ Removes from user-facing publishing │
└─────────────────────────────────────┘
          │
          ▼
PHASE 2: REGENERATE (AI Recreates Training)
┌─────────────────────────────────────┐
│ Regeneration Service                │
│ For each stale training item:       │
│ 1. Load source asset (new version)  │
│ 2. Run AI generation process        │
│ 3. Generate new content version     │
│ 4. Tag with source versions         │
│ Status: REGENERATED (not published) │
└─────────────────────────────────────┘
          │
          ▼
PHASE 3: VALIDATE (QA Checks Accuracy)
┌─────────────────────────────────────┐
│ Automated Validation:               │
│ - Screenshot accuracy:              │
│   Capture actual screens, compare   │
│   to training screenshots           │
│ - Selector validation:              │
│   Test all UI element selectors     │
│   to ensure they find elements      │
│ - Content consistency:              │
│   Verify no conflicting info        │
│ - Link validation:                  │
│   Cross-check all internal refs     │
│ Status: VALIDATED or FAILED         │
└─────────────────────────────────────┘
          │
          ├─→ VALIDATED? (90%+ pass rate)
          │      │
          │      ▼
          │  PHASE 4A: HUMAN REVIEW (SME Approval)
          │  ┌──────────────────────────┐
          │  │ Subject Matter Expert     │
          │  │ Reviews:                  │
          │  │ - Accuracy vs Tosca       │
          │  │ - Clarity of instruction  │
          │  │ - Site-specific overlays  │
          │  │ - Images/screenshots      │
          │  │ Decision:                 │
          │  │ ☑ Approve                 │
          │  │ ☐ Reject (needs fix)      │
          │  │ ☐ Request changes         │
          │  └──────────────────────────┘
          │      │
          │      ├─→ APPROVED
          │      │      │
          │      │      ▼
          │      │  Status: PUBLISHABLE
          │      │  Move to publishing queue
          │      │
          │      └─→ REJECTED
          │             │
          │             ▼
          │  Status: REGENERATION FAILED
          │  Log error, notify team
          │  Re-trigger regeneration with corrections
          │
          └─→ VALIDATION FAILED (< 90% pass)
                 │
                 ▼
             Status: REGENERATION FAILED
             Log errors, notify team
             Manual investigation required
             Re-trigger generation with corrections


PHASE 4B: PUBLISH
┌─────────────────────────────────────┐
│ Publishing Service                  │
│ For each PUBLISHABLE training:      │
│ 1. Update training repository       │
│ 2. Update user-facing portal        │
│ 3. Update LMS or documentation      │
│ 4. Log publication event            │
│ 5. Clear staleness flag             │
│ Status: CURRENT (published to users)│
└─────────────────────────────────────┘
          │
          ▼
┌─────────────────────────────────────┐
│ Dashboard Update                    │
│ Removed from "STALE" list           │
│ Moved to "CURRENT" list             │
│ Timestamp: published at [time]      │
└─────────────────────────────────────┘
```

## Validation Gates and Human Approval

**Key Principle:** AI generates; humans approve. Automation ensures speed, humans ensure accuracy.

### Automated Validation Gate 1: Content Validation

Run automated checks immediately after generation:

```
Checks Performed:

1. SCREENSHOT ACCURACY
   - Capture current live screenshots
   - Compare pixel-level to generated screenshots
   - Flag discrepancies (missing fields, layout changes, etc.)
   - Pass rate: 95%+ pixel match required

2. SELECTOR VALIDATION
   - For Layer 1 & Layer 4: Test every UI element selector
   - Primary selector must find element
   - Fallback selectors must be tested
   - Pass rate: 100% (all selectors must work)

3. REFERENCE VALIDATION
   - Check all internal links (Layer 2 → Layer 3, etc.)
   - Verify layer cross-references are valid
   - Check for dead links
   - Pass rate: 100% (no broken links allowed)

4. CONSISTENCY CHECKS
   - Layer 3 job aid steps must match Tosca script
   - Layer 4 flow completion conditions must match system validation
   - Layer 2 process must match BPMN model
   - Layer 1 navigation must match actual menu structure
   - Pass rate: 95%+ (minor discrepancies documented)

5. FIELD REFERENCE ACCURACY
   - All fields mentioned in Layer 3 must exist in system
   - Field data types correct (numeric fields labeled numeric, etc.)
   - Required vs. optional status matches system
   - Pass rate: 100%

Result: PASS or FAIL
If FAIL: Log errors, route to engineers for investigation,
         retry generation with corrections
If PASS: Proceed to Human Review Gate
```

### Human Approval Gate: Expert Review

Require SME approval before publication:

```
Approval Workflow:

Regenerated Training Generated
    │
    ├─ Validation Status: PASS ✓
    │
    ▼
Sent to Training Review Queue
    │
    ▼
Subject Matter Expert Reviews:
    ├─ [ ] Content Accuracy
    │       "Does this match the actual business process and system?"
    │
    ├─ [ ] Clarity
    │       "Would a new employee understand this?"
    │
    ├─ [ ] Completeness
    │       "Are all decision points and variations covered?"
    │
    ├─ [ ] Screenshots
    │       "Are the screenshots current and do they clearly show what to do?"
    │
    ├─ [ ] Site-Specific Accuracy
    │       "For each site variant, is the overlay correct?"
    │
    └─ [ ] Error Handling
            "Are all possible errors and how to fix them documented?"

Reviewer Decision:
    ├─ [✓] APPROVE
    │       Training is published immediately
    │
    ├─ [ ] APPROVE WITH COMMENTS
    │       Training published, but flag for future refinement
    │
    ├─ [ ] REVISION NEEDED
    │       Return to engineering with feedback
    │       Specify sections needing correction
    │       Engineering re-generates with feedback addressed
    │       Return to SME review
    │
    └─ [ ] REJECT
            Entire regeneration aborted
            Revert to previous version
            Log issue for investigation
            Contact engineering team

SLA for Approval:
    Business days: 1 (human review must complete within 24 hours)
    If no review within 24 hours, default to APPROVE
    (assumption: if not rejected, training is better than stale training)

Approval History:
    - Every training item tracks: who approved, when, review duration
    - Auditable: full log of approval decisions and reasons
    - Metrics: average review time, rejection rate, etc.
```

### Conditional Publishing: When to Block Publication

Publication is blocked (training not released to users) if:

1. **Validation fails** (automated gate shows > 5% errors)
2. **Human review rejects** (SME marks as REJECT or REVISION NEEDED)
3. **Critical error detected** (broken selectors, missing key steps, security issue)
4. **Governance not followed** (approval not obtained, audit trail incomplete)

If publication is blocked:
- Previous version remains available to users (reverted automatically)
- Team is notified to investigate
- Regeneration is re-triggered with manual intervention
- Dashboard clearly shows "Training Unavailable - Being Updated"

## Drift Reporting Dashboard

A key part of Layer 5 is visibility into training currency. The dashboard shows:

### Status Overview

```
TRAINING CURRENCY DASHBOARD

Project: Zero-Touch Training - GlobalMart DCs
Last Updated: 2024-01-20 14:32 UTC
Analysis Scope: All sites, all training materials

┌────────────────────────────────────────┐
│ TRAINING STATUS SUMMARY                │
├────────────────────────────────────────┤
│ Total Training Materials:    847       │
│ ✓ CURRENT:                  842 (99%)  │
│ ⚠ STALE:                      3 (0.4%) │
│ ⏳ REGENERATING:              2 (0.2%) │
│ ✗ FAILED:                     0 (0%)   │
│ 🔒 PENDING REVIEW:            0 (0%)   │
└────────────────────────────────────────┘

┌────────────────────────────────────────┐
│ RECENT CHANGES (Last 7 Days)            │
├────────────────────────────────────────┤
│ Changes detected:        5              │
│ Training regenerated:    5              │
│ Training approved:       5              │
│ Training published:      5              │
│ Time to publish (avg):   4 hours        │
└────────────────────────────────────────┘
```

### Stale Training Details

```
STALE TRAINING (3 items)

1. Layer 3: Creating Purchase Requisition
   Source Asset: Tosca/Create_PR v2.1
   Change Detected: 2024-01-20 09:30 UTC
   Stale Since: 4 hours
   Regeneration Status: IN PROGRESS
   Previous Version: HIDDEN FROM USERS
   ETA to Publish: 1 hour

   Change Summary: Tosca test updated step 5 selector from ID to CSS class
   Impact: Layer 3 job aid, Layer 4 WalkMe flow

2. Layer 2: Purchase Requisition to Goods Receipt Process
   Source Asset: BPMN Process Model v3.4
   Change Detected: 2024-01-19 16:45 UTC
   Stale Since: 22 hours
   Regeneration Status: PENDING HUMAN REVIEW
   Previous Version: HIDDEN FROM USERS
   Blocked Reason: SME requested clarification on new approval role

   Change Summary: New Finance Committee approval gate added for >$50K
   Impact: Layer 2 process video, Layer 3 job aids for approvers

3. Layer 1: Navigation to Procurement Apps
   Source Asset: Fiori App Catalog
   Change Detected: 2024-01-18 10:15 UTC
   Stale Since: 2.5 days
   Regeneration Status: VALIDATION FAILED
   Previous Version: REVERTED TO LIVE (previous version v1.7)
   Issue: 3 screenshots don't match current app tile layout

   Change Summary: Fiori app tiles reorganized, new "Quick Actions" section
   Impact: Layer 1 navigation guides for all users

   Next Action: Engineering to re-capture screenshots and re-generate
```

### Change Log with Traceability

```
CHANGE HISTORY (All changes from last 30 days)

Date/Time           Change Type     Source Asset        Reason          Status      Author
─────────────────── ─────────────── ─────────────────── ─────────────── ─────────── ──────────
2024-01-20 09:30   MODIFIED        Tosca/Create_PR     Selector update PUBLISHED   automation
2024-01-19 16:45   MODIFIED        BPMN Process v3.4   New approval    REVIEWING   automation
2024-01-18 10:15   MODIFIED        Fiori App Catalog   Reorganization  FAILED      automation
2024-01-15 14:22   NEW             Tosca/Reject_PR     New function    PUBLISHED   automation
2024-01-12 08:30   MODIFIED        SAP Config (MidWest-DC)   Override rules  PUBLISHED   SME-MidWest-DC
2024-01-10 16:45   MODIFIED        UI/SE-DC layout  Field order     PUBLISHED   automation
2024-01-08 09:00   DELETED         Tosca/Legacy_PR     Function retired PUBLISHED  automation
[... more history ...]

Legend:
  NEW: New training created for new functionality
  MODIFIED: Existing training updated due to source change
  DELETED: Training removed because functionality no longer exists
```

### By-Site View

```
TRAINING STATUS BY SITE

SE-DC Depot:
  Total Materials: 120
  Current: 119 (99%)
  Stale: 1 (Tosca update for Create_PR)
  Regenerating: 0
  Failed: 0
  Average Age: 3.2 days
  Last Change: 2024-01-20 09:30

MidWest-DC Depot:
  Total Materials: 120
  Current: 119 (99%)
  Stale: 1 (BPMN process update affecting approval flow)
  Regenerating: 1 (In SME review)
  Failed: 0
  Average Age: 2.8 days
  Last Change: 2024-01-12 08:30

[... other sites ...]
```

### Alerts and Escalation

```
CRITICAL ALERTS

🔴 [CRITICAL] Layer 1 Navigation - Validation Failed
   Training: Layer 1 Navigation to Procurement Apps
   Status: REVERTED TO PREVIOUS VERSION
   Problem: 3 of 5 screenshots invalid due to UI layout changes
   Action Required: Engineering must re-capture screenshots
   Time in FAILED state: 2.5 days
   Recommendation: Escalate to manager for priority fix
   Link: [View Details]

🟡 [WARNING] Layer 2 Process - Stuck in Review
   Training: Purchase Req to Goods Receipt Process Video
   Status: PENDING HUMAN REVIEW > 24 hours
   Blocked By: SME review of new Finance Committee approval step
   Action Required: Follow up with assigned SME
   Assigned To: J. Smith (Procurement Manager)
   Review SLA: 24 hours (breached by 0 hours 30 minutes)
   Link: [View Details] [Notify SME]

ℹ️ [INFO] Layer 3 Job Aid - Approved and Published
   Training: Creating a Purchase Requisition at SE-DC
   Status: PUBLISHED
   Source: Tosca v2.1 step selector change
   Publication Time: 2024-01-20 14:22 UTC
   SME Review Duration: 42 minutes (fast)
   Link: [View Live Training]
```

### Performance Metrics

```
PERFORMANCE METRICS

Change Detection to Publication Time:
  Average: 4 hours
  Median: 3.5 hours
  95th percentile: 8 hours
  Goal: < 24 hours (100% compliance)

Automated Validation Pass Rate:
  Current: 96%
  Target: > 95%
  Trend: ↑ (improving)

Human Approval Completion Rate:
  Within 24 hours: 100%
  Within 1 hour: 78%
  Average review time: 35 minutes

Publication Failure Rate:
  % Regenerations that fail validation: 0.3%
  % Regenerations rejected by human: 1.2%
  % Overall success rate: 98.5%

Training Staleness Duration:
  Average time training is stale: 2.3 hours
  Max staleness duration: 8 hours (all cases resolved)
  % of time with zero stale training: 89%
```

## Site-Specific Considerations

### Enterprise vs. Site-Specific Staleness Tracking

Staleness is tracked at two levels:

**Enterprise Level:**
- Tosca test changes
- BPMN process model changes
- Fiori app catalog updates
- Global SAP configuration changes
- Affect all sites

**Site Level:**
- Site-specific role assignments (SE-DC's approval chain differs from MidWest-DC's)
- Site-specific field defaults
- Site-specific approval thresholds
- Site-specific integration requirements
- Affect only that site

**Implementation:**
```
Training Material: Layer 3 - Creating a Purchase Requisition

Base Version: v1.0
  Source: Tosca/Create_PR v2.1, Deployed: 2024-01-15
  Applies To: All sites (enterprise standard)
  Status: CURRENT ✓

Site Overlay - SE-DC v1.0:
  Source: Opal/SE-DC Config v3.2
  Changes: Plant field auto-defaults to SE-DC_Main
  Applies To: SE-DC site only
  Status: CURRENT ✓

Site Overlay - MidWest-DC v1.2:
  Source: Opal/MidWest-DC Config v4.1
  Changes: Approval chain includes Finance Committee for >$50K
  Previous State: v1.1 (changed 2024-01-19)
  Applies To: MidWest-DC site only
  Status: REGENERATING (awaiting SME approval) ⏳
```

When enterprise base changes, all site overlays are checked for impact:
- If overlay is still relevant, mark as CURRENT
- If overlay contradicts new base, regenerate overlay
- Track changes independently per site

### Cross-Site Change Propagation

When a change affects multiple sites:

```
Scenario: Tosca test for Purchase Requisition is updated

Change Detected: 2024-01-20 09:30
  Source: Tosca/Create_PR v2.1 (enterprise)
  Affected Training: Layer 3 job aid + Layer 4 flow

Action for Each Site:

  SE-DC:
    Base Training: Stale (Tosca changed)
    Site Overlay: Stale (depends on base)
    Regenerate: Base + overlay
    Status: REGENERATING

  MidWest-DC:
    Base Training: Stale (Tosca changed)
    Site Overlay: Stale (depends on base)
    Regenerate: Base + overlay (includes Finance Committee override)
    Status: REGENERATING

  [Other sites...]

Result: 5 training materials regenerated, tested, and approved
        Rolled out across 8 sites within 4 hours
```

## Quality Criteria

All regenerated training must meet these standards before publication:

### Validation Criteria

1. **Tosca Alignment**
   - All steps in regenerated training match source Tosca script
   - UI element selectors all point to valid, current elements
   - Expected outcomes match Tosca validation assertions
   - No steps were omitted or invented

2. **Current System Alignment**
   - Screenshots match actual live system (pixel-level if needed)
   - Field names, button labels, menu structures all current
   - Error messages match what system actually displays
   - No references to deleted or renamed elements

3. **Consistency with Other Layers**
   - Layer 1 navigation to function matches Layer 3 starting point
   - Layer 2 process context matches Layer 3 role assignments
   - Layer 3 steps match Layer 4 in-app guidance
   - All cross-references are valid

4. **Completeness**
   - All decision points documented
   - All error conditions and solutions documented
   - All site-specific variations documented
   - All role-specific variations documented
   - Troubleshooting section covers common issues

5. **Accessibility**
   - Screenshots have alt text
   - Videos have captions
   - Color is not the only way to convey information
   - Text is readable at standard print sizes

### Approval Criteria

Before human approval, training must meet automated validation. Then SME must verify:

1. **Business Accuracy**
   - Training describes process correctly per current business rules
   - Role responsibilities are accurate
   - Approval chains are correct
   - Handoff points are accurate

2. **Clarity and Usability**
   - A new employee could follow the guide without confusion
   - No jargon without explanation
   - "Why" is explained, not just "how"
   - Examples are realistic and relevant

3. **Visual Quality**
   - Screenshots are clear and well-annotated
   - Videos are professional quality
   - Diagrams are understandable
   - Visual elements support, not confuse, the text

4. **Currency**
   - No outdated information
   - All references current
   - No mention of deprecated features
   - Site-specific variations are accurate

## Example: A Tosca Test Script Update

### Scenario

A Tosca test script for "Create Purchase Requisition" is updated:
- Previous version: Used CSS ID selector `input#material_id_field`
- New version: App refactored, ID changed to `input#mat_id_input`
- Change detected: Automatic via Tosca CI/CD pipeline

### Cascade Through Layers

```
TOSCA CHANGE DETECTED
Tosca/Create_PR v2.1 → v2.2
Change: Line 5 selector update
Timestamp: 2024-01-20 09:30 UTC

│
├─→ LAYER 1 IMPACT ANALYSIS
│   Query: "Does Layer 1 reference this Tosca script?"
│   Result: No direct reference (Layer 1 is about navigation, not UI selectors)
│   Status: No action needed
│
├─→ LAYER 2 IMPACT ANALYSIS
│   Query: "Does Layer 2 reference this Tosca script?"
│   Result: No direct reference (Layer 2 is about process context)
│   Status: No action needed
│
├─→ LAYER 3 IMPACT ANALYSIS
│   Query: "Does Layer 3 reference this Tosca script?"
│   Result: YES - Layer 3 job aid "Creating a Purchase Requisition" is directly generated from Tosca/Create_PR
│   Action: Flag as STALE
│   Regeneration: Extract new Tosca v2.2, regenerate job aid, capture new screenshots, retest selectors
│   Timeline: 20 minutes (automated)
│   New Output: Layer 3 job aid v1.1 (using new selector)
│   Validation: ✓ All selectors valid ✓ Screenshots match ✓ Steps match Tosca
│   Status: REGENERATED, awaiting human review
│
├─→ LAYER 4 IMPACT ANALYSIS
│   Query: "Does Layer 4 reference this Tosca script?"
│   Result: YES - Layer 4 WalkMe flow includes selector `input#material_id_field`
│   Action: Flag as STALE
│   Regeneration: Update WalkMe flow definition with new selector `input#mat_id_input`, test selector, validate fallbacks
│   Timeline: 5 minutes (automated)
│   New Output: WalkMe flow configuration v2.2
│   Validation: ✓ New selector works ✓ Fallbacks tested ✓ Tooltip content still valid
│   Status: REGENERATED, awaiting human review
│
└─→ LAYER 5 (THIS LAYER)
    Change Log: Entry created
    Staleness Report: Updated to show Layer 3 and Layer 4 stale/regenerating
    Dashboard: Alerts displayed

HUMAN REVIEW PHASE
Timestamp: 2024-01-20 09:45 UTC (15 minutes after detection)

  Training 1: Layer 3 Job Aid
  Reviewer: J. Smith (SME - Procurement)
  Review Time: 8 minutes
  Decision: ✓ APPROVE
  Reason: "Selector change validated, screenshots current, steps match Tosca exactly"

  Training 2: Layer 4 WalkMe Flow
  Reviewer: L. Johnson (System Admin)
  Review Time: 5 minutes
  Decision: ✓ APPROVE
  Reason: "New selector tested in staging, fallbacks confirmed, tooltip still relevant"

PUBLICATION PHASE
Timestamp: 2024-01-20 09:50 UTC (20 minutes after detection)

  Layer 3 Job Aid v1.1:
    Status: PUBLISHED
    Users: See updated job aid immediately on next page refresh
    Old version: Archived (available for audit trail)

  Layer 4 WalkMe Flow v2.2:
    Status: DEPLOYED
    Users: New selectors used for in-app guidance
    Old config: Replaced

DASHBOARD UPDATE
"Complete: Tosca/Create_PR selector updated"
"2 training materials regenerated and published"
"Time from change detection to publication: 20 minutes"
"No user-facing stale training at any time"
```

## Implementation Considerations

### Change Detection Infrastructure

**Tosca Integration:**
- Integrate with Tosca CI/CD pipeline via webhooks
- When test is updated in Git and passes CI, trigger training system notification
- Automated comparison: hash or version checking to detect changes

**SAP Configuration Monitoring:**
- Monitor change request transport pipeline (DEV → QA → PROD)
- Query SAP database periodically for configuration changes (tables RFTAB, RFSYS, T001W, etc.)
- Capture transport logs and notify training system when changes are deployed

**UI/Fiori Monitoring:**
- Automated screenshot service: take screenshots of key screens at regular intervals (daily)
- Image comparison service: detect pixel-level changes from previous screenshots
- Fiori app catalog API polling: detect new apps, updated apps, removed apps
- Element selector validation: test all selectors weekly to detect broken references

**Process Model Monitoring:**
- Signavio API polling: query process models by ID, check version numbers/timestamps
- Hash-based change detection: store BPMN file hash, detect when it changes
- Subscribe to Signavio events if available

### Regeneration Service

**Architecture:**
- Triggered by change notifications
- Runs in parallel (multiple regenerations concurrently, one per affected training item)
- Reuses generation pipelines from Layers 1-4 (same AI generation logic)
- Captures new source assets (new Tosca script, updated BPMN, etc.)
- Generates new training content

**Idempotency:**
- Should be safe to run regeneration multiple times if triggered multiple times
- If training already regenerated from version X, don't regenerate again (no new changes)
- Prevents duplicate work

**Error Handling:**
- If generation fails (AI error, missing source asset, etc.), log error and notify engineers
- Retry with exponential backoff
- If continues to fail, escalate to humans

### Validation Service

**Automated Tests:**
- Screenshot comparison (pixel-level or perceptual hash)
- Selector validation (attempt to find element using each selector)
- Reference validation (check all links, cross-layer dependencies)
- Content consistency checks (keywords, formatting, metadata)

**Metrics:**
- % of validations passing: target > 95%
- Time to validate: should be < 2 minutes per training item
- Error categories: track common failure types (selector not found, screenshot mismatch, etc.)

**Reporting:**
- Clear failure summary when validation fails
- Actionable feedback (not just "failed", but "why" it failed)

### Human Review Workflow

**SLA:** 24 hours maximum for SME review

**Tooling:**
- Dashboard showing pending review items
- Side-by-side comparison: previous version vs. regenerated version
- Approval interface with comment field
- Integration with notification system (email, Slack, etc.)

**Escalation:**
- If no review within 24 hours, auto-escalate
- Notify manager if no action within 24 hours

### Publishing Service

**Deployment Targets:**
- User-facing training portal
- LMS systems
- Mobile app
- In-app guidance system (WalkMe, etc.)
- PDF/printable guides
- Site-specific variants: separate deployments per site

**Versioning:**
- Keep version history (allow rollback if needed)
- Track which version is currently published
- Audit trail: who published, when, what changed

**Notification:**
- Users notified when updated training is available (optional)
- Training coordinators notified of successful publication
- Dashboard updated to show training as CURRENT

### Monitoring and Observability

**Metrics to Track:**
- Time from change detection to publication (target: < 24 hours)
- Validation failure rate (target: < 5%)
- Human approval rejection rate (target: < 2%)
- % of time with zero stale training (target: > 95%)
- Selector breakage incidents (target: 0 undetected)

**Alerting:**
- Alert if change detection latency exceeds 1 hour
- Alert if validation failure rate exceeds 5%
- Alert if training stuck in review > 24 hours
- Alert if publication fails

**Logging:**
- Every change event logged with timestamp, source, affected training
- Every regeneration logged (success/failure, duration, errors)
- Every validation logged (pass/fail, issues found)
- Every approval logged (approver, decision, duration)
- Every publication logged (version, timestamp, deployment targets)

---

**Document Version:** 1.0
**Last Updated:** [GENERATION_DATE]
**Monitoring Tools:** [LIST OF CHANGE DETECTION, VALIDATION, AND PUBLISHING TOOLS]
