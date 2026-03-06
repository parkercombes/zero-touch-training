# Navigation Walkthrough: Purchase Requisition to Goods Receipt (Create Purchase Requisition)

## Overview
This walkthrough guides you through creating a Purchase Requisition in SAP S/4HANA Fiori for the Southeast Distribution Center. You'll initiate the procurement process by requesting materials needed for your operations, which will later be converted to a Purchase Order and eventually result in goods receipt.

## Prerequisites
- Role: SE_DC_BUYER with appropriate authorization
- Access to SAP Fiori Launchpad at https://sap.globalmart.com/fiori
- Material information and delivery requirements ready
- Cost center and account assignment details available

## Step-by-Step Instructions

### 1. Access the Purchase Requisition Application
1. Navigate to the SAP Fiori Launchpad homepage
2. In the search box at the top, type **Create Purchase Requisition**
3. Click on the **Create Purchase Requisition** (ME51N) app tile from the search results

**What you should see:** The ME51N transaction opens in the Fiori interface with a blank Purchase Requisition form.

### 2. Set Purchase Requisition Header Information
4. In the **PR Type** dropdown, select **NB - Normally**
   - This is the standard requisition type for regular procurement needs

⚠️ **SE-DC Site Requirement**
5. In the **Purchasing Group** dropdown, select **R-SE - Regional Southeast**
   - SE-DC can only use R-SE (Regional Southeast) or R-NAT (National) purchasing groups per site procurement policy

6. In the **Purchasing Organization** dropdown, select **2000 - GlobalMart Procurement - Southeast Region**

**What you should see:** Header fields populated with your site-specific organizational data.

### 3. Enter Line Item Details
7. In the **Material Number** field for line item 1, enter **SKU-DRY-78432**
   - This example is for Organic Whole Milk, 1 Gallon

8. In the **Quantity** field, enter **500**

9. In the **Unit of Measure** dropdown, select **CS - Case**

10. In the **Requested Delivery Date** field, select a date 7 days from today (e.g., **2026-02-18**)
    - This meets the perishable lead time requirement for cold chain items

### 4. Specify Location and Storage Details
11. In the **Plant** dropdown, select **SE-DC - Southeast Distribution Center (Atlanta, GA)**

12. In the **Storage Location** dropdown, select **Zone-R - Refrigerated Zone (38°F)**
    - This ensures proper temperature-controlled storage for perishable items

### 5. Complete Account Assignment
13. In the **Cost Center** field, enter **CC-SEDC-4200 - SE DC Operations - Perishables**
    - This assigns the cost to the appropriate department budget

⚠️ **SE-DC Mandatory Field**
14. In the **Lot/Batch Number** field, enter **LOT-2026-0215-MK**
    - This field is mandatory at SE-DC for all perishable items to ensure food safety traceability compliance

15. In the **GL Account** field, enter **510200 - Inventory - Refrigerated Goods**
    - This categorizes the expense in the general ledger

**What you should see:** All line item fields completed with validation indicators showing no errors.

### 6. Save the Purchase Requisition
16. Click the **Save** button to create the Purchase Requisition

**What you should see:** A confirmation message displaying the new PR number (e.g., "Purchase Requisition 4500012345 created successfully").

## Verification Checklist
- [ ] Purchase Requisition number generated and displayed
- [ ] Purchasing Group shows R-SE (Regional Southeast)
- [ ] Plant shows SE-DC (Southeast Distribution Center)
- [ ] Storage Location shows Zone-R (Refrigerated Zone)
- [ ] Lot/Batch Number field is populated (mandatory for perishables)
- [ ] Delivery date is within acceptable lead time
- [ ] Cost Center and GL Account are correctly assigned

## Common Issues

**Issue:** "Purchasing Group not authorized" error
**Solution:** Verify you selected either R-SE or R-NAT. Other purchasing groups are restricted for SE-DC users.

**Issue:** Missing Lot/Batch Number validation error
**Solution:** This field is mandatory for perishable items at SE-DC. Enter a valid lot number following the format LOT-YYYY-MMDD-XX.

**Issue:** Storage Location not available
**Solution:** Ensure you selected the correct Plant (SE-DC) first, then choose Zone-R for refrigerated items or the appropriate zone for your material type.