# Mock Data Generation Methodology

## Overview

This demo uses **realistic synthetic data** generated from actual PSC operational data from the last 2 years. The data is filtered and processed to be demo-friendly while maintaining statistical accuracy and business realism.

## Data Sources

All source data comes from `/Users/jeremymcgee/Documents/GitHub/psc_demand/data/`:

1. **`inventory.xlsx`** (15MB) - Purchase order and inventory receipts data
2. **`orders.xlsx`** (101MB) - Customer order data
3. **`conversion.xlsx`** (603KB) - Rollstock specifications and conversions

## Data Filtering Strategy

### Time Window
- **Filter:** Last 2 years of data (from PO_Order_Date)
- **Reasoning:** Captures current operational patterns while excluding obsolete products
- **Result:** 8,351 inventory records from recent operations

### Rollstock Selection

#### Step 1: Volume Analysis
Analyzed all rollstocks by total quantity received (`Qty_Recieved` column) over the last 2 years:

```
Top 10 Rollstocks by Volume:
1. L55      - 38,964 units (17.4%)
2. L35      - 26,761 units (11.9%)
3. M23      - 25,703 units (11.5%)
4. SBS12    - 11,696 units (5.2%)
5. M33      - 10,334 units (4.6%)
6. M33HP    -  9,504 units (4.2%)
7. L35HP    -  8,686 units (3.9%)
8. SBS09    -  5,614 units (2.5%)
9. M36HP    -  5,374 units (2.4%)
10. L563W   -  4,645 units (2.1%)
```

**Coverage:** These 10 rollstocks represent **68.3%** of total inventory volume.

When including all rollstocks purchased in the last 2 years (136 types), coverage increases to **94.7%** of volume.

#### Step 2: Width Extraction

For each of the top 10 rollstocks, extracted **all unique widths** that were actually purchased:

```
Rollstock -> Width Combinations:
- L55:     31 widths (24.625" to 110.0")
- L35:     34 widths
- M23:     35 widths
- SBS12:   13 widths
- M33:     33 widths
- M33HP:   18 widths
- L35HP:    9 widths
- SBS09:   15 widths
- M36HP:    7 widths
- L563W:   16 widths

Total: 211 unique rollstock-width combinations
```

**Rationale:** This approach balances demo usability (manageable dropdown with 10 rollstocks) with realism (all actual width variations for those rollstocks).

## Generated Datasets

### 1. Rollstock/Width Combinations

**Source Column Mapping:**
- Rollstock: `Corr_RS_Desc` (standardized code) or `RS_desc` (fallback)
- Width: `Avg_Width`

**Output Structure:**
```json
{
  "rollstock": "L55",
  "widths": [24.625, 28.0, 28.125, ..., 110.0]
}
```

**Data Integrity:** All combinations are verified against actual purchase history.

### 2. Purchase Schedule (12 weeks)

**Generation Logic:**
- Analyzes `RELEASE_QTY` from orders.xlsx for realistic quantity distributions
- Calculates mean and standard deviation of order quantities
- Generates weekly quantities using normal distribution
- Rounds to 1,000 LF increments (MOQ constraint simulation)
- Initially sets `currentQty` = `recommendedQty` (user can edit via demo)

**Statistical Basis:**
- Mean quantity: ~80,000 LF (from actual orders)
- Standard deviation: ~20,000 LF
- Range: 0 - 140,000 LF typical

### 3. Inventory Projection (12 weeks)

**Generation Logic:**
- Creates 10th, 50th, and 90th percentile projections
- Simulates inventory growth trend (base + weekly accumulation)
- Adds uncertainty band (±15,000 LF around trend)
- Starting inventory: 120,000 LF

**Purpose:** Demonstrates demand uncertainty and risk-based planning.

### 4. Arrivals with PO Details (12 weeks)

**Data Sources:**
- **Vendor Names:** Real suppliers from `Vendor_name` column (top 5 by frequency)
  - INTERNATIONAL PAPER -DEL
  - CLEARWATER PAPER CORPORATION
  - etc.
- **Pricing:** Average cost per unit calculated from `avg_Cost_per_item_Recieved`
- **Rollstock/Width:** Randomly selected from the top 10 rollstock combinations

**PO Schema:**
```json
{
  "po_number": "PO-12345",
  "supplier": "<real vendor name>",
  "rollstock": "<from top 10>",
  "width": "<actual width for that rollstock>",
  "quantity_lf": 64000,
  "cost": 15762.95,
  "payment_status": "Paid/Pending",
  "ship_from": "<realistic location>",
  "ship_to": "PSC Warehouse A",
  "order_date": "2025-11-01",
  "lead_time_weeks": 2
}
```

**Business Rules:**
- Not every week has arrivals (70% probability after week 2)
- 1-3 POs per arrival week
- Quantities: 30,000 - 100,000 LF per PO
- 60% paid, 40% pending (realistic payment distribution)

### 5. Consumption with Order Details (12 weeks)

**Data Sources:**
- **Customer Codes:** Real customer codes from `CSCODE` column (top 10 by frequency)
  - HILCHE, JOIDIR, SBINDT, etc.

**Generation Logic:**
- Total consumption: 60,000 - 120,000 LF per week
- Confirmed vs Expected split: 70-85% confirmed (realistic booking patterns)
- Order details provided for first 5 weeks only (recent visibility)
- 2-4 orders per week with details

**Order Schema:**
```json
{
  "id": "ORD-001",
  "customer": "<real customer code>",
  "box": "Box 2-7",
  "qty": 30000,
  "status": "Confirmed",
  "shipDate": "2025-11-08"
}
```

## Data Validation

### Coverage Verification
Run `analyze_coverage.py` to verify:
```bash
uv run analyze_coverage.py
```

Expected output:
- **Volume coverage:** 94.7% (136 rollstocks) or 68.3% (top 10)
- **Top rollstocks:** All included ✓
- **Record coverage:** ~100% of recent inventory records

### Consistency Checks
1. ✅ All PO rollstocks are from top 10 list
2. ✅ All PO widths are valid for their rollstock
3. ✅ All vendor names are from real data
4. ✅ All customer codes are from real data
5. ✅ Quantities are realistic (based on statistical analysis)

## Regenerating Data

To regenerate with updated source data or different parameters:

```bash
cd ~/Documents/Github/psc-demo
uv run generate_mock_data.py
```

**Script parameters** (edit in `generate_mock_data.py`):
- `NUM_WEEKS`: Number of forecast weeks (default: 12)
- `BASE_DATE`: Starting date for projections (default: 2025-11-01)
- Top N rollstocks: Change `nlargest(10)` on line 72

## File Outputs

**Primary Output:**
- `data/demo_mock_data.json` (16.0 KB)

**Contents:**
- `rollstockWidthCombinations`: 10 rollstocks, 211 combinations
- `purchaseSchedule`: 12 weeks
- `inventoryProjection`: 12 weeks with percentiles
- `arrivals`: 12 weeks with PO details
- `consumption`: 12 weeks with order details

## Design Decisions

### Why Top 10 Rollstocks?
- **Pareto Principle:** 10 rollstocks cover ~68% of volume (80/20 rule in practice)
- **Demo Usability:** Manageable dropdown size for presentations
- **Realism:** Still represents majority of business operations
- **Variety:** 211 combinations show width diversity

### Why Last 2 Years?
- **Relevance:** Current operational patterns and active SKUs
- **Data Quality:** Recent data more accurate and complete
- **Business Changes:** Excludes discontinued products or obsolete processes

### Why Real Values?
- **Credibility:** Demo feels authentic to stakeholders
- **Testing:** Realistic data helps identify edge cases
- **Training:** Users see actual company names and codes

## Maintenance

**When to Regenerate:**
1. Source data updated (new inventory/orders added)
2. Business changes (new rollstocks introduced)
3. Demo requirements change (need different time window)
4. Data quality issues found

**Update Frequency:**
- Recommended: Quarterly or before major demos
- Required: If showing to customers/partners who know the data

## Technical Notes

### Dependencies
- Python 3.10+
- pandas >= 2.0.0
- openpyxl >= 3.1.0
- numpy >= 1.24.0

Managed via `uv` (inline script dependencies).

### Performance
- Full generation: ~30-60 seconds
- Memory usage: ~500MB peak (reading Excel files)
- Output size: 16 KB (git-friendly)

---

*Generated: 2025-11-16*
*Data Window: Last 2 years from source data*
*Coverage: 68.3% of inventory volume (top 10 rollstocks)*
