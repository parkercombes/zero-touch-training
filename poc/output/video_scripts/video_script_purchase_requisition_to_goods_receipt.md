# Understanding Purchase Requisition to Goods Receipt at Southeast Distribution Center

## Training Video Script for Buyer Role

---

### TITLE CARD

[VISUAL: GlobalMart logo and SE-DC facility image with title overlay]
**"Understanding Purchase Requisition to Goods Receipt at Southeast Distribution Center"**
*A Training Guide for Buyers*

---

### INTRODUCTION (30 seconds)

[VISUAL: Split screen showing SE-DC warehouse operations and SAP S/4HANA interface]
NARRATOR: "Welcome to the Purchase Requisition to Goods Receipt process training for GlobalMart's Southeast Distribution Center. As a Buyer at SE-DC, you play a crucial role in converting purchase requisitions into purchase orders while ensuring our perishable goods meet strict cold chain requirements."

[VISUAL: Process flow diagram highlighting Buyer role]
NARRATOR: "In the next six minutes, you'll learn how to navigate the entire process from PR creation to goods receipt, understand your specific responsibilities, and master the SE-DC requirements that keep our perishable operations running smoothly."

---

### PROCESS OVERVIEW (60 seconds)

[VISUAL: High-level BPMN process diagram with role swimlanes]
NARRATOR: "Let's start with the big picture. This process involves five key roles: the Store or Department Requestor who identifies the need, you as the Buyer who converts PRs to POs, the Category Manager and VP Supply Chain for approvals, and the Receiving Clerk who posts goods receipt."

[VISUAL: Animation showing process flow with timing callouts]
NARRATOR: "The process begins when inventory needs are identified and ends when goods are received and stock is updated. What makes SE-DC unique is our focus on perishable goods with strict seven-day delivery windows and mandatory cold chain compliance."

[VISUAL: Highlight Buyer responsibilities in orange]
NARRATOR: "As the Buyer, you're the bridge between approved purchase requisitions and successful supplier delivery. You'll negotiate terms, ensure compliance with regional supplier programs, and make sure temperature zone requirements carry through to delivery."

---

### STEP-BY-STEP WALKTHROUGH (2-3 minutes)

[VISUAL: SAP ME51N transaction screen]
NARRATOR: "The process starts when requestors create purchase requisitions using transaction ME51N. They'll specify the material, quantities in cases, and delivery dates within our seven-day perishable window."

[VISUAL: Screen recording showing PR creation with callouts for mandatory fields]
NARRATOR: "[CALLOUT] Notice that at SE-DC, lot and batch tracking is mandatory for perishables, and purchasing groups are restricted to R-SE for Regional Southeast or R-NAT for National programs only."

[VISUAL: Decision diamond showing $25K threshold]
NARRATOR: "Once the PR is created, the system checks if the amount exceeds twenty-five thousand dollars. [HIGHLIGHT] This is different from the enterprise standard of fifty thousand because we're dealing with perishables that carry higher spoilage risk."

[VISUAL: Two-tier approval flow diagram]
NARRATOR: "For PRs twenty-five thousand or less, we follow standard two-tier approval: Category Manager review followed by Procurement Lead verification. This keeps smaller orders moving quickly through our perishable pipeline."

[VISUAL: Three-tier approval flow diagram]
NARRATOR: "For amounts over twenty-five thousand, we add VP Supply Chain approval. This extra step ensures proper oversight for high-value perishable orders where spoilage could mean significant losses."

[VISUAL: SAP ME21N transaction screen highlighting key fields]
NARRATOR: "Here's where you take center stage. Using transaction ME21N, you'll convert the approved PR into a purchase order. Your job is to negotiate terms with suppliers, verify they're part of our approved regional programs, and confirm delivery schedules."

[VISUAL: Screen recording showing PO creation with temperature zone verification]
NARRATOR: "[HIGHLIGHT] Pay special attention to temperature zone requirements. These must carry through from the PR to ensure proper cold chain handling. Zone-F for frozen, Zone-R for refrigerated, and Zone-A for ambient temperature goods."

[VISUAL: Multiple transmission methods shown - EDI, email, portal]
NARRATOR: "Once the PO is complete, you'll send it to the supplier using the appropriate method: EDI for major regional suppliers, email for routine suppliers, or our supplier portal for integrated partners."

[VISUAL: SE-DC receiving dock with temperature monitoring equipment]
NARRATOR: "When goods arrive at SE-DC, our Receiving Clerks take over. They'll post goods receipt using MIGO with movement type 101, but they're doing much more than a standard receipt."

[VISUAL: MIGO screen showing SE-DC specific fields and checks]
NARRATOR: "[CALLOUT] At SE-DC, every perishable delivery requires cold chain verification with actual temperature recording at the dock. The system also flags items for mandatory quality inspection based on our perishable and private-label policies."

[VISUAL: MMBE inventory verification screen]
NARRATOR: "Finally, the Receiving Clerk verifies that inventory is properly updated in the correct temperature zone with all lot and batch information recorded for traceability."

---

### KEY DECISION POINTS (60 seconds)

[VISUAL: Decision point diagram with paths highlighted]
NARRATOR: "Let's focus on the critical decision point that affects your work as a Buyer. The twenty-five thousand dollar threshold determines approval complexity and timing."

[VISUAL: Clock animation showing approval timeframes]
NARRATOR: "Orders twenty-five thousand or less move through two-tier approval, typically completed within one business day. This keeps our perishable supply chain moving at the speed our seven-day delivery window requires."

[VISUAL: Three-tier approval with extended timeline]
NARRATOR: "Orders exceeding twenty-five thousand need VP Supply Chain approval, which can add an additional business day. [HIGHLIGHT] Plan accordingly when working with suppliers on large perishable orders – that extra day matters when you're dealing with short shelf lives."

[VISUAL: Approval routing diagram]
NARRATOR: "Understanding this decision point helps you advise requestors on timing expectations and allows you to manage supplier relationships more effectively."

---

### SITE-SPECIFIC REQUIREMENTS (60 seconds)

[VISUAL: Side-by-side comparison of Enterprise vs SE-DC requirements]
NARRATOR: "SE-DC has several requirements that differ from enterprise standards, and it's crucial you understand why. First, our purchasing group restriction to R-SE and R-NAT ensures we're working with suppliers who understand cold chain requirements."

[VISUAL: Lot tracking format example: LOT-YYYY-MMDD-XX]
NARRATOR: "[CALLOUT] Mandatory lot and batch tracking isn't just a nice-to-have here – it's required for food safety traceability. The format is LOT, year, month, day, and sequence number."

[VISUAL: Temperature zone mapping diagram]
NARRATOR: "Our temperature zone assignments must be precise. Zone-F for frozen goods, Zone-R for refrigerated, and Zone-A for ambient. Any mismatch can compromise product quality and safety."

[VISUAL: Thermometer showing cold chain verification]
NARRATOR: "The mandatory cold chain verification at receiving means your delivery scheduling becomes critical. Suppliers need to understand that temperature excursions will result in rejected deliveries."

---

### WRAP-UP (30 seconds)

[VISUAL: Key takeaways checklist appearing on screen]
NARRATOR: "To summarize: As an SE-DC Buyer, you're managing more than just purchase orders – you're ensuring cold chain integrity from supplier to shelf. Remember the twenty-five thousand dollar approval threshold, verify temperature zone requirements, and work only with R-SE and R-NAT purchasing groups."

[VISUAL: Resource links and contact information]
NARRATOR: "For additional support, check the SE-DC Buyer Quick Reference Guide in the training portal, or contact the Procurement Help Desk. Your next recommended training is 'Cold Chain Supplier Management' to build on what you've learned today."

[VISUAL: GlobalMart SE-DC logo with "Training Complete" message]
NARRATOR: "Thanks for completing this training. Now you're ready to manage the Purchase Requisition to Goods Receipt process effectively at Southeast Distribution Center."

---

**Total Duration: Approximately 6 minutes**

**Related Training Modules:**
- Cold Chain Supplier Management
- SAP S/4HANA Purchase Order Management
- SE-DC Quality Inspection Procedures