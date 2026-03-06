# Purchase Requisition to Goods Receipt — Quick Reference for Buyer

**Site:** Southeast Distribution Center (SE-DC)  
**Transaction:** ME51N (via Fiori)  
**Last Updated:** 2026-02-11

---

## WHEN TO USE THIS

Use this process when creating purchase requisitions for materials needed at SE-DC. Triggered by inventory needs, store requests, or replenishment requirements that require formal procurement approval.

---

## BEFORE YOU START

- **Access Required:** SE_DC_BUYER role in SAP S/4HANA
- **Have Ready:** Material numbers, quantities needed, delivery dates, cost center information
- **Check:** Supplier agreements and current inventory levels
- **Verify:** Budget availability for requested items

---

## KEY FIELDS REFERENCE TABLE

| Field | Where to Find It | What to Enter | Site Rule |
|-------|------------------|---------------|-----------|
| **PR Type** | PR Type dropdown | NB (Normally) | Standard |
| **Purchasing Group** | Purchasing Group dropdown | R-SE or R-NAT only | ⚠️ SE-DC restricted |
| **Purchasing Org** | Purchasing Organization dropdown | 2000 (SE Region) | Standard |
| **Material Number** | Material Number field | SKU code (e.g., SKU-DRY-78432) | Standard |
| **Quantity** | Quantity field | Numeric value | Standard |
| **Unit of Measure** | UoM dropdown | CS, EA, etc. | Standard |
| **Delivery Date** | Delivery Date field | Date (7 days max for perishables) | ⚠️ SE-DC perishable rule |
| **Plant** | Plant dropdown | SE-DC | Standard |
| **Storage Location** | Storage Location dropdown | Zone-R (refrigerated), Zone-D (dry) | Standard |
| **Cost Center** | Cost Center field | CC-SEDC-#### format | Standard |
| **Lot/Batch Number** | Lot/Batch field (CHARG) | LOT-YYYY-MMDD-XX format | ⚠️ SE-DC mandatory for perishables |
| **GL Account** | GL Account field | 510200 (refrigerated), 510100 (dry) | Standard |

---

## STEP-BY-STEP (Condensed)

1. **Navigate:** Open Fiori Launchpad → Search "Create Purchase Requisition" → Click ME51N tile
2. **Set Type:** Select PR Type = **NB** (Normally)
3. **Set Groups:** Purchasing Group = **R-SE** or **R-NAT** only | Purchasing Organization = **2000**
4. **Add Item:** Enter **Material Number** → Verify description auto-populates
5. **Set Quantities:** Enter **Quantity** and **Unit of Measure** (CS for cases)
6. **Set Delivery:** Select **Delivery Date** (max 7 days for perishables) | Plant = **SE-DC**
7. **Set Location:** Choose appropriate **Storage Location** (Zone-R for refrigerated)
8. **Account Assignment:** Enter **Cost Center** (CC-SEDC-####) and **GL Account**
9. **Lot/Batch:** ⚠️ Enter **Lot/Batch Number** (mandatory for perishables at SE-DC)
10. **Review:** Verify all mandatory fields completed and amounts under $25K threshold
11. **Save:** Click Save button → Note generated PR number and approval status

---

## SITE-SPECIFIC RULES (SE-DC)

> **⚠️ SE-DC Variations from Enterprise Standard**
>
> - **Purchasing Groups:** Enterprise: All groups allowed → **SE-DC: R-SE or R-NAT only** — Regional supplier agreements
> - **Perishable Delivery:** Enterprise: 14-day max → **SE-DC: 7-day max** — Cold chain requirements  
> - **Lot/Batch Tracking:** Enterprise: Optional → **SE-DC: Mandatory for perishables** — Food safety traceability
> - **Approval Threshold:** Enterprise: $50K → **SE-DC: $25K** — Local authorization limits
> - **Storage Zones:** Enterprise: Generic → **SE-DC: Zone-R (38°F), Zone-D** — Temperature-controlled zones

---

## VERIFICATION CHECKLIST

- [ ] PR Type set to "NB"
- [ ] Purchasing Group is R-SE or R-NAT
- [ ] Material description auto-populated correctly  
- [ ] Delivery date within 7 days for perishables
- [ ] Plant set to SE-DC
- [ ] Lot/Batch number entered for perishable items
- [ ] Cost center matches your department (CC-SEDC-####)
- [ ] PR total under $25,000 for standard approval routing
- [ ] All mandatory fields completed (no red asterisks)

---

## COMMON ERRORS & FIXES

| Error | Cause | Fix |
|-------|--------|-----|
| "Purchasing Group not allowed" | Selected group outside R-SE/R-NAT | Change to R-SE (Regional Southeast) or R-NAT (National) |
| "Lot/Batch number required" | Missing lot number for perishable item | Enter format: LOT-YYYY-MMDD-XX |
| "Delivery date too far out" | Date >7 days for perishable | Select date within 7 days of today |
| "Cost center invalid" | Wrong format or inactive cost center | Use CC-SEDC-#### format, verify with Finance |

---

## NEED HELP?

- **Detailed Process:** SAP Help Portal → Procurement → Purchase Requisitions
- **Site Questions:** Contact SE-DC Procurement Team (ext. 4200)  
- **System Issues:** IT Help Desk (ext. 8888)
- **Related Transactions:** ME21N (Convert to PO), ME53N (Display PR)

**Next Step:** After approval, convert PR to Purchase Order using ME21N or monitor in approval workflow.