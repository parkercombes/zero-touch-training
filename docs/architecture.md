# Zero-Touch Training System Architecture

## 1. System Overview

The Zero-Touch Training system is an AI-driven, automated ERP training generation platform that embeds "Training-as-Code" into the DevSecOps pipeline. Rather than manually authoring training materials, the system automatically compiles training content from authoritative source assets—process models, automated test scripts, UI metadata, and configuration data—and transforms them through an intelligent AI processing layer.

### Core Concept

```
SOURCE ASSETS → AI PROCESSING PIPELINE → TRAINING OUTPUTS
```

The system operates on the principle that training should be derived from the same artifacts that define and validate the system itself:
- **Process Models** define what should happen
- **Test Scripts** validate that it works correctly
- **UI Metadata** documents where to click and what to enter
- **Configuration Data** encodes business rules and role definitions

By making training a derivative of these source systems, the Zero-Touch Training platform ensures training is always synchronized with system reality and automatically updates whenever source data changes.

## 2. Source Systems & Data Flows

### 2.1 SAP Signavio Process Models

**Source:** Signavio Process Intelligence (connected to SAP landscape)

**Data Provided:**
- Process flow diagrams (BPMN 2.0 format)
- Task definitions with responsible roles
- Decision logic and business rules
- Data object mappings
- Process metrics and ownership metadata
- Swimlane organizational structures

**Use in Training:**
- Video script generation (process explainer videos)
- Process context for job aids
- Role-to-task assignment matrices
- Transaction flow understanding

**Access Method:** REST API / ODS export
**Frequency:** Daily synchronization

### 2.2 Automated Test Scripts (Tosca)

**Source:** Tosca test management and execution engine

**Data Provided:**
- Step-by-step test scripts with:
  - Action descriptions (click, type, select, verify)
  - UI element references (locators, IDs, XPaths)
  - Screenshot captures at each step
  - Assertion validation logic
  - Expected vs. actual results
- Test execution history and pass/fail rates
- Regression test coverage maps
- Test data and transaction codes used

**Use in Training:**
- Navigation walkthrough generation (Layer 1)
- Screenshot sourcing for visual guides
- Job aid procedure steps (Layer 3)
- WalkMe flow automation basis (Layer 4)

**Access Method:** Tosca API / Test result XML exports
**Frequency:** On each test execution (continuous)

### 2.3 UI Metadata

**Sources:**
- **SAP Fiori:** Semantic annotations, app catalogs, navigation hierarchies
- **Appian:** App definitions, interface structures, field metadata
- **SAP GUI:** Screen metadata, menu trees, transaction codes

**Data Provided:**
- Menu hierarchies and navigation paths
- Field labels and help text
- Screen layouts and functional areas
- Dialog workflows
- Authorization-gated UI elements
- Accessibility metadata

**Use in Training:**
- Walkthrough navigation instructions
- Field labeling in job aids
- Role-based UI element filtering
- Localization metadata

**Access Method:** Native APIs, metadata repositories, UI inspection
**Frequency:** Weekly synchronization

### 2.4 Configuration Data

**Source:** SAP configuration tables, transport histories, custom tables

**Data Provided:**
- Transaction codes and their associated functionality
- Authorization roles (PFCG) and permission matrices
- Organizational hierarchies and cost center mappings
- Master data (company codes, plants, storage locations)
- Custom field definitions and validations
- Site-specific customizations and variants

**Use in Training:**
- Role-specific content filtering
- Transaction code references in walkthroughs
- Site-specific overlay data (Opal)
- Business context for process explanation

**Access Method:** SAP RFC / Direct table access
**Frequency:** Weekly or on transport release

---

## 3. AI Processing Pipeline

The AI processing pipeline transforms raw source data into structured, consumable training content through a series of coordinated stages.

### 3.1 Ingestion Stage

**Responsibilities:**
- Parse and normalize diverse source formats
- Extract semantic meaning from test scripts, process diagrams, and UI metadata
- Map relationships between source data (test → UI element → transaction → authorization role)
- Validate data completeness and consistency
- Flag missing or conflicting information

**Key Operations:**

| Source Type | Parsing Method | Normalization Output |
|---|---|---|
| Tosca Test Scripts | XML parsing + screenshot OCR | Structured steps with element refs, screenshots, assertions |
| BPMN Process Models | XML to graph conversion | Task nodes with roles, data flows, decision logic |
| Fiori/Appian Metadata | API traversal | Navigation trees, field definitions, permissions |
| SAP Config Tables | RFC query + transformation | Transaction maps, role matrices, customization records |

**Data Quality Checks:**
- Verify test scripts reference valid UI elements
- Confirm process tasks map to executable transactions
- Validate role definitions against authorization data
- Cross-reference UI changes against recent transports

### 3.2 Content Generation Stage

#### 3.2.1 Navigation Walkthrough Generation (Layer 1)

**Input:** Tosca test scripts + UI metadata

**Process:**
1. Extract step sequences from test scripts
2. Enrich with UI element context from metadata
3. Generate natural language instructions from technical step definitions
4. Create visual guides using captured screenshots with annotations
5. Add explanatory context ("You are now in the Vendor Master record creation flow")

**Output Format:**
- Sequential step instructions
- Localized screenshots with pointer overlays
- Quick reference tables of common entry points
- Alternative paths and error handling notes

#### 3.2.2 Process Explainer Video Script Generation (Layer 2)

**Input:** Signavio process models + configuration context

**Process:**
1. Convert BPMN swimlanes to narrative script structure
2. Identify decision points and gate logic for explanation
3. Map process steps to business outcomes
4. Contextualize with enterprise policies and approvals
5. Generate stage-gate progression narrative
6. Align with role responsibilities

**Output Format:**
- Video script with timing markers
- Slide deck structure (process diagrams with annotations)
- Voiceover narrative
- Supporting statistics (process metrics from Signavio)
- Key learning objectives

#### 3.2.3 Role-Specific Job Aid Generation (Layer 3)

**Input:** Test scripts + process models + role authorization data

**Process:**
1. Filter test scripts to those relevant for the target role
2. Extract discrete "jobs" or tasks (e.g., "Create Purchase Requisition")
3. Combine walkthrough steps with process context
4. Add validation rules and business decision guidance
5. Include related transaction codes and menu paths
6. Format as quick-reference card or checklist

**Output Format:**
- Checklists with prerequisite steps
- Field-by-field guidance with validation rules
- Decision tables for conditional logic
- Reference information (codes, dates, responsible parties)
- Common error scenarios and resolution

#### 3.2.4 WalkMe Flow Draft Generation (Layer 4)

**Input:** Test scripts + UI metadata + role definitions

**Process:**
1. Convert Tosca test steps to WalkMe-compatible action sequences
2. Map UI element references to WalkMe selectors
3. Generate bubble content with instructional text
4. Establish branching logic for conditional paths
5. Define guidance triggers (on-demand vs. auto-launch)
6. Create targeting rules based on roles and organizational context

**Output Format:**
- WalkMe JSON or XML flow definitions
- Segment targeting rules
- Bubble content and validation logic
- Analytics tracking configuration

### 3.3 Assembly Stage

The assembly stage combines enterprise baseline content with site-specific overlays and role context to produce the final delivered training.

**Assembly Formula:**
```
Delivered Training = Enterprise Baseline
                   + Opal Site Overlay
                   + Role Context Filter
```

**Process:**
1. Load canonical enterprise training content (all process models, standard walkthroughs)
2. Apply site-specific variations from Opal overlay (see Section 6)
3. Filter by role: remove inaccessible transactions, specialize language for role competency
4. Localize: apply language, locale, and region customizations
5. Package: create delivery bundles for each training type

**Example:** A Purchase Requisition creation process:
- **Enterprise Baseline:** Standard PR creation in SAP, approval workflow
- **SE-DC Site Overlay:** Uses different cost center validation, mandatory lot/batch tracking for perishables, three-tier approval for amounts > $25K
- **Buyer Role Filter:** Hide Accounts Payable steps, emphasize cost center selection, show vendor preference rules
- **Result:** SE-DC Buyer role receives a PR creation guide with SE-DC-specific validations and Buyer-relevant information

### 3.4 Validation Stage

**Human-in-the-Loop Checkpoints:**

1. **Accuracy Verification**
   - SME review of generated content against source systems
   - Test case validation: does training accurately reflect test script flows?
   - Process correctness: does narrative match Signavio model?
   - Configuration accuracy: are role and transaction references current?

2. **Completeness Review**
   - Coverage analysis: are all required roles covered?
   - Process coverage: do walkthroughs address all major paths?
   - Metadata review: are all field definitions and help text included?

3. **Readability & Clarity**
   - Tone and vocabulary assessment for target audience
   - Terminology consistency with enterprise standards
   - Visual clarity of screenshots and annotations
   - Logical flow and prerequisite ordering

4. **Governance & Compliance**
   - No PII in training materials
   - Alignment with security and compliance policies
   - Authorization level appropriateness (role can execute content)
   - Audit trail documentation

**Approval Workflow:**
```
Content Generated → Automated Quality Checks → SME Review
→ Governance Check → Approved for Publishing
```

Validation failures trigger remediation: script modifications are flagged, content is returned to generation stage with specific correction requests.

---

## 4. Training Output Types

### Layer 1: Navigation Walkthroughs

**Purpose:** "Click here, type that, then click here"

**Format:**
- Numbered step-by-step instructions
- Annotated screenshots
- Expected results at each step
- Common mistakes and how to avoid them

**Content Length:** 2-10 minutes to navigate a transaction

**Delivery:** Web-based guides, PDF, WalkMe flows

**Example:** "Create a Purchase Requisition in SAP"
- Step 1: From SAP Easy Access, click Material Management → Purchasing → Purchase Requisition → Create
- Step 2: Enter PR type (NB for normal), purchasing group (010), purchasing organization (1000)
- (Screenshots with arrows and highlights at each step)

### Layer 2: Process Explainer Videos

**Purpose:** "Here's why this process works this way"

**Format:**
- 5-15 minute narrated videos
- Animated process flow diagrams
- Business context and decision logic
- Policy implications and approval gates

**Content Scope:**
- End-to-end process narratives
- Organizational responsibilities
- Business metrics and KPIs
- Compliance and policy context

**Delivery:** Video platform (YouTube, Vimeo, LMS)

**Example:** "Purchase-to-Pay Process Overview"
- Explains business needs: cost control, vendor management, compliance
- Shows entire process flow from PR creation through invoice matching
- Highlights approval gates and decision points
- Context on cost center hierarchy and budget control

### Layer 3: Role-Specific Job Aids

**Purpose:** "Here are all the tasks you need to do your job"

**Format:**
- Organized by job function
- Checklists with decision trees
- Quick reference cards
- Field definitions and business rules

**Content Scope:**
- All transactions relevant to a role
- Decision guidance for conditional logic
- Related information and lookup tables
- Common scenarios and edge cases

**Delivery:** PDF guides, mobile-accessible cards, in-app help

**Example:** "Purchase Manager Quick Reference"
- Create Purchase Order (with PO type decision logic)
- Release Purchase Order (with budget check procedure)
- Release GR/IR (with match rules)
- Create Payment Terms (with reference tables)
- Manage Vendor Master (authorization checks)

### Layer 4: WalkMe Flow Drafts

**Purpose:** "Real-time guidance in the application"

**Format:**
- In-application guidance flows
- Contextual help bubbles
- Field validation and masking
- Task progress indicators

**Content Scope:**
- Transactional guidance (next field, next action)
- Conditional branching (if X, then do Y)
- Validation error handling
- Success confirmation

**Delivery:** WalkMe platform, with continuous A/B testing

**Example:** "PR Creation In-App Flow"
- Auto-triggers when user opens PR creation transaction
- "Enter PR type" bubble guides first field
- On PR type selection, branch to relevant next steps
- Field validation shows errors with correction guidance
- Completion checklist confirms all required fields filled

---

## 5. Change Detection & Continuous Update

The Zero-Touch Training system continuously monitors source data for changes and automatically regenerates affected training content, with human approval gates.

### 5.1 Change Detection Mechanisms

#### Regression Test Monitoring

**Source:** Tosca test execution
**Detection Method:** Timestamp and checksum comparison

| Test Change Type | Detection | Training Impact | Trigger |
|---|---|---|---|
| New test script | Source control commit, test registry update | New training content needed | Auto-generate, flag for review |
| Modified test step | Script version change | Associated training marked stale | Regenerate with change highlights |
| New screenshot | Step execution change | Update visual guides | Auto-refresh, review snapshot changes |
| Failed test regression | Test execution failure | Investigate source data accuracy | Alert SME, halt regen pending investigation |

**Frequency:** Real-time on test execution

#### Configuration Change Detection

**Source:** SAP transport management system (TMS)
**Detection Method:** Transport release tracking, table change logs

| Config Change Type | Source | Detection | Training Impact |
|---|---|---|---|
| Authorization role change | PFCG role assignment | RFC query delta | Role-specific content regenerated |
| Transaction code modification | Customization tables | Transport log parsing | Walkthrough steps may be invalid |
| Field addition/removal | SAP DD (Data Dictionary) | Table metadata comparison | Job aid field sections updated |
| Org structure change | Master data tables | Hierarchy export delta | Approval role context updated |

**Frequency:** Weekly synchronization or on-transport release

#### UI Change Detection

**Source:** Fiori/Appian UI metadata, UI snapshots
**Detection Method:** Visual comparison, metadata versioning

| UI Change Type | Detection Method | Training Impact |
|---|---|---|
| Field label change | UI metadata property comparison | Update field references in job aids |
| Screen layout modification | Visual screenshot comparison (ML-based) | Regenerate annotated screenshots |
| Menu path restructuring | Navigation tree metadata diff | Update transaction path walkthroughs |
| Permission-gated UI changes | Role-based UI metadata filtering | Re-apply role filters and regenerate |

**Frequency:** Weekly or per release cycle

### 5.2 Automated Regeneration Workflow

```
CHANGE DETECTED
    ↓
SCOPE ANALYSIS: Which training artifacts are affected?
    ↓
AUTO-REGENERATION: Rebuild affected content
    ↓
QUALITY CHECKS: Automated validation against sources
    ↓
HUMAN REVIEW GATE: SME approval required
    ↓
STAGING: Stage updated content for publication
    ↓
PUBLICATION: Deploy to training platform
    ↓
NOTIFICATION: Alert users of updated training
```

**Change Scoping Examples:**

- **Test script step modified:** Regenerate associated navigation walkthrough and WalkMe flow
- **Authorization role changed:** Regenerate all job aids and walkthroughs for affected roles
- **Process model updated:** Regenerate process explainer video script
- **UI field label change:** Update all training content referencing that field

### 5.3 Approval Gates & Safety Mechanisms

**Auto-Approved Changes:**
- Minor updates (screenshot refresh, label text changes)
- Additive changes (new role added, content never removed)
- Formatting-only modifications

**Requires SME Approval:**
- Step sequence changes (could break user workflow)
- Role-based content filtering changes
- Process logic modifications
- Removals of content

**Requires Governance Review:**
- Changes affecting compliance training
- Authorization changes with security implications
- PII or sensitive data identification in source

**Escalation:** If multiple conflicting changes detected, pause regeneration and alert implementation team.

---

## 6. Opal Overlay Architecture

The Opal overlay system enables site-specific variations of enterprise standard processes while maintaining a single source of truth for baseline content.

### 6.1 Architecture Model

```
Enterprise Standard Process
        ↓
    +---+---+
    |   |   |
  Site1 Site2 Site3  (Opal Overlays)
    |   |   |
    +---+---+
        ↓
   Delivered Training
   (Enterprise Base + Site Overlay + Role Filter)
```

### 6.2 Overlay Data Structure

An Opal overlay is a specification of site-specific variations to enterprise standard processes.

**Overlay Record Fields:**

```yaml
Overlay:
  Site: "SE-DC"
  Process: "Purchase-to-Pay"
  Effective_Date: "2024-01-15"
  Variations:
    - Field: "PurchasingGroup"
      Enterprise: "any value"
      Site_Override: "R-SE or R-NAT only"
      Type: "validation_constraint"
      Description: "SE-DC uses only regional Southeast and National purchasing groups"

    - Field: "LotBatchTracking"
      Enterprise: "optional"
      Site_Override: "mandatory"
      Type: "field_requirement"
      Description: "SE-DC requires lot/batch tracking for all perishable items"

    - Field: "TemperatureZoneApprovalThreshold"
      Enterprise: "2-tier for > $100K"
      Site_Override: "3-tier for > $25K"
      Type: "approval_rule"
      Description: "SE-DC has stricter approval controls for perishable categories"

    - Task: "VendorApproval"
      Enterprise: "optional for vendors in vendor master"
      Site_Override: "required for all new vendors at SE-DC"
      Type: "process_gate"
      Description: "SE-DC enforces regional vendor review and food safety compliance"
```

### 6.3 Assembly Logic

During the Assembly stage (Section 3.3), overlays are applied systematically:

```
FOR EACH training artifact IN enterprise_baseline:

  LOAD: Enterprise standard content

  APPLY OVERLAY:
    IF artifact matches overlay process AND
       artifact location within affected transaction path THEN
      REPLACE/MERGE: enterprise step with overlay variation
      ANNOTATE: "[SE-DC]" markers on modified steps
    END IF

  APPLY ROLE FILTER:
    REMOVE: steps for roles without authorization
    HIGHLIGHT: role-critical steps

  PACKAGE: Create delivery artifact with base + overlays + role context
```

### 6.4 Example: Purchase Requisition at SE-DC

**Enterprise Standard Walkthrough:**
```
Step 1: Navigate to ME51N (Create PR)
Step 2: Enter PR Type (NB)
Step 3: Enter Purchasing Group
Step 4: Enter Distribution Center
Step 5: Add material lines
Step 6: Save
```

**SE-DC Overlay Modifications:**
```
Step 3: MODIFIED - Purchasing Group
  Add constraint: "Select only R-SE (Regional Southeast) or R-NAT (National)"

Step 4.5: NEW STEP - Temperature Zone (inserted before Distribution Center)
  "Temperature zone is mandatory at SE-DC for perishables"
  Show dropdown of valid temperature zones (Zone-F/Zone-R/Zone-A)

Step 5: MODIFIED - Add material lines
  Add validation rule: "All perishable materials must have lot/batch tracking enabled"
```

**SE-DC Buyer Training Output:**
```
Step 1: Navigate to ME51N (Create PR)
Step 2: Enter PR Type (NB)
Step 3: Enter Purchasing Group [SE-DC: Select R-SE or R-NAT]
Step 4: Enter Temperature Zone [SE-DC REQUIRED for perishables]
Step 5: Enter Distribution Center
Step 6: Add material lines [SE-DC: Enable lot/batch tracking for perishables]
Step 7: Save
```

**SE-DC Manager Training Output (Process Explainer):**
```
Video includes:
- Standard PR process flow
- SE-DC-specific approval gates:
  * 3-tier approval for perishable purchases > $25K (vs. enterprise > $100K)
  * Mandatory new vendor food safety review
  * Temperature zone and batch tracking validation
```

---

## 7. Integration Points

### 7.1 System Integration Map

| System | Source Data | Protocol | API/Method | Frequency | Authentication |
|---|---|---|---|---|---|
| **Signavio** | Process models (BPMN) | REST API | `/api/v1/processes`, `/api/v1/diagrams` | Daily | API Key |
| **Tosca** | Test scripts, screenshots, results | REST API + File Export | Tosca API v2.0, XML export | Real-time on execution | OAuth 2.0 |
| **SAP Fiori** | App metadata, navigation | REST OData / Native API | `/sap/opu/odata/`, FLP catalog API | Weekly | Technical user RFC |
| **Appian** | Interface definitions, fields | REST API | `/api/v18.0/applications` | Weekly | API Token |
| **SAP GUI** | Screen metadata, transaction codes | RFC / Direct Query | FM `SAPGUI_GET_SCREEN_INFO` | Weekly | RFC user |
| **SAP Config (Tables)** | PFCG roles, org hierarchy, customization | RFC / SQL Query | `SE16` FM, direct table read | Weekly | RFC user |
| **SAP TMS** | Transport releases, change logs | RFC / API | `STMSADMIN` FMs, change log tables | Per transport | RFC user |
| **WalkMe** | Flow management, publishing | REST API | `/api/v1/flows`, `/api/v1/segments` | On-demand | API Token |
| **Training LMS** | Content publishing, tracking | REST API | `/api/v1/courses`, `/api/v1/enrollments` | On-demand | OAuth 2.0 |

### 7.2 Data Flow Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    SOURCE SYSTEMS                            │
│  Signavio | Tosca | Fiori | Appian | SAP Config | TMS       │
└──────────────────────┬──────────────────────────────────────┘
                       │
                  (INGESTION)
                       │
┌──────────────────────▼──────────────────────────────────────┐
│              ZERO-TOUCH TRAINING PLATFORM                    │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  INGESTION LAYER                                     │  │
│  │  ├─ Parse Tosca scripts & screenshots               │  │
│  │  ├─ Extract BPMN process diagrams                   │  │
│  │  ├─ Read UI metadata                                │  │
│  │  └─ Ingest config & role data                       │  │
│  └──────────────────┬───────────────────────────────────┘  │
│                     │                                       │
│  ┌──────────────────▼───────────────────────────────────┐  │
│  │  AI CONTENT GENERATION LAYER                         │  │
│  │  ├─ Navigation Walkthroughs                         │  │
│  │  ├─ Process Explainer Scripts                       │  │
│  │  ├─ Job Aid Checklists                              │  │
│  │  └─ WalkMe Flow Definitions                         │  │
│  └──────────────────┬───────────────────────────────────┘  │
│                     │                                       │
│  ┌──────────────────▼───────────────────────────────────┐  │
│  │  ASSEMBLY & VALIDATION LAYER                         │  │
│  │  ├─ Apply Opal overlays                              │  │
│  │  ├─ Filter by role                                  │  │
│  │  ├─ Validate against source data                    │  │
│  │  └─ Human review checkpoints                        │  │
│  └──────────────────┬───────────────────────────────────┘  │
│                     │                                       │
│  ┌──────────────────▼───────────────────────────────────┐  │
│  │  CHANGE DETECTION & CONTINUOUS UPDATE                │  │
│  │  ├─ Monitor test script changes                      │  │
│  │  ├─ Track config modifications                       │  │
│  │  ├─ Detect UI updates                               │  │
│  │  └─ Auto-trigger regeneration                       │  │
│  └──────────────────┬───────────────────────────────────┘  │
│                     │                                       │
└─────────────────────┼───────────────────────────────────────┘
                      │
              (PUBLISHING & DELIVERY)
                      │
┌─────────────────────▼───────────────────────────────────────┐
│              DELIVERY SYSTEMS                                │
│  WalkMe | LMS | PDF Guides | Training Portal | Mobile App   │
└─────────────────────────────────────────────────────────────┘
```

---

## 8. Security & Governance

### 8.1 Data Privacy & PII Protection

**Policy:** Training materials contain NO personally identifiable information (PII).

**Enforcement:**
- Automated scanning: All generated content checked for PII patterns (names, SSNs, email addresses)
- Source data filtering: Before ingestion, sensitive fields masked or excluded
  - Test data sanitized: Replace actual employee/vendor names with placeholders
  - Screenshots scrubbed: OCR and manual review to remove visible PII
  - Configuration data limited to transaction codes and role names, not employee assignments
- Content review: Human reviewers verify no PII in training outputs before publication
- Regular audits: Monthly review of generated content for accidental PII leakage

### 8.2 Role-Based Access Control (RBAC)

**Pipeline Access Roles:**

| Role | Permissions | Use Case |
|---|---|---|
| **Admin** | All operations, system configuration | Platform operations, release management |
| **Content Generator** | Trigger regeneration, view generated content | SME automation, content updates |
| **SME Reviewer** | Approve/reject generated content, provide feedback | Subject matter expert validation |
| **Governance Lead** | Approve compliance-related content, audit logs | Security, compliance oversight |
| **Viewer** | View published training, access reports | End users, reporting |

**Source System Permissions:**
- Signavio access: Read-only, API key rotation quarterly
- Tosca access: Read test results only, no write permissions
- SAP access: Technical user account with table read-only permissions
- WalkMe/LMS: Administrative token scoped to publishing operations only

### 8.3 Audit Trail & Accountability

**Logged Events:**

```
INGESTION:
  ├─ Data source accessed (timestamp, user, system)
  ├─ Records imported (count, data hash)
  └─ Quality check results

CONTENT GENERATION:
  ├─ Generation initiated (user, process, parameters)
  ├─ AI model version, generation timestamp
  ├─ Content output (artifacts generated, lines of content)
  └─ Generation warnings/errors flagged

VALIDATION:
  ├─ Review started (reviewer, date, process)
  ├─ Issues identified and resolved
  ├─ Final approval (reviewer, timestamp, notes)
  └─ Rejection with remediation guidance (if applicable)

ASSEMBLY & PUBLICATION:
  ├─ Overlay application (site, variations applied)
  ├─ Role filtering (roles applied, artifact size delta)
  ├─ Publication (platform, timestamp, delivery channels)
  └─ Change notifications (users/teams alerted)

CHANGE DETECTION & REGEN:
  ├─ Change detected (source system, change type, timestamp)
  ├─ Regen triggered (user or automatic)
  ├─ Content changes (diff summary)
  └─ Re-approval (if required)
```

**Audit Access:**
- All events queryable by timestamp, user, process, system
- Immutable audit log (append-only, no deletion or modification)
- Monthly reports generated for governance review
- 7-year retention per regulatory requirements

### 8.4 Human-in-the-Loop Governance

**Content Approval Workflow:**

```
Generated Content
      │
      ├─→ Automated Quality Checks
      │   ├─ Syntax validation (no malformed instructions)
      │   ├─ PII scanning (no sensitive data)
      │   ├─ Source alignment (content matches test scripts, processes)
      │   ├─ Role consistency (role-specific content filtered correctly)
      │   └─ Format validation (all output types well-formed)
      │
      ├─→ SME Content Review (business correctness)
      │   ├─ Verify against source system reality
      │   ├─ Assess clarity and accuracy
      │   ├─ Check for missing edge cases or variations
      │   └─ Approve or request modifications
      │
      └─→ Governance & Compliance Review (security, policy)
          ├─ Confirm no PII or restricted information
          ├─ Verify role-based access controls applied
          ├─ Assess compliance implications
          └─ Final approval or escalation
```

**Approval Decision Options:**
- **Approved:** Content published immediately
- **Approved with Changes:** Minor automated fixes applied (label corrections, screenshot refresh)
- **Needs Modification:** Specific issues identified, routed back to generation stage
- **Escalation:** Unresolvable conflicts escalated to implementation team

### 8.5 Compliance & Risk Management

**Training Compliance:**
- All training content aligned with enterprise policies and procedures
- Authorization-level appropriateness verified (user can execute trained content)
- Compliance training flagged for special handling (audit evidence)
- Change tracking ensures training updates synchronized with policy changes

**System Compliance:**
- GDPR: No PII, no unnecessary data retention
- SOX/HIPAA: Audit trail for compliance-sensitive content
- Data residency: Source data locality respected, no cross-border data transfer
- Access controls: RBAC enforced on all pipeline operations

**Risk Assessment:**
- Regular penetration testing of pipeline
- Source system access audited quarterly
- API key rotation and credential management per policy
- Separation of duties: content generation, review, and publishing by different roles

---

## 9. Deployment & Operations

### 9.1 Environment Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                      DEVELOPMENT                             │
│  Source System Sandboxes | Pipeline v.next | Test Workflows  │
└──────────────────────────────────────────────────────────────┘
                           │ (Test release)
                           ▼
┌──────────────────────────────────────────────────────────────┐
│                      STAGING                                 │
│  Clone of Prod Config | Pre-publication Preview | Validation │
└──────────────────────────────────────────────────────────────┘
                           │ (Approved release)
                           ▼
┌──────────────────────────────────────────────────────────────┐
│                      PRODUCTION                              │
│  Live Pipeline | Continuous Monitoring | Published Training  │
└──────────────────────────────────────────────────────────────┘
```

### 9.2 Performance Baseline

| Operation | Target Duration | Notes |
|---|---|---|
| Ingest Tosca scripts (1000 test cases) | < 15 minutes | Parallel batch processing |
| Generate navigation walkthroughs (50 transactions) | < 30 minutes | AI model inference |
| Generate process videos (5 processes) | 2-4 hours | Includes video rendering |
| Apply Opal overlays | < 5 minutes | Per site, per process |
| Full validation cycle | < 2 hours | Includes all checks |
| Publish to WalkMe | < 10 minutes | Per batch |

### 9.3 Monitoring & Alerting

**Key Metrics:**
- Source system connectivity (all systems reachable)
- Ingestion success rate (> 99% of records parsed cleanly)
- Content generation quality (< 2% rejected in SME review)
- Publication timeliness (< 2 hours from approval to live)
- Change detection lag (< 1 hour from test/config change to detection)

**Alerting Thresholds:**
- Source system connection failure: Immediate alert to operations
- Ingestion error rate > 5%: Page on-call engineer
- SME rejection rate > 10%: Escalate to product team
- Publication failures: Halt pipeline, alert governance

---

## 10. Future Roadmap & Extensibility

### 10.1 Planned Enhancements

- **Multi-language support:** Automated translation of generated training content
- **Video generation:** AI-powered video synthesis from process models and screenshots
- **Mobile-first delivery:** Optimize training for mobile/tablet consumption
- **Learning analytics:** Track training effectiveness and user performance correlation
- **Personalization:** Adaptive training paths based on user role and learning history
- **Integration with peoplesoft, Oracle Cloud:** Extend beyond SAP landscape

### 10.2 Extensibility Points

The architecture supports addition of new:
- **Source systems:** Add ingestion parsers for new process/test frameworks
- **Content types:** Implement new output template generators
- **AI models:** Swap or upgrade underlying language/image models
- **Delivery platforms:** Integrate with new training/collaboration platforms
- **Overlay systems:** Support additional variation dimensions (country, org size, industry)

---

## 11. Video Pipeline Architecture (Veo 3 + Native Audio)

### 11.1 Overview

The social media video component (Layer 2 explainer videos) has evolved through three generations:

| Version | Script | Audio | Video | Cost |
|---|---|---|---|---|
| v2 (sandbox) | Hardcoded | libflite (local TTS) | ffmpeg static frames | Free |
| Mark 1 (Bigfoot) | Claude-generated | OpenAI TTS (nova) | DALL-E 3 stills | ~$0.90 |
| Mark 2 (Veo 3) | Claude-generated | Veo 3 native (lip-synced) | Google Veo 3 clips | ~$3.60–$15.60 |

### 11.2 Veo 3 Native Audio Architecture

Google Veo 3 generates video and audio together from a single prompt. When dialogue is embedded in the video prompt, Veo produces natural lip movement and voice in sync — no separate TTS step required.

```
video_prompt (with embedded dialogue)
           │
           ▼
    Google Veo 3 API
           │
           ▼
  raw_clip.mp4 (video + lip-synced audio, single file)
           │
           ▼
    compose_scene()
    ffmpeg: -map 0:v -map 0:a?
    (preserves native audio, re-encodes to H.264/AAC)
           │
           ▼
  scene_NNN.mp4
           │
           ▼
    concat_scenes()
    ffmpeg concat demuxer
           │
           ▼
  bigfoot_goods_receipt_veo3.mp4  (720×1280, 9:16)
```

The critical implementation detail in `compose_scene()`:

```python
"-map", "0:v",
"-map", "0:a?",   # native Veo audio — the ? skips gracefully if no audio track
```

Earlier versions used `-map 1:a` to overlay a separately generated TTS file, discarding Veo's lip-synced audio. The `veo3_test_clip.py` validator skipped `compose_scene` entirely (downloading raw output), which is why single-clip tests sounded correct while the full pipeline did not.

### 11.3 Character Cast System

Each of the 13 training scenes is assigned to one of four named Bigfoot employees. Character identity is embedded in the video prompt as a multi-sentence physical description, giving Veo enough detail to maintain visual consistency across clips.

```python
DAVE = ("Dave, a 7-foot sasquatch with dark reddish-brown fur, broad shoulders, "
        "a wide friendly face with amber eyes, wearing a bright orange GLOBALMART SE-DC "
        "safety vest and a yellow employee ID badge clipped to the left strap")

SANDRA = ("Sandra, a 7-foot sasquatch with silver-grey fur, sharp focused eyes, "
          "wearing a red COMPLIANCE safety vest with a laminated badge on a lanyard, "
          "clipboard in hand, authoritative posture")

MARCUS = ("Marcus, a 7-foot sasquatch with jet-black fur and a relaxed confident posture, "
          "wearing a yellow RECEIVING safety vest and a blue hard hat, "
          "breath visibly fogging in the cold air")

KEISHA = ("Keisha, a 7-foot sasquatch with auburn reddish fur and precise attentive manner, "
          "wearing a white QUALITY ASSURANCE safety vest with a QA logo patch, "
          "holding a tablet computer")
```

Scene-to-character mapping is by domain ownership: Dave handles intro/document entry/posting/outro, Sandra owns compliance verification, Keisha owns QA inspection, Marcus owns cold chain/temperature zone.

### 11.4 POC Cut

`video_render_veo3_poc.py` is a 3-scene subset for development and daily-quota-constrained testing. It imports character constants and utility functions from the main script and runs independently:

```
Scene 01 — Dave (intro)
Scene 05 — Sandra (movement type 101 lesson)
Scene 13 — Marcus (outro)
Estimated cost: ~$3.60 (Veo 3 Fast, 3 × 8s × $0.15)
```

### 11.5 Quota and Tier Notes

- Veo 3 access requires Google AI Studio with billing enabled
- Default free tier exhausts quickly (≈2–3 clips)
- Tier 2 requires $250 cumulative GCP spend + 30 days, then manual request at aistudio.google.com
- `veo-3.0-fast-generate-001` ($0.15/s) vs `veo-3.0-generate-001` ($0.40/s)
- Silent empty-result failure: Veo occasionally returns `operation.done=True` with no error but empty `generated_videos` list — handled inside the retry loop with 30-second wait

---

## 12. UI Trainer Architecture

### 12.1 Scenario Pack Pattern

The UI trainer (`ui_trainer.py`) is a generic HTML simulation engine. All warehouse-specific content lives in Python modules under `poc/generators/scenarios/`.

```
ui_trainer.py                   # generic engine — HTML player, screen navigation, HUD
     │
     ├── scenarios/base.py       # shared Pillow drawing helpers (SAP Fiori chrome)
     │
     └── scenarios/<name>.py     # scenario pack
             │
             ├── SCENARIO dict   # metadata: id, title, site, process, handling_profile
             ├── SCREEN_GENERATORS  # dict mapping screen names → generator functions
             └── generate_screens(out_dir)  # calls all generators, writes PNGs
```

The engine loads the scenario module dynamically:

```python
import importlib
mod = importlib.import_module(scenario_module)  # e.g. "scenarios.sedc_goods_receipt"
scenario = mod.SCENARIO
mod.generate_screens(screens_dir)
```

### 12.2 SAP Fiori Chrome (base.py)

`scenarios/base.py` provides a consistent SAP Fiori visual language across all scenario packs using Pillow:

- Shell bar (dark blue, hamburger menu, user avatar)
- Field inputs with label, border, optional amber highlight and underline
- Dropdown fields with caret arrow
- Primary/secondary buttons (blue, amber highlight state)
- Table headers and row rendering with per-column highlight
- Checkboxes with check mark
- Card containers with optional title and divider
- Status banners (green success / red error)

All colors follow the SAP Fiori palette: `#0070F2` (primary blue), `#033D80` (shell), `#E87600` (amber/hotspot), `#107E3E` (success green), `#BB000B` (error red).

### 12.3 Handling Profiles

| Profile | Scenario File | Site Example | Distinguishing Fields |
|---|---|---|---|
| `perishable` | sedc_goods_receipt.py | GlobalMart SE-DC | Lot/batch, temp zone, cold chain, QI mandatory |
| `standard_dry` | standard_dry.py | Apex Auto Parts DC | Basic 6-step receipt, no regulatory layer |
| `regulated_pharma` | regulated_pharma.py | Cardinal Health DC | Lot + expiry + CoA, QI hold, GxP language |
| `hazmat` | hazmat.py | ChemCo Industrial DC | UN number, hazmat class, DOT/OSHA mandatory fields |
| `serialized` | serialized.py | TechVault DC | Serial number scan, CAGE-01 secure storage, manager approval |

### 12.4 Adding a New Scenario

1. Copy `scenarios/standard_dry.py` as a starting point
2. Update the `SCENARIO` dict: `id`, `title`, `site`, `process`, `handling_profile`, `num_screens`
3. Update `SCREEN_GENERATORS` with the screens relevant to the new process
4. Run: `python3 ui_trainer.py scenarios.<your_module_name>`
5. Output lands in `poc/output/ui_trainer/<scenario_id>/`

No changes to `ui_trainer.py` or `base.py` are required for a new scenario.

### 12.5 Game Layer (Planned)

The current UI trainer renders a static HTML simulation. The following game mechanics are planned for the next development phase:

- **Level system** (0=orientation, 1=guided, 2=semi-guided, 3=challenge/timed)
- **XP and achievement badges** stored in session JSON
- **Timer** in Level 3 with score formula: `base × time_bonus × accuracy_multiplier`
- **Narrative premise cards** before each Level 3 scenario
- **Error consequence explanations** (Layer 5 content delivered in-moment)
- **Confetti animation** on successful posting
- **Site-level leaderboard** via lightweight file-based score store

See `docs/game-design-vision.md` for full design rationale, real-world benchmarks, and implementation priority order.

---

## 13. Glossary

**Baseline (Enterprise Standard):** Canonical, standardized process and training content applicable across all sites

**Opal Overlay:** Site-specific variation specification that modifies enterprise baseline for local context

**SME (Subject Matter Expert):** Business user responsible for validating generated training content

**Test Script:** Automated test case defining step-by-step actions and validations

**Training-as-Code:** Practice of deriving training materials from source system artifacts (tests, models, configs)

**Walkthrough:** Step-by-step navigation guide with screenshots for executing a transaction

**WalkMe:** In-application guidance platform providing contextual help and task automation

**Zero-Touch Training:** Fully automated training generation with no manual content authoring required

---

## Document Information

**Version:** 1.0
**Last Updated:** 2024
**Audience:** Technical architects, system engineers, training operations team
**Classification:** Technical Architecture Reference
