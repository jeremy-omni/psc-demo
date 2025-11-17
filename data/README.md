# Demo Data Directory

This directory contains realistic mock data generated from actual PSC operational data.

## Files

### `demo_mock_data.json` (16 KB)
**Primary demo data file** - Contains all data needed for the purchase planning demo.

**Contents:**
- **rollstockWidthCombinations** - Top 10 rollstocks with all their widths (211 combinations)
- **purchaseSchedule** - 12 weeks of purchase planning data
- **inventoryProjection** - 12 weeks of inventory forecasts (10th/50th/90th percentiles)
- **arrivals** - 12 weeks of incoming PO shipments with supplier details
- **consumption** - 12 weeks of demand forecast with customer order details

**Source:** Generated from last 2 years of real PSC data (inventory.xlsx, orders.xlsx)

**Coverage:** Represents 68.3% of actual inventory volume

## Data Characteristics

### Real Values Used:
- ✅ Rollstock codes (L55, M23, SBS12, etc.)
- ✅ Width dimensions (actual purchased widths)
- ✅ Vendor names (INTERNATIONAL PAPER, CLEARWATER PAPER, etc.)
- ✅ Customer codes (HILCHE, JOIDIR, SBINDT, etc.)
- ✅ Quantity distributions (based on statistical analysis)

### Synthetic Elements:
- Weekly quantities (generated from real distributions)
- PO assignments (which PO delivers which rollstock)
- Specific dates (structured for 12-week demo window)

## Usage

### In HTML Demo:
```javascript
// Load the mock data
fetch('data/demo_mock_data.json')
  .then(response => response.json())
  .then(data => {
    // Use data.rollstockWidthCombinations for dropdown
    // Use data.purchaseSchedule for Panel 1
    // Use data.inventoryProjection for Panel 2
    // Use data.arrivals for Panel 3
    // Use data.consumption for Panel 4
  });
```

### Regenerating Data:
```bash
uv run generate_mock_data.py
```

See `../DATA_GENERATION.md` for full methodology and documentation.

## Data Quality Metrics

- **Rollstocks:** 10 types (top by volume)
- **Combinations:** 211 rollstock-width pairs
- **Volume Coverage:** 68.3% of 2-year inventory
- **Vendors:** Real supplier names from data
- **Customers:** Real customer codes from data
- **POs:** 14 purchase orders across 12 weeks
- **Orders:** 11 customer orders with details

---

*Last Generated: 2025-11-16*
*See DATA_GENERATION.md for complete documentation*
