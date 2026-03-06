# Navigation Walkthrough: Purchase Requisition to Goods Receipt (Post Goods Receipt - MIGO)

## Overview
This walkthrough guides you through posting a goods receipt in SAP S/4HANA when materials arrive at your warehouse. You'll record the physical receipt of goods against a purchase order, update inventory levels, and ensure proper quality inspection documentation for perishable items.

## Prerequisites
- User access: Receiving Clerk role or equivalent permissions for MIGO transaction
- Purchase Order number ready (e.g., 4500234567)
- Physical goods received and inspected
- Material information available (SKU, quantity, storage requirements)

## Step-by-Step Instructions

### 1. Access the Post Goods Receipt Application
1. Navigate to the SAP Fiori Launchpad at https://sap.globalmart.com/fiori
2. In the **Search** box at the top of the screen, type: `Post Goods Receipt`
3. Click on the **Post Goods Receipt** app tile when it appears in the search results

**What you should see:** The MIGO transaction opens in the Fiori interface with options for different receipt types.

### 2. Configure Receipt Type and Reference Document
4. In the **Movement Type** dropdown, select `101 - Goods Receipt for Purchase Order`
5. In the **Purchase Order Number** field, enter your PO number (example: `4500234567`)
6. Press Enter or click the search button to load the PO details

**What you should see:** The system displays all line items from the purchase order with quantities, materials, and delivery information.

### 3. Enter Receipt Quantities and Storage Details
7. In the **Goods Receipt Quantity** field for the first line item, enter the quantity received (example: `500` for 500 cases)
8. In the **Storage Location** dropdown for the line item, select the appropriate storage zone

> ⚠️ **SE-DC Specific Requirement**  
> For perishable items at the Southeast Distribution Center, you must select **Zone-R (Refrigerated Zone)** to maintain the cold chain. The system validates that temperature-sensitive products are assigned to climate-controlled storage areas.

**What you should see:** The system updates the line item with your quantity and storage location. The total value should calculate automatically.

### 4. Configure Quality Inspection (Required for Perishables)
9. Check the **Quality Inspection** checkbox for the line item

> ⚠️ **SE-DC Specific Requirement**  
> Quality inspection is mandatory for all perishable and private-label goods at SE-DC. This checkbox must be selected to comply with distribution center policies and cannot be bypassed.

10. In the **Quality Inspection Notes** field, document your inspection results including:
    - Temperature readings
    - Packaging condition
    - Expiry dates
    - Lot numbers
    
    Example: `Temperature at receiving: 36°F (within 33-40°F range). Packaging intact. Expiry date: 2026-03-01. Lot LOT-2026-0215-MK verified.`

### 5. Post the Goods Receipt
11. Review all line items to ensure quantities and storage locations are correct
12. Click the **Post** button to finalize the goods receipt

**What you should see:** A confirmation message displays with the material document number (example: 5000123456). This confirms the receipt was posted successfully.

### 6. Verify Stock Update
13. Navigate to **Stock Overview** by entering transaction code `MMBE` or searching for "Stock Overview" in the Fiori search
14. In the **Material** field, enter the material number (example: `SKU-DRY-78432`)
15. In the **Plant** filter, select `SE-DC (GlobalMart Southeast Distribution Center)`
16. In the **Storage Location** filter, select your storage location (example: `Zone-R`)

**What you should see:** The stock levels show your newly received quantity in the specified storage location.

## Verification Checklist
- [ ] Material document number generated and saved
- [ ] Stock levels updated in correct storage location
- [ ] Quality inspection flagged for perishable items
- [ ] Temperature zone requirements met for cold chain items
- [ ] All PO line items processed or remaining quantities noted

## Common Issues and Solutions

**Issue:** "Storage location not valid for material" error  
**Solution:** Verify the storage location matches the material's temperature requirements. Perishable items must go to refrigerated zones (Zone-R at SE-DC).

**Issue:** Cannot post without quality inspection  
**Solution:** Ensure the Quality Inspection checkbox is selected for perishable and private-label items. Add inspection notes documenting temperature, condition, and lot information.

**Issue:** Quantity exceeds purchase order amount  
**Solution:** Check if you're entering the quantity in the correct unit of measure (cases vs. individual units). Verify the actual quantity received against the delivery note and PO.