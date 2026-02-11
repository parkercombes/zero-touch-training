# Layer 1: ERP Orientation & Navigation

**Goal:** "I'm not lost."

## Purpose

Layer 1 provides new and returning users with the confidence to navigate the ERP system independently. By eliminating navigation anxiety, this layer forms the foundational user competence needed to proceed to deeper process and task understanding. Users who complete Layer 1 should be able to locate and access any system function assigned to their role without external assistance.

## Source Inputs

Layer 1 training is automatically generated from the following sources:

### UI Metadata
- Complete menu hierarchies (SAP GUI, Fiori, Appian, and any custom portals)
- Navigation path definitions (transaction codes, app links, URL patterns)
- Button/link labels and their hierarchy within screens
- Breadcrumb structures and navigation history patterns
- Search functionality and keyword mappings

### Fiori App Catalog
- Complete list of published Fiori apps by role
- App categories, launch methods, and prerequisites
- App tile configurations and semantic meanings
- Custom Fiori apps specific to organizational needs

### SAP GUI Favorites
- Personalized favorite path configurations by role profile
- Frequency data for common entry points
- Shortcut key assignments and mnemonic codes
- Menu tree configurations at the site level

### Appian Workspace Layouts
- Workspace structures for each user role
- Portal organization and access patterns
- Task queue navigation and filtering
- Report portal hierarchies

### Signavio Role Definitions
- Role assignments and their scope
- Restricted functions or transaction codes by role
- Approval role hierarchies

## AI Generation Process

### Step 1: Extract Navigation Artifacts
Parse all source systems to build a complete navigation graph:
- Identify all transaction codes, Fiori app IDs, Appian task types, and portal sections
- Map role-to-feature access rules
- Extract field-level visibility constraints for different user roles
- Catalog common entry points for each business function (e.g., all paths that lead to purchase requisition creation)

### Step 2: Identify Common Entry Points Per Role
- Analyze historical transaction logs to determine which navigation paths are most frequently used by role
- Identify primary and secondary entry points for each critical function
- Flag rarely-used but important paths (e.g., emergency requisition creation)
- Determine typical user session patterns (e.g., "Most Purchasing Officers start at the Requisition Worklist")

### Step 3: Generate Annotated Walkthrough Sequences
- Create sequential navigation guides showing:
  - Starting position (e.g., SAP GUI Main Menu)
  - Each click/action required to reach the destination
  - Expected screen appearance at each step
  - Alternative paths (if applicable)
  - Common mistakes or dead ends to avoid
- Pair each step with a screenshot annotated with highlights showing the exact location of the next action
- Include keyboard shortcuts and mnemonic codes where available
- Document role-based variations (e.g., "If you do not see this menu item, your role may not have access")

### Step 4: Generate Optional Video Walkthroughs
- For complex multi-step navigation sequences, generate short video walkthroughs
- Use screen recording with cursor tracking and text overlays
- Include voiceover narration explaining each action
- Keep videos under 2 minutes per navigation path

## Output Format

### Static Navigation Guides
- One guide per major business function accessible from multiple entry points
- Format: Markdown with embedded screenshots
- Structure:
  - Function title and purpose
  - Prerequisites/role requirements
  - Numbered step sequence with annotated screenshots
  - Common variations or branches
  - Troubleshooting section (what if I don't see X?)
  - Links to related Layer 2 process documentation

### Screenshot Annotations
- Highlighting of clickable elements using boxes or arrows
- Text labels identifying menu items, buttons, or fields
- Optional color coding (e.g., red box = current step, blue box = next step)
- Consistent visual style across all guides

### Navigation Flowcharts
- For complex decision points, provide flowchart showing all possible paths
- Include text descriptions for each path branch
- Link to appropriate step-by-step guides from each branch

### Video Walkthroughs
- Format: MP4 or WebM
- Resolution: 1920x1080 minimum
- Include clickable video chapters for quick navigation to specific steps
- Provide transcript alongside video

## Site-Specific Considerations

Navigation configurations often vary across distribution center sites. The generation process must handle:

### Menu Configuration Variations
- Some sites may have restricted menu items based on local business rules
- Custom menu additions or reorganizations per site
- Transaction code availability varies by site authorization matrix
- Solution: Generate base navigation guides from enterprise configuration, then overlay site-specific differences with clear visual indicators (e.g., "At SE-DC, this menu is organized differently")

### Restricted Transaction Codes
- Certain transaction codes may be disabled at specific sites
- Some roles may have narrower authorizations at certain locations
- Solution: Include role + site matrix in guide generation; flag restricted paths with explanation of alternative routes

### Site-Specific Favorites and Shortcuts
- Each site may have curated favorite lists that differ from enterprise defaults
- Local power users have personalized shortcuts that should be documented as "Advanced" content
- Solution: Generate guides using enterprise defaults, then append site-specific favorites section

### Portal and Workspace Customization
- Appian workspace configurations are often site-customized
- Fiori app availability may differ based on local system landscape decisions
- Solution: Pull site-specific workspace definitions from Appian metadata and Fiori provisioning system

## Quality Criteria

All navigation training must meet these verification standards before publication:

### Path Verification
- Every navigation path described in the guides must be executable in the live system
- QA validation: Walk each guide using test user accounts at each site
- Screenshots must be current and match live system appearance
- No dead-end references that lead to inaccessible functions

### Role-Based Access Validation
- All role + function combinations must be verified against current authorization matrix
- Guides must accurately reflect what each role can and cannot access
- Test with multiple user roles to ensure correct visibility rules

### Consistency Across Formats
- Navigation guides, videos, and flowcharts must describe the same sequence of steps
- Visual elements (menu names, button labels) must be identical across all output formats
- Terminology consistency: Use official SAP/Appian/Fiori terminology

### Currency
- Generation date and source system snapshot date must be documented
- Automated regression testing must confirm no navigation paths have broken since generation
- Any manual updates must be tracked and dated

### Accessibility
- Screenshots must have alt text describing the navigation context
- Videos must include captions
- Guides must be readable by screen readers
- No reliance on color alone to convey information

## Example: "Navigating to Create Purchase Requisition in Fiori"

### Generated Walkthrough Structure

**Title:** Accessing the Create Purchase Requisition Function in SAP Fiori

**Target Roles:** Purchasing Officer, Materials Planner, Procurement Specialist

**Estimated Time:** 2 minutes

**Prerequisites:** You must have Purchasing Officer authorization (MM_PUR)

---

**Step 1: Open SAP Fiori Home**
- *Action:* From your desktop or browser bookmark, open the SAP Fiori Launchpad
- *Expected Screen:* You should see a grid of colored tiles with app names
- *Screenshot:* [Annotated screenshot showing Fiori home with all visible app tiles]
- *Note:* If you see a login screen instead, enter your network credentials and click "Log In"

**Step 2: Locate the Procurement Category**
- *Action:* On the Fiori home screen, look for the section labeled "Procurement" (or scroll if not immediately visible)
- *Expected Screen:* You should see multiple app tiles grouped under the Procurement heading
- *Screenshot:* [Annotated screenshot with red box around Procurement section]
- *Tip:* You can also use the search bar at the top of the screen: type "Purchase Requisition" and jump directly to Step 4

**Step 3: Find the "Create Purchase Requisition" App Tile**
- *Action:* Within the Procurement section, locate the tile labeled "Create Purchase Requisition"
- *Expected Screen:* This tile is typically teal/green colored
- *Screenshot:* [Close-up annotated screenshot of the Create Purchase Requisition tile]
- *Variation at SE-DC:* This app tile may be in a custom "Quick Actions" section at the top due to local configuration

**Step 4: Click the App Tile**
- *Action:* Click the "Create Purchase Requisition" tile
- *Expected Screen:* The app opens and displays a form with fields for Material, Quantity, Plant, Delivery Date, etc.
- *Screenshot:* [Annotated screenshot of the empty Create Requisition form]
- *Timing:* The app may take 3-5 seconds to load; a progress indicator will show during loading

**Step 5: Confirm You Are in the Correct App**
- *Visual Confirmation:* The page header should display "Create Purchase Requisition"
- *URL Check:* The URL should contain "/create-pr" or similar (check your browser address bar)
- *Screenshot:* [Annotated header showing the app title and key fields]

---

**Alternative Paths:**

**Path A: Using SAP GUI Menu (for users who prefer classic interface)**
1. Open SAP GUI
2. Click Menu → Materials Management → Purchasing → Purchase Requisition → Create
3. Transaction code: ME51N
4. [Screenshot of SAP GUI menu with path highlighted]

**Path B: Using Search Functionality (quickest for experienced users)**
1. At any point in Fiori, press Ctrl+/ (or click the Search icon)
2. Type "ME51" or "Purchase Requisition"
3. Click the matching result
4. [Screenshot of search bar and results]

---

**Troubleshooting:**

- **Q: I don't see the Procurement section on my Fiori home**
  - *A:* Your role may have restricted access to procurement functions. Contact your supervisor or IT support. Go to Layer 2 to understand if this function is part of your assigned role.

- **Q: The Create Purchase Requisition tile is missing or grayed out**
  - *A:* This app may not be provisioned for your user. Contact the Fiori administrator for your site.

- **Q: I clicked the tile but nothing happened**
  - *A:* Try clearing your browser cache (Ctrl+Shift+Delete) and logging in again. If the problem persists, check Layer 4 (In-App Assistance) for troubleshooting steps.

---

**Related Resources:**
- Layer 2: Understanding the Purchase Requisition Process
- Layer 3: Creating a Purchase Requisition - Your Role as Purchasing Officer
- Layer 4: In-App Help While Creating a Requisition

---

## Implementation Considerations

### Generation Infrastructure
- UI metadata extraction tools must be deployed to capture current menu structures, app definitions, and role mappings
- Screenshot generation automation requires headless browser instances or RPA tools to capture live system state
- Video generation may require screen recording automation + voiceover synthesis or template-based assembly

### Validation Workflow
- Automated testing: For each generated guide, execute the navigation path using test user accounts to confirm walkability
- Manual review: Subject matter experts (super users) review guides for accuracy and completeness
- Regression testing: When system updates occur, re-run navigation path tests to flag broken guides

### Update Triggers
- Layer 1 training becomes stale when:
  - Menu structures change (detected via periodic UI metadata snapshots)
  - Transaction codes are added/removed (detected via SAP change log)
  - Fiori app provisioning changes (detected via app catalog version changes)
  - Role authorization matrices change (detected via authorization configuration)
- Stale guides trigger automatic regeneration (see Layer 5)

### Role-Based Training Personalization
- Generate role-specific variants of guides showing only accessible functions for that role
- Use role-based filtering during screenshot generation to hide inaccessible menu items
- Include role prerequisites at the beginning of each guide

---

**Document Version:** 1.0
**Last Updated:** [GENERATION_DATE]
**Source System Snapshot:** [UI_METADATA_VERSION]
