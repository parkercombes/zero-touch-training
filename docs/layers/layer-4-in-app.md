# Layer 4: In-App Assistance

**Goal:** "Help me while I'm doing it."

## Purpose

Layer 4 is point-of-need assistance delivered inside the application as users work. While Layers 1-3 are reference materials users consult before or between tasks, Layer 4 provides contextual guidance without the user leaving the app. When a user is filling out a Purchase Requisition form and pauses at a field, Layer 4 guidance appears immediately at that field.

Layer 4 is built using workflow/walkthrough tools like WalkMe, Apptio, or similar platforms. The key innovation is that Layer 4 guidance is not manually authored — it is generated directly from Tosca test scripts and deployed through automated configuration, dramatically reducing the overhead of setting up and maintaining in-app guidance.

## Source Inputs

### Tosca Test Scripts (Step Sequences)
- Extract the sequence of actions from Tosca scripts (same source as Layer 3)
- For each Tosca test step, identify:
  - What UI element the user interacts with
  - What action (click, type, select, date pick) is required
  - What the user should enter (or select)
  - What the system does in response
  - Any validation or conditional logic

### UI Element Identifiers
Critical for in-app guidance to target the exact field or button:

- **CSS Selectors:** For web-based SAP Fiori and Appian apps
  - Example: `button[aria-label="Create Purchase Requisition"]`
  - Example: `input[id="mat_id_field"]`

- **Fiori Element Identifiers:** For SAP Fiori apps
  - Form IDs, control IDs, semantic selectors
  - Example: `sap.m.Button#createPRBtn`

- **SAP GUI Field IDs:** For SAP GUI applications
  - OKCODE values, screen field positions
  - Example: `/nME51N` (transaction code)

- **Appian Component IDs:** For Appian workflow apps
  - Field identifiers and process variable names
  - Example: `component.123.fields.material_id`

- **Semantic Locators:** For accessibility and resilience
  - Role-based and text-based selectors that work even if IDs change
  - Example: "Button labeled 'Create'" or "Input field for 'Material ID'"

### Field Help Text and Guidance Content
- Extract help text from system field definitions
- Business rules and validation constraints
- Examples of correct input
- Cross-field dependencies and conditional logic

### Validation Rules and Error Messages
- All validation rules from Tosca (what triggers errors, what warnings appear)
- Error message text from the system
- How to resolve each error
- Fallback paths if validation fails

## AI Generation Process

### Step 1: Map Tosca Steps to UI Elements
Create a mapping of every Tosca test step to the specific UI element it targets:

```
Tosca Step:
  Action: Click element with CSS selector "button[aria-label='Submit']"

Mapping:
  UI Element ID: submit_button
  Element Type: Button
  Label: "Submit"
  Location: Bottom right of form
  CSS Selector: button[aria-label='Submit']
  Fiori ID: sap.m.Button#confirmBtn
  Semantic Locator: "button labeled 'Submit'"
  Action Type: Click
  Expected Response: Form submission, loading animation, success/error message
```

### Step 2: Extract Action Sequences and UI Dependencies
Document the flow of actions and how UI elements depend on each other:

```
Flow: Create Purchase Requisition

  Action 1: Navigate to Create PR app
    → UI State: Form appears with fields
    → Dependency: User must see Fiori home first (Layer 1 prerequisite)

  Action 2: Click Material ID field
    → UI Element: Input field with ID "material_id"
    → Expected: Field becomes active (cursor visible, field outlined)

  Action 3: Enter material code
    → UI Element: Same input field
    → Input: "012345000000789012" (18-digit string)
    → Validation: System looks up material; display name appears below field
    → Dependency: If material not found, error message prevents proceeding

  Action 4: Click Quantity field
    → UI Element: Input field with ID "quantity"
    → Expected: Material ID field loses focus; Quantity field becomes active

  [... continue for each action ...]
```

### Step 3: Identify UI Element Selectors with Fallback Strategies
Create robust selectors that work even if the system changes:

```
Element: Material ID Input Field

Primary Selector (CSS): input#material_id_field
Fallback Selector 1 (XPath): //input[@placeholder='Material ID']
Fallback Selector 2 (Semantic): Input field for "Material ID"
Fallback Selector 3 (Fiori): sap.m.Input with ariaLabel="Material ID"

Test Selectors Against Current System:
  ✓ CSS selector works
  ✓ XPath selector works
  ✓ Semantic selector matches
  ✓ Fiori ID works

If primary fails, system will try fallbacks in order.
```

### Step 4: Generate WalkMe (or Similar) Flow Definitions
Create flow configuration in the format expected by the in-app guidance platform:

WalkMe flow is typically expressed as JSON or XML defining:
- Flow name and description
- Trigger conditions (when should this guidance appear)
- Sequence of steps/actions
- For each step: UI element selector, tooltip/tip content, completion criteria

```json
{
  "flowId": "create_pr_guidance",
  "flowName": "Create Purchase Requisition Walkthrough",
  "description": "Step-by-step guidance for creating a purchase requisition",
  "trigger": {
    "type": "page_load",
    "condition": "page contains 'Create Purchase Requisition' in title"
  },
  "startMode": "manual",
  "steps": [
    {
      "stepId": "step_1_material_id",
      "elementSelector": "input#material_id_field",
      "fallbackSelectors": [
        "//input[@placeholder='Material ID']",
        "input[aria-label='Material ID']"
      ],
      "actionType": "highlight",
      "tooltip": {
        "title": "Enter Material ID",
        "body": "Enter the 18-digit material code from your parts catalog. Example: 012345000000789012",
        "position": "right"
      },
      "completionCondition": "field contains value AND field has valid format (18 digits)",
      "validationError": {
        "trigger": "field contains non-numeric characters",
        "tooltip": "Material ID must be 18 digits. You entered: [user_value]"
      }
    },
    {
      "stepId": "step_2_quantity",
      "elementSelector": "input#quantity_field",
      "fallbackSelectors": [
        "//input[@name='quantity']",
        "input[aria-label='Quantity']"
      ],
      "actionType": "highlight",
      "tooltip": {
        "title": "Enter Quantity",
        "body": "How many units do you need? Enter a positive whole number (1 to 999,999).",
        "position": "right"
      },
      "completionCondition": "field contains numeric value > 0 AND < 999999"
    },
    {
      "stepId": "step_3_plant",
      "elementSelector": "select#plant_field",
      "tooltip": {
        "title": "Select Plant",
        "body": "Choose the warehouse that will receive this material. At Anniston, this field auto-selects 'Anniston_Main'.",
        "position": "right"
      },
      "siteSpecific": {
        "Anniston": {
          "tooltip": {
            "body": "The Plant field is automatically set to 'Anniston_Main' and cannot be changed."
          },
          "completionCondition": "field displays 'Anniston_Main'"
        }
      }
    },
    {
      "stepId": "step_4_delivery_date",
      "elementSelector": "input#delivery_date_field",
      "actionType": "highlight",
      "tooltip": {
        "title": "Enter Delivery Date",
        "body": "When do you need this material? Use format YYYY-MM-DD. Must be a future date (not today or earlier).",
        "position": "right"
      },
      "validationWarning": {
        "trigger": "date is less than material lead time",
        "tooltip": "This delivery date is sooner than typical for this material. Confirm with procurement."
      }
    },
    {
      "stepId": "step_5_submit",
      "elementSelector": "button[aria-label='Submit']",
      "actionType": "highlight",
      "tooltip": {
        "title": "Submit Your Requisition",
        "body": "Click Submit to send your purchase requisition for approval.",
        "position": "left"
      },
      "completionCondition": "form submission succeeds AND success message appears"
    }
  ],
  "completionMessage": {
    "title": "Requisition Created!",
    "body": "Your purchase requisition has been created and is awaiting approval. Your PR number is [pr_number]. You can track it in the Requisition Worklist."
  }
}
```

### Step 5: Generate Contextual Tips at Each Step
Create helpful guidance that appears at the moment the user needs it:

For each field/step, generate:
- **Title:** What the user is doing now
- **Body:** Why it matters and what to enter
- **Examples:** Concrete examples of correct input
- **Links:** To detailed Layer 3 job aid if user needs more help
- **Common mistakes:** What not to do

### Step 6: Add Decision Branch Logic
For tasks with conditional paths, define branching in the flow:

```
If user clicks "Reject" instead of "Approve":
  → Show different guidance flow for "Rejecting a Requisition"
  → Guidance says: "You are rejecting this requisition. You must provide feedback
     to the requester. Add a comment in the Rejection Reason field explaining
     what needs to be changed."
  → Guide them through rejection process instead

If user enters amount > $50,000:
  → Add step: "This amount requires Finance Committee approval"
  → Guide them through adding finance approver

If user tries to proceed without filling required field:
  → Highlight the missing field in red
  → Tooltip: "You must complete [Field Name] before you can submit"
  → Prevent submission
```

### Step 7: Identify UI Element Resilience Requirements
Plan for how guidance will adapt if the system changes:

```
Material ID Field Resilience Strategy:

Scenario 1: CSS selector ID changes from "material_id_field" to "mat_id_input"
  → Primary selector fails
  → Fallback: XPath selector "//input[@placeholder='Material ID']" succeeds
  → Flow continues without interruption

Scenario 2: Field label changes from "Material ID" to "Material Code"
  → Semantic selector still works ("Input field for entering material identifier")
  → Tooltip text may need update (governance gate catches this in Layer 5)
  → Flow continues but guidance is flagged for review

Scenario 3: Field is hidden for certain roles
  → Trigger condition checks: "Is this field visible for current user role?"
  → If hidden: Flow skips this step
  → If visible: Flow shows step normally

Resilience Test:
  ✓ Can we still locate the element after system update?
  ✓ Is the guidance still relevant if element changes?
  ✓ Will the flow gracefully degrade if element is not found?
```

### Step 8: Compile WalkMe Configuration for Deployment
Package all flows and guidance into deployment-ready format:

- Test all selectors against current system (ensure no dead links)
- Validate JSON/XML syntax
- Version the configuration
- Flag site-specific variations for separate deployment per site
- Create manifest documenting all flows, versions, and dependencies

## Output Format

### WalkMe Flow Definitions

**Delivery Format:** JSON or XML configuration files

**Structure:** As shown in Step 4 above—hierarchical definition of flows, steps, tooltips, and completion criteria

**Validation:** Every flow must:
- Have valid element selectors that work against current system
- Include fallback selectors for robustness
- Define clear completion conditions
- Include helpful tooltip text
- Link to Layer 3 detailed guidance for users who want more help

### Contextual Tooltip Definitions

**Display Location:** In-app, adjacent to the UI element being described

**Content Template:**

```
[Icon] [Title]
[Body text, 1-3 sentences]
[Examples, if applicable]
[Link to detailed guidance]
[Acknowledge button: "Got it" or "Show me more"]
```

**Example Tooltip:**

```
ICON: Information circle

TITLE: Material ID

BODY:
Enter the 18-digit material code from your parts catalog. This tells the
system which item you're ordering and pulls in pricing, availability, and
lead time information.

EXAMPLE:
Correct: 012345000000789012
Incorrect: 012345789 (too short)

NEED MORE HELP?
[View detailed guide for creating a requisition]

[Got it]  [Show me more]
```

### Smart Walk-Thru Sequences

Sequences guide users step-by-step through multi-step processes:

**Sequence A: Create Purchase Requisition (Happy Path)**
1. Highlight Material ID field
2. Wait for user to enter valid material
3. Highlight Quantity field
4. Wait for user to enter valid quantity
5. Highlight Plant field (with site-specific guidance)
6. Highlight Delivery Date field
7. Highlight Submit button
8. Monitor form submission
9. Display success message with PR number

**Sequence B: Create Purchase Requisition (High-Value Path)**
1. [Same as Sequence A through step 6]
7. Detect: amount > $50,000
8. Insert step: "This requisition requires Finance Committee approval. Click the 'Add Approver' button and select Finance Committee."
9. [Continue with submit...]

**Sequence C: Approve Purchase Requisition**
1. Highlight Approve button
2. If amount < $5,000: "Click Approve to auto-approve this requisition"
3. If amount $5,000-$50,000: "Click Approve and select which approver this goes to next"
4. If amount > $50,000: "This requires Finance approval. Click Forward to Finance."
5. Highlight Comments field (optional but recommended)
6. Monitor submission

### Site-Specific Guidance Overlays

For in-app guidance, site-specific variations are embedded in the flow definition:

```json
{
  "stepId": "step_plant_selection",
  "elementSelector": "select#plant_field",
  "tooltip": {
    "default": "Select the warehouse that will receive this material.",
    "siteSpecific": {
      "Anniston": "The Plant field is automatically set to 'Anniston_Main' and cannot be changed.",
      "Rome": "Select your plant from the dropdown. Options: Rome_Central, Rome_North, Rome_South."
    }
  }
}
```

At runtime, the guidance platform checks the user's site and displays the appropriate tooltip.

### Validation Rule Definitions

For each input field, encode what the system accepts and what error messages appear:

```json
{
  "fieldId": "material_id",
  "validation": [
    {
      "rule": "length must be 18",
      "errorMessage": "Material ID must be exactly 18 digits",
      "userGuidance": "Check your parts catalog for the correct 18-digit code"
    },
    {
      "rule": "must contain only digits",
      "errorMessage": "Material ID cannot contain letters or special characters",
      "userGuidance": "Material ID is numeric only. Remove any letters."
    },
    {
      "rule": "material must exist in database",
      "errorMessage": "Material [entered_value] not found in catalog",
      "userGuidance": "This material does not exist in our catalog. Check with Materials Manager."
    },
    {
      "rule": "material must be active (not retired)",
      "warning": "Material [name] was retired on [date]. Continued use requires supervisor approval.",
      "userGuidance": "This material is no longer standard. If you must use it, add a note in Special Instructions."
    }
  ]
}
```

## Site-Specific Considerations

### UI Configuration Variations
Different sites may have different Fiori configurations or SAP GUI menu layouts. The in-app guidance must handle:

- **Different element IDs:** If Anniston configures a button with ID "btn_submit_anniston" and Rome uses "btn_submit_rome"
  - Solution: Use fallback selectors that work regardless of specific IDs
  - Solution: Maintain site-specific selector mappings

- **Different field visibility:** Some fields are required at all sites, optional at some, hidden at others
  - Solution: Embed visibility checks in flow definitions
  - Solution: Different flow variants per site if variations are extensive

- **Different field defaults:** Material ID might be pre-populated at Anniston but blank at Rome
  - Solution: Document default behavior in tooltip
  - Solution: Adjust completion criteria per site

### Approval Flow Variations
Different approval requirements at different sites require different guidance sequences:

```
Create PR with amount $25,000:

At Anniston:
  Requisition → Anniston_Manager → Procurement_Manager → Auto-approve
  Guidance: "Route to your manager for approval"

At Rome:
  Requisition → Rome_Supervisor → Rome_Manager → Finance_Approval
  Guidance: "Route to your supervisor, who will forward to the manager"
```

Solution: Parameterize approval flow guidance based on site and amount.

### Language and Localization
If sites operate in different languages or have local terminology:

- Tooltip text may need translation
- Field names may have site-specific labels
- Examples should use realistic data for that site/language
- Solution: Maintain localized versions of guidance content per site/language

## Quality Criteria

All in-app guidance must meet these standards:

### Selector Accuracy and Resilience
- Primary selectors must work against current live system (tested in automation)
- Fallback selectors must be tested; at least one must work if primary fails
- Selectors should use semantic approaches when possible (resilient to ID changes)
- Every selector should be validated in QA before deployment

### Tooltip Clarity and Brevity
- Tooltips must be understandable to users with minimal ERP experience
- Text must be concise: title in 3-4 words, body in 2-3 sentences
- Examples must be realistic and match the current system
- "Why it matters" must be explained at least once per task

### Completeness of Error Handling
- All validation errors from Tosca must have corresponding tooltip guidance
- Every error message the system displays must have an explanation and solution in the tooltip
- Edge cases and uncommon paths must be documented
- No references to fields or system behavior that don't exist

### Functional Testing
- Every flow must be executable end-to-end with test user accounts
- QA must walk through each flow and confirm all guidance appears at the right time
- Form submissions in flows must actually succeed in the live system
- Conditional paths (if-then branches) must be tested with appropriate data

### Site-Specific Validation
- Flows must be tested at each site where they apply
- Site-specific selectors must work at each site
- Site-specific guidance text must be accurate for that site's configuration
- Approval workflows must match actual site approval chains

### Accessibility
- Tooltips must be readable by screen readers
- Guidance must not rely on color alone to convey information
- Links must be keyboard-navigable
- Font sizes must be legible (10pt minimum)

## Example: WalkMe Flow for "Create Purchase Requisition"

### Complete Flow Configuration

**Flow Name:** Create Purchase Requisition
**Description:** Step-by-step in-app guidance for creating a purchase requisition
**Versions:** Enterprise standard (all sites), Anniston overlay, Rome overlay

**Trigger:** Page contains "Create Purchase Requisition" title OR URL contains "/create-pr"

**Steps:**

1. **Welcome**
   - Type: Message
   - Content: "Welcome! This guide will walk you through creating a purchase requisition. Click next to begin."
   - Buttons: [Next] [I know how to do this, skip guide]

2. **Material ID Field**
   - Type: Highlight + Tooltip
   - Element: input#material_id_field
   - Tooltip Title: "Enter Material ID"
   - Tooltip Body: "The 18-digit material code from your parts catalog. Example: 012345000000789012"
   - Highlight Color: Blue
   - Position: Right
   - Completion: Field contains 18 numeric characters AND system displays material name below field
   - If validation fails (non-numeric or wrong length): Show error tooltip with correction

3. **Material Confirmation**
   - Type: Highlight
   - Element: div#material_name_display
   - Tooltip: "The system found your material: [material_name]. If this is wrong, go back and re-enter the Material ID."
   - Continue: Automatic (system detected material was found)

4. **Quantity Field**
   - Type: Highlight + Tooltip
   - Element: input#quantity_field
   - Tooltip Title: "Enter Quantity"
   - Tooltip Body: "How many units do you need? Enter a number from 1 to 999,999."
   - Completion: Field contains positive integer < 999,999
   - Validation: If user enters 0 or negative, show error tooltip. If > 999,999, show warning.

5. **Plant Selection**
   - Type: Highlight + Conditional Tooltip
   - Element: select#plant_field
   - Tooltip (Enterprise): "Select the plant/warehouse that will receive this material."
   - Tooltip (Anniston Site): "Your plant is automatically set to 'Anniston_Main'."
   - Tooltip (Rome Site): "Select your plant from the dropdown."
   - Completion: Field contains valid plant selection

6. **Delivery Date Field**
   - Type: Highlight + Tooltip
   - Element: input#delivery_date_field
   - Tooltip Title: "Delivery Date"
   - Tooltip Body: "When do you need this? Enter in YYYY-MM-DD format. Must be a future date."
   - Completion: Field contains valid future date
   - Validation: If date < today, show error. If date < material lead time, show warning.

7. **Decision Point: Check Amount**
   - Logic: If [amount] < $5,000, skip to step 8. If >= $5,000, show step 8a.

8a. **Add Approver (High-Value PRs)**
   - Condition: Amount >= $5,000
   - Type: Highlight + Tooltip
   - Element: button#add_approver_button
   - Tooltip: "This requisition is over $5,000 and requires approval from [appropriate_role]. Click this button to add an approver."
   - Completion: Approver has been added

8. **Submit Button**
   - Type: Highlight + Tooltip
   - Element: button[aria-label='Submit']
   - Tooltip Title: "Submit Your Requisition"
   - Tooltip Body: "Click Submit to send your purchase requisition for approval. You'll receive a PR number in the next screen."
   - Highlight Color: Green
   - Position: Left

9. **Form Submission**
   - Type: Monitor
   - Wait for: API call to /api/create-pr succeeds
   - Monitor: Spinning progress indicator
   - Tooltip: "Submitting your requisition... This may take a few seconds."

10. **Success**
    - Type: Message
    - Trigger: Success API response received
    - Content: "Your purchase requisition has been created! Your PR number is [pr_number]. Track it in the Requisition Worklist."
    - Buttons: [Done] [Create another requisition] [View my requisition]

**Error Handling:**

```
If material ID is invalid:
  → Show tooltip: "Material ID must be exactly 18 digits with no letters.
     You entered: [value]"
  → Highlight field in red
  → Block progress until corrected

If form submission fails:
  → Show error message with system error text
  → Provide troubleshooting: "Try refreshing the page and submitting again.
     If the problem persists, contact IT support."

If user closes the flow:
  → Preserve form data
  → Allow user to resume flow by clicking "Help" icon
```

---

## Implementation Considerations

### WalkMe Integration
- Deploy WalkMe agent/script in the ERP environment
- Configure WalkMe to load flow definitions from Zero-Touch Training platform
- Set up WalkMe to capture element selectors and validate them
- Configure WalkMe analytics to track which flows are used, completion rates, where users drop off

### Selector Validation Automation
- Build an automated test that:
  - Loads each WalkMe flow
  - For each step, attempts to locate the target element using all selectors
  - Tests primary selector first, then fallbacks
  - Reports: selector works, selector fails, element not found
  - Runs after system updates to detect broken flows

### Deployment Strategy
- Generate WalkMe flows at system build time
- Test flows in staging environment before production deployment
- Deploy flows to production with version control
- Maintain separate flow deployments per site (due to site-specific variations)
- Implement feature flags to enable/disable flows per site or user role

### Performance Optimization
- WalkMe overlays can impact page performance if there are too many active flows
- Implement flow prioritization: only deploy highest-value flows, deactivate rarely-used flows
- Use WalkMe segmentation to show guidance only to new users or first-time task performers
- Monitor WalkMe impact on page load time; optimize selectors if necessary

### Update Triggers
- Layer 4 training becomes stale when:
  - Tosca test script changes (new steps, changed UI element selectors, changed validation)
  - UI elements change (IDs change, selectors become invalid, elements are hidden)
  - Tooltip content references system behavior that has changed
  - Site-specific configurations change
  - Error messages change in the system
- Stale guidance triggers automatic regeneration (see Layer 5)

### Human Review Model
- AI generates WalkMe flow definitions from Tosca + UI metadata
- Humans review flow definitions for:
  - Selector validity and resilience
  - Tooltip clarity and accuracy
  - Completeness of error handling
  - Site-specific accuracy
- Approval gate: SMEs and process owners must approve before flows go live
- Rejected flows are regenerated with corrections

### Accessibility Compliance
- Ensure all WalkMe tooltips are accessible to screen reader users
- Use ARIA labels and semantic HTML where possible
- Test flows with accessibility testing tools (WAVE, Axe, etc.)
- Ensure keyboard navigation works (tooltips are dismissable with Esc key, focus is properly managed)

---

**Document Version:** 1.0
**Last Updated:** [GENERATION_DATE]
**Source System Snapshot:** [TOSCA_VERSION], [UI_ELEMENT_METADATA_VERSION], [SITE_CONFIG_VERSION]
