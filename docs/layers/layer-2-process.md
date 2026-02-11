# Layer 2: End-to-End Process Understanding

**Goal:** "I know where I fit."

## Purpose

Layer 2 training demonstrates to users where their individual tasks sit within the broader business process. Users learn not only what they do, but what happens before their work, what depends on their work, and how their role contributes to the complete process. This contextual understanding increases compliance, reduces errors, and helps users understand why certain fields matter or why timing is critical.

Without Layer 2, users may perform tasks mechanically without understanding business impact. With Layer 2, they understand cause and effect across organizational boundaries.

## Source Inputs

Layer 2 training is automatically generated from the following sources:

### Signavio Process Models (BPMN)
- Complete end-to-end process flow diagrams in BPMN 2.0 format
- Swim lanes representing organizational roles and departments
- Task nodes representing specific work activities
- Decision gateways showing conditional logic
- Event triggers and completion conditions
- Data flow annotations showing information flow between tasks
- Process metadata (owner, version, effective date, site applicability)

### Role Definitions and Swim Lanes
- Official role titles and responsibilities
- Role-to-organization-unit mappings (e.g., "Purchasing Officer reports to Procurement Department")
- Role hierarchies and approval authorities
- Cross-functional role dependencies

### Organizational Data
- Department structures and reporting relationships
- Inter-site handoff patterns (e.g., SE-DC requisitions require MidWest-DC approval)
- Business unit-specific variations in process flow
- Escalation paths and exceptions handling

### Signavio Annotations
- Process descriptions and business context
- Field-level explanations within tasks
- Decision criteria for gateways (when to choose which path)
- Performance metrics and SLAs
- Risk and compliance annotations

## AI Generation Process

### Step 1: Parse BPMN Process Models
Extract all structural elements from Signavio:
- Identify all task nodes and their assigned roles (swim lanes)
- Extract all gateways and decision logic
- Locate start and end events
- Parse data objects and flow annotations
- Capture all sub-processes and reference models
- Extract timing information and SLA annotations

### Step 2: Identify All Roles and Swim Lanes
- Create a comprehensive list of every role involved in the process
- Determine the sequence in which each role participates
- Identify handoff points where work transfers from one role to another
- Document role-to-role dependencies (e.g., "Approver must review before Processor can proceed")
- Note parallel vs. sequential participation patterns
- Identify roles with conditional participation (e.g., "Compliance Officer only reviews if amount > $X")

### Step 3: Extract Handoff Points and Sequencing
- For each pair of consecutive roles, document:
  - What information passes from Role A to Role B
  - What happens if Role A does not complete their work
  - What Role B does with Role A's output
  - Timing constraints (e.g., "Role B must complete within 24 hours")
  - Communication mechanism (system notification, email, manual handoff)
- Create a detailed handoff matrix showing all role-to-role transitions
- Document what happens if a handoff fails or is delayed

### Step 4: Generate Narrated Process Overview
- Create a high-level narrative describing the complete process end-to-end
- Explain what happens before the user's role gets involved
- Explain what depends on the user's work (downstream impact)
- Identify the critical role(s) in the process
- Highlight compliance/risk points
- Explain business rationale for process structure
- Use plain-English narrative style, avoiding technical BPMN terminology

### Step 5: Generate Role-Highlighted Process Flow Diagrams
- Visually highlight the path that a specific role follows through the complete process
- Color-code or otherwise emphasize:
  - Tasks that the specific role performs (e.g., "Purchasing Officer creates requisition")
  - Tasks that depend on this role's output (e.g., "Approver reviews Purchasing Officer's requisition")
  - Decision points that affect this role
  - Waiting periods where this role is blocked by other roles
- Create a separate version for each primary role in the process
- Include side annotations explaining the highlighted path

### Step 6: Identify Role-Specific Inputs and Outputs
- For the user's specific role, document:
  - What they receive as input (from upstream roles or systems)
  - What they must produce as output (for downstream roles or systems)
  - What information they have available to make decisions
  - What information they must gather or validate
  - What information they must NOT modify (protected fields)
  - What happens if they provide incorrect output
- Use this information to create the "context wrapper" for Layer 3 (execution guides)

## Output Format

### AI-Generated Explainer Videos (Bigfoot-Style Approach)

The term "Bigfoot-style" refers to a minimal-post-production video generation approach originally used to create viral content rapidly. For Zero-Touch Training, we apply this methodology with full governance oversight, prioritizing rapid generation over cinematic polish.

#### Video Generation Pipeline

**Input:** BPMN model + role definitions + narrative annotations from Signavio

**Step 1: Script Generation**
- AI generates a narration script explaining the process end-to-end
- Script is role-aware: "As a Purchasing Officer, here's what happens in the Purchase Requisition to Goods Receipt process"
- Script includes specific numbers/facts from the BPMN (e.g., "This process typically takes 5-7 business days from requisition to goods receipt")
- Script length: approximately 1.5-2 minutes of voiceover
- Output format: Plain-text script with timing annotations

**Step 2: Visual Generation**
- Extract or generate visual elements:
  - BPMN diagram as primary visual (rendered from Signavio export)
  - Screenshots of UI screens the role will encounter (from Layer 1 navigation)
  - Callout graphics showing data flows and handoffs
  - Timeline graphics showing durations and SLAs
  - Role illustrations (simple icons/avatars representing each organizational role)
- Create visual sequence that aligns with voiceover timeline
- Minimal animation (e.g., highlighting swim lanes as they are mentioned)

**Step 3: Assembly**
- Combine script + visuals + background music into a video
- Add text overlays for key concepts
- Include visual chapter markers for quick navigation
- Generate subtitles from script
- No extensive post-production (color grading, transitions, effects); focus on clarity and speed of generation

**Step 4: Governance Review**
- Subject matter experts review script accuracy against BPMN source
- Approvers verify process description matches current business practice
- Process owner signs off on role representations and handoff descriptions
- Human review ensures accuracy but does NOT require re-shooting or extensive revision
- Approved videos are published; rejected videos are re-generated with corrections

#### Video Specifications
- Duration: 1.5-3 minutes per process
- Resolution: 1280x720 (HD) minimum
- Format: MP4 with H.264 codec for broad compatibility
- Voiceover: Clear, professional narration at natural speaking pace
- Subtitles/Captions: Full transcript in SRT format
- Audio: Background music at -12dB during voiceover, +6dB in intro/outro
- Accessibility: Color-blind friendly palette, alt text for on-screen graphics

#### Video Organization
- One primary process video per major business process (e.g., "Purchase Requisition to Goods Receipt")
- One role-specific variant per significant role in the process
- Chapter marks allow jumping to role-specific sections
- Each video includes:
  - Title slide with process name and target role
  - Introduction: "This video explains the complete Purchase Requisition to Goods Receipt process and shows you where you fit in"
  - Main content: Process walkthrough with role highlighting
  - Summary slide with key takeaways
  - Links to Layer 3 and Layer 4 resources

### Process Flow Diagrams with Role Highlighting

**Format:** SVG (scalable vector graphics) or interactive HTML

**Content:**
- Complete BPMN process diagram exported from Signavio
- Color-coded swim lanes (one color per role)
- Animated highlighting showing the path a specific role follows
- Hover tooltips explaining each task
- Icons indicating decision points, approval gates, and waiting periods
- Timeline annotations showing typical duration for each task
- Data flow arrows showing information passing between roles

**Role-Specific Variants:**
- Generate one diagram per major role
- Highlight the role's tasks in bold, with other tasks in lighter color
- Add annotations showing dependencies on upstream roles
- Show downstream consumers of this role's output
- Include error/exception paths specific to this role

**Interactive Elements (if tool supports):**
- Click on a task to reveal detailed step-by-step execution guidance (link to Layer 3)
- Click on a role to show all tasks that role performs across all processes
- Hover over handoff arrows to show timing and information exchange
- Timeline slider showing process progression in real-time scenarios

### Narrated Written Overview

For users who prefer text to video, provide a detailed written narrative:

**Structure:**
- Executive summary: 100-word overview of the process purpose and flow
- "Before your role" section: What happens upstream, what information is available when you begin
- "Your role" section: Your specific responsibilities and decision points
- "After your role" section: What depends on your output, who uses what you create, timing pressures downstream
- "Key metrics and SLAs" section: Performance expectations for this process
- "Exception paths" section: What happens if things go wrong, who handles escalations
- "Compliance and risk" section: Why this process exists, what regulations it supports, what you must never do

**Visual Support:**
- Embedded diagrams showing your role in context
- Tables showing role-to-role handoff points
- Timeline graphics showing typical duration
- Decision tree diagrams showing conditional paths

## Site-Specific Considerations

Business processes often have site-specific variations. The generation system must handle:

### Role Assignment Variations
- Some sites may have different role structures (e.g., at one site, "Materials Planner" and "Purchasing Officer" are the same person; at another, they are separate)
- Some approval hierarchies vary by location (e.g., MidWest-DC requires 3-level approval for high-value PRs, SE-DC requires only 2-level)
- Solution: Generate base process model from enterprise BPMN, then overlay site-specific role assignments with clear annotations (e.g., "At SE-DC, the Materials Manager approves directly; at other sites, this step goes through the Procurement Manager")

### Process Flow Variations
- Some sites may have additional approval gates or compliance checks not required at other locations
- Escalation paths may differ (e.g., "Contracts with Military Affairs" may only apply at SE-DC)
- Some decision branches may not be applicable at all sites
- Solution: Include conditional process paths in BPMN and visually indicate which paths apply at which sites

### Timing and SLA Differences
- Service level agreements may be site-specific (e.g., "3-day approval SLA at MidWest-DC, 5-day SLA at SE-DC")
- Process durations may differ based on site-specific system performance or staffing
- Solution: Document site-specific SLAs in narrative text and timeline graphics with callouts

### Organizational Hierarchy Overlays
- Reporting relationships and approval authorities vary by site
- Matrix organization structures may create different chains of command
- Solution: Document enterprise role definitions as baseline, then provide site-specific organizational context annotations

## Quality Criteria

All process training must meet these standards:

### Model-to-Training Accuracy
- Every task, role, decision point, and handoff in the training must exist in the source BPMN model
- Training narrative must accurately reflect the process model; no invented steps or roles
- Visual highlighting must correctly show the sequential path through the process
- Timing and SLA annotations must come directly from BPMN metadata, not estimates

### Role Representation Completeness
- All roles that appear in the BPMN are represented in the training
- No roles are omitted or downplayed
- Role sequence is accurate (role A completes before role B begins, unless parallel)
- Handoff information is complete and accurate

### Role-to-Site Mapping Accuracy
- Training explicitly documents which roles exist at which sites
- Site-specific role assignments match official organizational data
- Approval chains match current authorization matrices
- Conditional roles are clearly explained with decision criteria

### Currency and Version Control
- Training is tagged with the source BPMN version
- Generation date is clearly documented
- Any manual updates to training are flagged and dated
- Automated testing confirms the described process is executable in the current system

### Accessibility
- Videos include full captions for hearing accessibility
- Diagrams use color and shape coding (not color alone) to convey meaning
- Text overlays describe visual elements for screen reader compatibility
- Written narratives avoid process diagram jargon

### Cognitive Clarity
- Training is comprehensible to users without BPMN training
- Role responsibilities are stated simply (no jargon)
- Handoff points are visually obvious
- "Why this matters" is explained at least once per major decision point

## Example: "Purchase Requisition to Goods Receipt — Your Role as Purchasing Officer"

### Generated Video Structure

**Title Slide:**
"Purchase Requisition to Goods Receipt: The Complete Process and Your Role as Purchasing Officer"

**Narration Script (Excerpt):**
```
"Welcome. This video explains the complete purchase requisition to goods receipt process
and shows you exactly where you fit in as a Purchasing Officer.

A purchase requisition is a formal request for materials or services. It begins with a
materials planner or department manager identifying a need. That person creates a purchase
requisition in SAP and submits it for approval.

Your role, as the Purchasing Officer, typically comes next. You receive the requisition
and review it. You check whether the requested materials align with our suppliers, our
current contracts, and our budget. If everything looks good, you convert that requisition
into a purchase order — which is a formal offer to buy from a vendor.

Here's why this matters: The quality of your review directly affects the company's
spending and supplier relationships. A purchase officer who misses a cheaper available
alternative costs the company money. A purchase officer who ignores contractual obligations
exposes the company to legal risk.

After you create the purchase order, the order goes to a vendor. The vendor ships the
materials. When the shipment arrives at our dock, the receiving department inspects it
and creates a goods receipt in SAP. This completes the requisition-to-receipt cycle,
which typically takes 5-7 business days from start to finish.

Let's see this in action..."
```

**Visual Sequence:**
1. BPMN diagram appears on screen, showing all swim lanes
2. Highlight "Materials Planner" swim lane as voiceover explains requisition creation
3. Flash to screenshot of "Create Purchase Requisition" screen from Layer 1
4. Highlight "Purchasing Officer" swim lane as voiceover introduces the role
5. Highlight decision gateway: "Does requisition comply with policy?"
6. Show two paths: approved path in green, rejected path in red
7. Zoom into "Convert to Purchase Order" task
8. Flash to screenshot of the PO creation screen
9. Highlight downstream "Vendor" role and "Receiving Department" role
10. Timeline graphic showing 5-7 day typical duration
11. Summary slide with key takeaways

**Role-Specific Diagram:**
- BPMN diagram with Purchasing Officer's tasks (Review Requisition, Validate Budget, Convert to PO) in bright color
- Upstream Materials Planner task in lighter gray
- Downstream Receiving Department tasks in lighter gray
- Arrows highlighting Purchasing Officer's input sources and output destinations
- Annotations: "You depend on this upstream" and "This downstream task depends on you"

**Summary Section:**
```
"Key takeaways:
1. You are the gateway between internal requesters and external vendors
2. Your job is to ensure compliance, quality, and cost-effectiveness
3. Your output — the purchase order — is legally binding and triggers vendor fulfillment
4. The materials planner needs your PO within 3 business days; waiting longer delays the whole process
5. If something doesn't look right, ask questions before approving

Next steps:
- Layer 3 shows you exactly how to perform your tasks step-by-step
- Layer 4 provides in-app help while you're actually working
- If you have questions about your role in this process, contact your manager"
```

---

## Implementation Considerations

### Video Generation Infrastructure
- Signavio API integration to export BPMN models in standardized format
- BPMN parsing library (e.g., bpmn-js) to extract structural information
- Video generation tool (e.g., ffmpeg, Adobe Premiere API) to assemble visuals + voiceover
- Text-to-speech engine (cloud-based, e.g., Google Cloud TTS or Azure Speech Services) for voiceover generation
- Subtitle generation from TTS timing data
- Automated QC checks: verify BPMN parsing accuracy, video file integrity, subtitle synchronization

### Diagram Generation and Interaction
- Signavio export as SVG or direct API access
- SVG annotation tools to add role highlighting and callouts
- Interactive HTML layer (if implementing click-through versions)
- Responsive design for mobile viewing (processes may be viewed on phones at the shop floor)

### Governance and Review Workflow
- Generated videos → Subject Matter Expert review → Process Owner approval → Publishing
- Review dashboard showing videos pending approval, approved, rejected
- Versioning: track which BPMN version generated which video
- Comment/feedback system for reviewers
- Automated re-generation if BPMN changes

### Update Triggers
- Layer 2 training becomes stale when:
  - BPMN model is updated (new tasks, changed roles, altered sequence)
  - Signavio model version changes
  - Site-specific role assignments change
  - SLAs or performance metrics change
  - Organizational restructuring affects roles
- Stale training triggers automatic regeneration (see Layer 5)

### Performance Optimization
- Pre-generate videos at system build time, not on-demand
- Cache generated videos; only regenerate when source BPMN changes
- Provide low-bandwidth versions (lower resolution) for slow connections
- Make videos embeddable in Layer 3 and Layer 4 contexts

---

**Document Version:** 1.0
**Last Updated:** [GENERATION_DATE]
**Source System Snapshot:** [SIGNAVIO_PROCESS_MODEL_VERSION]
