# Layer 3: Role-Specific Execution

**Goal:** "I can do my job."

## Purpose

Layer 3 provides the detailed, step-by-step execution guidance users need to perform their assigned tasks. Unlike Layer 2 (which shows context), Layer 3 focuses entirely on how to execute: what to click, what to type, what to validate, what to do if something goes wrong. Each Layer 3 guide is a job aid — a short reference document a user consults while actively performing work.

Layer 3 is the core of the Zero-Touch Training system. It is generated directly from Tosca automated test scripts, ensuring every step has been validated against the live system before training is published.

## Source Inputs

### Tosca Automated Test Scripts (Primary Source)
Tosca test scripts are the authoritative source for execution guidance. Each test script:
- Defines the complete sequence of actions required to complete a task
- Specifies exact UI element selectors (CSS, XPath, Fiori element IDs)
- Includes validation logic proving each step succeeded
- Contains business data (typical values, edge cases, validation rules)
- Documents what the system does in response to each action
- Identifies conditional branches (e.g., "If amount > $10,000, approval is required")
- Captures error messages and how to resolve them

Example Tosca test script structure:
```
Test: Create_Purchase_Requisition_Standard
  Step 1: Navigate to Create PR app
  Step 2: Enter Material ID (validation: must exist in catalog)
  Step 3: Enter Quantity (validation: must be > 0)
  Step 4: Select Plant (validation: user's plant or authorized plants only)
  Step 5: Enter Delivery Date (validation: must be >= today)
  Step 6: Click Submit
  Step 7: System displays Confirmation message: "PR [Number] created"
  Step 8: Verify PR appears in Requisition Worklist with "Open" status
```

### UI Field Mappings
- Technical field names (SAP field IDs, Fiori element IDs, Appian field mappings)
- UI element selectors (CSS classes, XPath expressions, semantic locators)
- Label text and placeholder text displayed to users
- Field data types (string, numeric, date, dropdown, etc.)
- Required vs. optional field indicators
- Default values per role or per site

### Business Rules and Validation Logic
- Input validation rules (e.g., "Quantity must be > 0 and < 999,999")
- Cross-field validation (e.g., "If Delivery Date is urgent, Expedite checkbox must be checked")
- Role-based field visibility (e.g., "Cost Center field is hidden for Material Planners")
- Authorization rules affecting field population or task completion
- SLA checks (e.g., "System prevents approval after 5-day waiting period")

### Field Help Text and Tooltips
- Original system help text for fields (from SAP/Fiori)
- Business context explanations
- Examples of correct input
- Common mistakes and how to avoid them

## AI Generation Process

### Step 1: Parse Tosca Test Scripts
Extract all structural information from test script files:
- Parse test step definitions to identify:
  - Target UI element (CSS selector or technical identifier)
  - Action type (click, input text, select from dropdown, date picker, etc.)
  - Input data (what the user should type or select)
  - Expected system response/validation result
  - Branching conditions (if validation fails, what happens next)
- Identify all test data used in scripts:
  - Typical values (e.g., "Material ID 12345 is a typical internal purchase item")
  - Edge cases (e.g., "Negative materials require special approval")
  - Error conditions (e.g., "Entering an invalid material ID causes error message X")
- Extract all validation assertions to understand success criteria

### Step 2: Extract Action Sequences into Plain Language
Convert Tosca's technical syntax into readable steps:
- Transform technical UI selectors into user-friendly location descriptions
  - Tosca: `Click element "//button[@aria-label='Create']"`
  - Training: `Click the "Create" button in the upper right`
- Translate system responses into user-understandable outcomes
  - Tosca: `Assert element "//div[@id='success-msg']" is visible`
  - Training: `You should see a green confirmation message saying "Purchase Requisition created"`
- Convert validation logic into user instructions
  - Tosca: `Validate: quantity > 0 AND quantity < 999999`
  - Training: `Quantity must be a positive whole number. The maximum is 999,999 units`

### Step 3: Create Field-Level Guidance
For each input field, generate context and help:
- **What to enter:** Clear examples of correct values
- **Why it matters:** Business context for why this field is important
- **What happens if wrong:** Specific error message the user will see, and how to fix it
- **Dependencies:** What other fields this field affects, or what affects it
- **Site-specific variations:** If this field behaves differently at different sites (using Opal overlay logic)

Example field guidance structure:
```
Field: Material ID
  What to enter: The 18-digit material number from your parts catalog
  Example: "012345000000789012"
  Where to find it: Check your parts list or ask your supervisor
  Why it matters: The system uses Material ID to look up price, availability, and lead time

  What happens if wrong:
    - If you enter a non-existent Material ID: System displays "Material not found"
      and prevents you from proceeding. Check the catalog and try again.
    - If you enter an inactive material: System displays a warning "This material
      is retired as of [date]" and requires supervisor approval to use it anyway.

  Special cases:
    - Some materials require special approval if you are not the material owner
    - Hazardous materials trigger additional compliance questions

  Variation - Anniston site: At Anniston, the Material ID field auto-populates
    if you enter the material name instead. At other sites, you must know the ID.
```

### Step 4: Translate Test Data into Usage Scenarios
Use test data from Tosca to create realistic examples:
- Take common test cases from Tosca scripts and create realistic scenarios
  - "Standard Purchase Requisition" (typical approval flow)
  - "Expedited Materials" (high-urgency path with special approval)
  - "Budget Override Required" (when normal budget is exceeded)
  - "Multi-Site Sourcing" (when material needs come from multiple plants)
- Document what values Tosca used and why (common cases vs. edge cases)
- Create separate job aids for common variations (e.g., "Creating a Rush Purchase Requisition")

### Step 5: Apply Opal Overlays for Site-Specific Variations
Integrate site-specific variations identified by Opal metadata:
- Check if any Tosca test variants exist for different sites
  - If Rome has different validation rules than Anniston, Tosca may have separate test scripts
  - If field defaults differ by site, extract both configurations
- For each site, document:
  - Enterprise baseline (standard field requirements, validation, behavior)
  - Site-specific overlay (what changes at this site and why)
- Explicitly flag overlays in the generated job aid
  - "At Anniston, step 5 differs from the enterprise standard..."
  - "This field is required at all sites except Rome..."

### Step 6: Structure as Short Job Aids (1-2 Pages)
Create focused guides organized by task:
- One job aid per atomic task (one user action that accomplishes a business goal)
- Examples of atomic tasks:
  - "Creating a Purchase Requisition"
  - "Approving a Purchase Requisition"
  - "Rejecting a Purchase Requisition and Requesting Changes"
  - "Canceling a Purchase Requisition in Process"
- Not one giant guide for entire role (too overwhelming); instead, many small, focused guides

### Step 7: Generate Supporting Materials
Create additional content derived from Tosca and UI metadata:
- **Decision trees:** For roles that make approvals or rejections, create visual flowcharts showing decision logic
  - "If amount < $5,000, approve immediately"
  - "If amount $5,000-$50,000, route to approver"
  - "If amount > $50,000, route to finance committee"
- **Field reference sheets:** Tabular format listing every field in a task, what it means, typical values
- **Checklist versions:** For compliance-critical tasks, create checkoff lists (e.g., "Before submitting a high-value PR, verify: [ ] Budget approved, [ ] Supplier verified, [ ] Delivery date realistic")

## Output Format

### Short Job Aids (Primary Output)

**Page Count:** 1-2 pages (printed or PDF)

**Standard Structure:**

```
[Task Title]
Goal: [What user accomplishes when they complete this task]
Time Required: [Typical duration]
Prerequisites: [What must be true before starting this task]

---

STEP-BY-STEP INSTRUCTIONS:

Step 1: [Actionable instruction + what to expect]
  [Annotated screenshot showing where to click, what to enter]
  Expected result: [How you know step 1 succeeded]

Step 2: [Actionable instruction + what to expect]
  [Annotated screenshot or table showing field values]
  Expected result: [How you know step 2 succeeded]

[... continue for all steps ...]

---

DECISION POINTS [if applicable]:
If [condition], then [action]
If [condition], then [action]

---

FIELD REFERENCE:
[Table showing each field: Name | What to Enter | Why It Matters | Common Mistakes]

---

TROUBLESHOOTING:
Q: [Common problem] → A: [Solution]
Q: [Common problem] → A: [Solution]

---

RELATED GUIDES:
- [Link to other Layer 3 guides in the workflow chain]
- [Link to Layer 2 process context]
- [Link to Layer 4 in-app assistance]
```

### Annotated Screenshots

**Screenshot Specifications:**
- Resolution: 1920x1080 minimum (so details are legible when printed)
- Annotation style: Professional boxes and arrows, consistent color scheme
- Clarity: Highlight the specific UI element the user should interact with
- Context: Show enough of the surrounding UI that user can verify they're in the right place

**Annotation Types:**
- Red box: "Click here" or "Find this field"
- Blue arrow: "Then do this"
- Green highlight: "You should see this result"
- Yellow circle: "Pay special attention to this"
- Text label: "This is the field name"

### Decision Trees / Flow Diagrams

For decision-intensive tasks, supplement step-by-step guides with visual logic:

```
User Has PR Requisition Ready to Approve
    |
    v
Amount < $5,000?
    |--YES--> Auto-approve (no further approvers needed)
    |         Go to Step 7: Submit Approval
    |
    |--NO --> Amount < $50,000?
              |--YES--> Route to Procurement Manager Approval
              |         Go to Step 6: Submit for Review (Procurement Manager)
              |
              |--NO --> Amount > $50,000?
                        |--YES--> Route to Finance Committee
                        |         Go to Step 5: Submit for Finance Review
```

### Field Reference Table

Create a scannable reference for all fields in a task:

| Field Name | What to Enter | Data Type | Required? | Why It Matters | Common Mistakes |
|---|---|---|---|---|---|
| Material ID | 18-digit material code from catalog | Text (18 digits) | Yes | Links to pricing and availability | Entering 17 or 19 digits causes error |
| Quantity | Number of units needed | Positive integer | Yes | Determines order size and lead time | Entering 0 or negative numbers is invalid |
| Plant | Choose from dropdown | Dropdown | Yes | Determines which warehouse ships the material | Selecting wrong plant sends to wrong location |

### Checklist Format

For approval or compliance-sensitive tasks:

```
PURCHASE REQUISITION APPROVAL CHECKLIST

Before you approve this PR, verify all of the following:

☐ Material ID is valid (check against catalog)
☐ Quantity is reasonable for intended use
☐ Delivery date is realistic (not in the past)
☐ Budget has been allocated (confirm with finance)
☐ Supplier is authorized (check approved vendor list)
☐ For amounts > $50K: Procurement Manager pre-approved
☐ For international shipping: Customs documentation is prepared
☐ For hazardous materials: Safety approval obtained

Notes: [Space for user to document exceptions]

Approver Name: ___________________   Date: ___________
```

### Site-Specific Job Aid Variants

When significant site-specific variations exist, create separate job aids:

**Approach 1: Single Guide with Opal Overlay**
- Write a single guide using enterprise standard as baseline
- Use callout boxes to show site-specific variations
- Example: "At Anniston, the Plant field defaults to 'Anniston_Main'; at Rome, you must manually select 'Rome_Central'"

**Approach 2: Separate Guides per Site**
- If variations are extensive, create separate guides per site
- Title includes site name: "Creating a Purchase Requisition at Anniston"
- Reduces cognitive load by not mixing multiple variations
- Use when variations affect multiple steps

## Site-Specific Considerations

### Field Configuration Variations
- Some fields are required at all sites; others are optional at some sites
- Default values differ by site (e.g., "Plant" field auto-populates with site's plant code)
- Dropdown options vary by site (e.g., Cost Centers available at Rome differ from Anniston)
- Solution: Document enterprise baseline, then overlay site-specific requirements with clear visual distinction

### Approval Workflow Variations
- Approval chains differ by site and by dollar amount ranges
- Some sites have additional approval gates (compliance, security)
- Some approval types are automated at one site, manual at another
- Solution: Create separate job aids for each approval scenario, clearly labeled with site applicability

### Integration Differences
- Some sites may integrate with external systems (e.g., "At Rome, approved PRs automatically sync to the vendor portal")
- Different sites may use different payment terms or shipping providers
- Some sites have additional compliance requirements
- Solution: Document integration steps in site-specific job aids

### Validation Rule Variations
- Some sites have stricter quantity limits or budget caps
- Some sites require additional data fields for compliance
- Delivery date rules may vary (e.g., Rome requires 10-day lead time minimum, Anniston 5 days)
- Solution: Call out validation rules in step-by-step instructions with site context

### User Experience Variations
- Screen layouts may differ due to local configuration
- Report outputs may have different formats per site
- Navigation may vary if sites have different menu customizations
- Solution: Use site-specific screenshots in job aids; do not use generic screenshots if sites differ visually

## Quality Criteria

All execution training must meet these standards:

### Tosca Alignment
- Every step in the job aid must correspond to a step in the source Tosca script
- UI element references must be accurate (selectors work, element exists)
- Expected results must match what Tosca validates (if Tosca checks for "success message", training must tell user to expect that message)
- No invented steps that don't appear in Tosca
- All error handling paths in Tosca must be documented in "Troubleshooting" section

### Executability
- Every job aid must be walkable end-to-end using a test user account
- QA validation: Walk each guide using multiple roles and on multiple sites where variations exist
- All screenshots must be current (not stale or from previous system versions)
- No references to fields that no longer exist or have been renamed

### Clarity for Diverse Audience
- Language must be accessible to users with varying technical backgrounds
- Technical field names from SAP (e.g., "EKKO") must be supplemented with human-readable labels
- No assumptions about prior ERP experience
- "Why it matters" explanations help users understand business purpose, not just mechanics

### Completeness
- Every field in the actual task must be described in the field reference
- Every decision point in the Tosca test must be represented
- All error messages the system might display must be documented in "Troubleshooting"
- All site-specific variations must be identified and documented

### Currency
- Job aids must be regenerated when:
  - Tosca test scripts change (updated steps, new validation rules, changed error messages)
  - UI elements change (field renamed, selector becomes invalid, layout reorganized)
  - Business rules change (new approval thresholds, new required fields)
  - Site configurations change (new default values, new approval requirements)
- Each job aid should include source Tosca script version and generation date

### Accessibility
- Screenshots must have alt text
- Color must not be the only way to convey information
- Text must be large enough to read (10pt minimum for printed guides)
- Tables and lists must be clearly structured for screen reader compatibility

## Example: "Creating a Purchase Requisition — Anniston"

### Generated Job Aid Structure

---

**CREATING A PURCHASE REQUISITION**

**Goal:** Submit a formal request for materials or services into the procurement system
**Time Required:** 5-10 minutes
**Prerequisites:**
- You have a Materials Planner or Purchasing Officer role
- You know the Material ID of what you need
- You know the quantity and delivery date required
- Your department's budget is available for this purchase

---

**STEP-BY-STEP INSTRUCTIONS:**

**Step 1: Open the Create Purchase Requisition App**
1. Open your SAP Fiori home page
2. Locate the "Procurement" section
3. Click the "Create Purchase Requisition" tile
4. The app should open showing an empty form

[Screenshot: Fiori home with Procurement section highlighted, Create PR tile circled in red]

Expected result: You see a form with fields for Material ID, Quantity, Plant, Delivery Date, and other options. The form is empty and ready for input.

**Step 2: Enter the Material ID**
1. Click in the "Material ID" field (top left of the form)
2. Type the 18-digit material code (e.g., "012345000000789012")
3. Press Tab or click elsewhere; the system will look up the material

[Screenshot: Material ID field highlighted with example value entered]

Expected result:
- If the material exists, the system displays the material name below the ID field
- If the material does not exist, the system displays a red error message "Material Not Found"

**What if the material does not exist?**
- Check your parts list to verify the correct material ID
- If you're unsure which material to order, ask your supervisor or Materials Manager
- Do not proceed until the material is found

**Step 3: Enter the Quantity**
1. Click in the "Quantity" field
2. Enter the number of units you need (e.g., "100")
3. Press Tab; the system validates that the quantity is valid

[Screenshot: Quantity field highlighted with example value]

Expected result: The system accepts the number and moves to the next field. You should see no error messages.

**Common mistakes:**
- Entering "0" (zero) → System displays error "Quantity must be > 0"
- Entering more than 999,999 units → System displays warning "Quantity exceeds normal range; confirm with supervisor"
- Entering decimal values (e.g., "10.5") → System rounds to nearest whole number and displays warning

**Step 4: Select the Plant**
1. Click in the "Plant" field
2. At Anniston: The Plant field automatically shows "Anniston_Main" and you cannot change it
3. At other sites: The field is empty; click the dropdown arrow and select your plant from the list

[Screenshot: Plant field dropdown open, showing available plants]

Expected result: You see your plant name selected in the Plant field. The system prevents selection of other plants (at Anniston) or allows any plant (at other sites).

**Step 5: Enter the Delivery Date**
1. Click in the "Delivery Date" field
2. Enter the date you need the material (e.g., "2024-03-15")
3. Alternatively, click the calendar icon to select the date from a calendar widget

[Screenshot: Delivery Date field with calendar icon highlighted]

Expected result: The system accepts the date and validates that it is:
- Not in the past
- Realistic for the material's lead time

If you enter a date too soon, you see a warning: "Delivery date is before typical lead time for this material (5-7 days). Confirm with procurement."

**Step 6: Add Optional Details (if needed)**
The following fields are optional; fill them only if applicable to your purchase:

- **Cost Center:** If you want to charge this purchase to a specific cost center
- **Expedite:** Check this box only if the purchase is urgent and needs rush processing (may incur additional costs)
- **Special Instructions:** Add any notes for the Purchasing Officer (e.g., "Hazardous material; requires special handling")

[Screenshot: Optional fields section with examples]

**Step 7: Review Your Entry**
Before submitting, scroll up and verify:
- Material ID is displayed correctly with material name
- Quantity is correct and matches what you need
- Plant is set correctly
- Delivery date is realistic
- All required fields have values (required fields have a red asterisk *)

[Screenshot: Completed form showing all entries]

**Step 8: Submit the Purchase Requisition**
1. Click the blue "Submit" button at the bottom of the form
2. Wait 2-3 seconds while the system processes
3. You should see a green confirmation message

[Screenshot: Submit button highlighted in blue]

Expected result:
- Green message: "Purchase Requisition PR-2024-001234 created successfully"
- The system displays your new PR number
- The form clears and is ready to create another PR if needed

---

**DECISION POINTS:**

**Should I create a Purchase Requisition or a Purchase Order directly?**
→ Create a Purchase Requisition if:
- You are a Materials Planner or department manager identifying a need
- You need approval before procurement commits to buying
- The purchase is standard and will follow the normal approval chain

→ Create a Purchase Order directly if:
- You are a Purchasing Officer who already has an approved requisition
- The purchase is for an emergency or has already been verbally approved
- You are experienced and authorized to create orders without prior requisition

If unsure, create a Purchase Requisition. It's the standard path and ensures proper approvals.

---

**FIELD REFERENCE:**

| Field | What to Enter | Why It Matters | If Left Blank |
|---|---|---|---|
| Material ID | 18-digit code from parts catalog | Determines price, availability, lead time | Error: System prevents submission |
| Quantity | Number of units needed | Determines order size and shipping | Error: System prevents submission |
| Plant | Location that will receive the material | Ensures delivery to correct warehouse | At Anniston: Auto-filled with Anniston_Main; At other sites: Error |
| Delivery Date | When you need the material | Affects supplier selection and lead time | Error: System prevents submission |
| Cost Center | 6-digit internal cost code | Allocates cost to correct department | Optional; if blank, defaults to requester's default cost center |
| Expedite | Check box if urgent | Triggers fast-track approval and may add cost | Optional; if unchecked, normal lead time applies |
| Special Instructions | Free-text notes for Purchasing Officer | Communicates special requirements | Optional; no impact if blank |

---

**TROUBLESHOOTING:**

**Q: I clicked Submit but nothing happened**
A: The system may still be processing. Wait 5 seconds and check for a green success message. If you still see the form, there may be an error in a required field. Look for red error messages and correct them.

**Q: The system says "Material Not Found"**
A: The Material ID you entered does not exist in the catalog. Check your parts list for the correct 18-digit code. Common mistakes: transposing digits, using old material IDs that have been retired. If the material is new, contact the Materials Manager to ensure it has been added to the catalog.

**Q: I see a warning "Delivery date is before typical lead time"**
A: The delivery date you requested is sooner than the supplier can typically deliver. If the delivery date is firm, check "Expedite" and add a note explaining why rush delivery is needed. The Purchasing Officer will contact the supplier and may be able to arrange faster delivery (but at higher cost). If you have flexibility, change the delivery date to a later date.

**Q: The system says "Quantity exceeds normal range"**
A: You have ordered more than 999,999 units, which is unusual. If this is intentional, add an explanation in the Special Instructions field (e.g., "Annual stocking order"). If this is a mistake, reduce the quantity and verify the number needed.

**Q: My Plant field is locked and shows a different plant than I want**
A: At Anniston, the Plant field is automatically set to "Anniston_Main" and cannot be changed. If you actually need materials sent to a different location, contact your supervisor. At other sites, the Plant field is editable; click the dropdown and select the correct plant.

---

**RELATED RESOURCES:**
- Layer 2: Understanding the Purchase Requisition Process (context and workflow)
- Layer 3: Approving a Purchase Requisition (if you are an approver)
- Layer 4: In-App Help While Creating a Requisition
- Tosca Test Script Source: `Create_Purchase_Requisition_Standard_Anniston_v2.1`
- Generated: 2024-01-15 from BPMN v3.4, Tosca v2.1, Anniston Site Configuration v1.8

---

## Implementation Considerations

### Tosca Integration
- Tosca scripts must be accessible programmatically (via API or exported XML)
- Build a parser/converter to transform Tosca syntax into plain-English instructions
- Maintain a mapping between Tosca element selectors and user-friendly location descriptions
- Automated QC: After generating a job aid, execute the corresponding Tosca script to verify all steps still work

### Screenshot Generation and Markup
- Use automated UI testing tools (e.g., Selenium, Cypress) to capture live screenshots
- Implement annotation layer (arrows, boxes, text labels) using image manipulation library
- Generate screenshots with test data that matches examples in job aids
- Store original unadorned screenshots separately so they can be updated when UI changes

### Field Mapping Maintenance
- Extract UI field metadata from SAP (technical names, data types, labels)
- Extract from Fiori app metadata (element IDs, semantic locators)
- Build a field reference database linking technical names to user-friendly names
- Keep this database current as system changes; flagging stale references

### Opal Overlay System
- Build a metadata layer tracking site-specific variations (field defaults, approval rules, validation rules)
- During job aid generation, query Opal to identify variations for each site
- Parameterize job aid template with site-specific values
- Generate multiple variants if variations are extensive

### Validation and QA
- Automated testing: Execute Tosca script and capture expected outcomes; compare with job aid descriptions
- Manual testing: Have super users walk through job aids to verify accuracy and clarity
- Regression testing: When system updates, re-run validation to identify stale job aids
- User testing: Have sample users from different roles use job aids to identify clarity issues

### Update Triggers
- Layer 3 training becomes stale when:
  - Tosca test scripts change (new steps, modified selectors, changed expected outcomes)
  - UI changes (field renamed, layout reorganized, element selectors invalid)
  - Business rules change (new validation rules, new approval thresholds)
  - Site configurations change
  - Field help text changes in the system
- Stale training triggers automatic regeneration (see Layer 5)

### Scale Considerations
- For an enterprise like Army depots, potentially hundreds of job aids (one per role-task combination)
- Pre-generate all job aids at build time, not on-demand
- Organize job aids in a searchable repository with filtering by role, business process, and site
- Package job aids as PDF for offline access and printing

---

**Document Version:** 1.0
**Last Updated:** [GENERATION_DATE]
**Source System Snapshot:** [TOSCA_VERSION], [SAP_UI_METADATA_VERSION], [SITE_CONFIG_VERSION]
