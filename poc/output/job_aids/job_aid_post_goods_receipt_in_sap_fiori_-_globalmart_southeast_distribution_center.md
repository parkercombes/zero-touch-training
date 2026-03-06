# Purchase Requisition to Goods Receipt — Quick Reference for Buyer

**Site:** Southeast Distribution Center (SE-DC)  
**Transaction:** MIGO (Post Goods Receipt)  
**Last Updated:** 2026-02-11

## WHEN TO USE THIS

Use this process when you need to receive goods against an approved Purchase Order. This is triggered when the Receiving Clerk notifies you that goods have physically arrived and need to be posted in SAP to update inventory and complete the procurement cycle.

## BEFORE YOU START (Prerequisites)

- **Access:** SAP Fiori Launchpad access with Receiving Clerk permissions
- **Information needed:**
  - Purchase Order number (from supplier delivery documentation)
  - Physical quantity received
  - Storage location assignment
  - Quality inspection requirements for the material category
- **Physical verification:** Goods must be physically received and inspected before system posting

## KEY FIELDS REFERENCE TABLE

| Field | Where to Find It | What to Enter | Site Rule |
|-------|------------------|---------------|-----------|
| **Movement Type** | MIGO form dropdown | 101 (Goods Receipt for PO) | Standard |
| **PO Number** | Main entry field | 10-digit PO number from delivery docs | Standard |
| **GR Quantity** | Line item table | Actual quantity received | Must match physical count |
| **Storage Location** ⚠️ | Line item dropdown | Zone-R for perishables | **SE-DC: Temperature zone matching mandatory** |
| **Quality Inspection** ⚠️ | Line item checkbox | ☑️ for PERISHABLE-DAIRY | **SE-DC: Mandatory for perishables/private-label** |
| **Inspection Notes** ⚠️ | Text field | Temperature, packaging, expiry details | **SE-DC: Required for cold chain traceability** |

## STEP-BY-STEP (Condensed)

1. **Access MIGO:** Search "Post Goods Receipt" in Fiori Launchpad → Click MIGO tile
2. **Set Movement Type:** Select **101** (Goods Receipt for Purchase Order)
3. **Enter PO:** Input PO number → Verify line items auto-populate
4. **Validate Material:** Confirm material number and description match delivery
5. **Enter Quantities:** Input actual received quantity (must match physical count)
6. **⚠️ Assign Storage:** Select temperature-appropriate zone (Zone-R for perishables)
7. **⚠️ Quality Check:** Enable inspection for PERISHABLE-DAIRY materials (mandatory at SE-DC)
8. **Document Inspection:** Enter temperature, packaging, and expiry verification notes
9. **Post Receipt:** Click Post → Capture Material Document number for records
10. **Verify Stock:** Check MMBE to confirm inventory update in correct storage location

## SITE-SPECIFIC RULES (SE-DC)

> **⚠️ SE-DC Distribution Center Requirements**
> 
> - **Storage Location Matching:** Enterprise: Optional zone assignment → **SE-DC: Mandatory temperature zone matching** (Zone-R for perishables at 38°F)
> - **Quality Inspection:** Enterprise: Optional for most goods → **SE-DC: Mandatory for all perishable and private-label items** per DC policy
> - **Inspection Documentation:** Enterprise: Basic notes → **SE-DC: Detailed cold chain verification required** (temperature, packaging, expiry, lot tracking)
> - **Approval Threshold:** Enterprise: $50K → **SE-DC: $25K for perishables** (expedited approval process)

## VERIFICATION CHECKLIST

- [ ] Movement Type = **101** (Goods Receipt for PO)
- [ ] PO number entered and line items populated correctly
- [ ] Material numbers match physical delivery documentation
- [ ] GR quantities match actual physical count
- [ ] Storage location matches product temperature requirements (Zone-R for perishables)
- [ ] Quality inspection enabled for PERISHABLE-DAIRY items
- [ ] Inspection notes include temperature, packaging, and expiry verification
- [ ] Material Document number generated and recorded
- [ ] Stock update confirmed in MMBE for correct plant/storage location

## COMMON ERRORS & FIXES

| Error | Cause | Fix |
|-------|-------|-----|
| "Storage location not valid for material" | Wrong temperature zone selected | Select Zone-R for perishables, Zone-D for dry goods |
| "Quality inspection required" system block | PERISHABLE-DAIRY material without inspection flag | Enable Quality Inspection checkbox (mandatory at SE-DC) |
| "Material document not generated" | Missing mandatory fields | Verify all required fields completed, especially inspection notes |
| "Stock not updated in MMBE" | Posting incomplete or system delay | Wait 2-3 minutes, refresh MMBE, or check Material Document status |

## NEED HELP?

- **Detailed Process Guide:** SAP Help Portal → MIGO Transaction Guide
- **SE-DC Specific Issues:** Contact SE-DC Warehouse Manager (ext. 5847)
- **System Problems:** SAP Support Desk (ext. 4357)
- **Related Transactions:**
  - **ME23N:** Display Purchase Order details
  - **MMBE:** Stock Overview verification
  - **ME51N:** Create Purchase Requisition (upstream process)