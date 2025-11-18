# PSC Demo App Specification - Updated Based on Lina's Mock

## Purpose
Build a clickable prototype matching Lina's vision to demo for James - shows the multi-view analytics interface for purchase planning.

## Mock
![PSC mock](assets/PSC%20mock.png)


## User Stories to Demonstrate

### Story 1: Review and Act on AI Purchase Recommendations
**As a** purchasing officer  
**I want to** see AI-recommended purchase quantities for each rollstock over the coming weeks  
**So that** I can make informed ordering decisions based on forecasted demand

**Workflow:**
1. Select a specific rollstock and width combination to review
2. View the recommended purchase schedule across multiple weeks
3. Understand what quantities the AI suggests ordering and when
4. Decide whether to accept recommendations as-is, modify them, or take no action
5. Commit to a purchase plan that will drive downstream planning

### Story 2: Understand Inventory Implications of Purchase Decisions
**As a** purchasing officer  
**I want to** see how different purchase scenarios affect future inventory levels  
**So that** I can avoid stockouts while minimizing excess inventory

**Workflow:**
1. Compare projected inventory levels under different purchase scenarios
2. Understand the difference between following AI recommendations versus current plans
3. Identify potential stockout risks if purchases are delayed or reduced
4. See the range of inventory outcomes based on demand uncertainty
5. Make risk-informed decisions about purchase timing and quantities

### Story 3: Verify Supply Chain Timing and Material Arrivals
**As a** purchasing officer  
**I want to** understand when ordered materials will arrive given supplier lead times  
**So that** I can ensure inventory is available when customer demand materializes

**Workflow:**
1. See when purchase orders will convert to available inventory
2. Verify that lead times match supplier agreements
3. Understand the gap between placing an order and having material on hand
4. Confirm that material will arrive in time to fulfill customer commitments
5. Identify any timing mismatches that require expediting or alternative planning

### Story 4: Trace Material Requirements to Specific Customer Orders
**As a** purchasing officer or analyst  
**I want to** understand which customer orders are driving material consumption  
**So that** I can prioritize purchases based on customer commitments and explain decisions to stakeholders

**Workflow:**
1. View forecasted material consumption by week
2. Distinguish between confirmed customer orders and expected demand
3. Drill down to see specific orders that require the material
4. Understand which customers and box types are driving requirements
5. Use this traceability to justify purchase decisions and prioritize when capacity is constrained



## Screen Layout (Based on Mock)

### Top Section: Rollstock Selection
```
┌─────────────────────────────────────────────────────────────┐
│ [▼ Rollstock: M23]    [▼ Width: 70.25]                     │
└─────────────────────────────────────────────────────────────┘
```

**Key Changes:**
- **Two separate dropdowns** instead of one combined selector
- Rollstock dropdown (e.g., M23, M24, M25, etc.)
- Width dropdown (e.g., 70.25, 72.5, 80.0, etc.)
- Width options are **conditional** based on selected rollstock (not every rollstock comes in every width)
- See **Data Models & Schema** section for the rollstock-width combinations data structure

**ACTION ITEM - JEREMY:**
- [ ] Synthesize data for valid rollstock/width combinations from PSC data
- [ ] Determine default selection (TBD: most common? highest volume? alphabetical first?)

### Main Content: 4 Visualization Panels

#### Panel 1: Recommended Purchase Schedule

**Visual Components:**
- **Blue bars** = Current user-set purchase quantities (editable via drag or table)
- **Red horizontal lines** = AI resimulator recommendations (baseline/target)
- **Two action buttons:**
  - **"Do Nothing"** - Sets all purchases to zero (shortcut for zero-purchase scenario)
  - **"Reset to Recommended Levels"** - Snaps all bars back to AI recommendations
- **Save button**: Commits current blue bar values

**Load State Behavior:**
- On initial load: Blue bars **match** red horizontal lines exactly
- After user edits bars: Blue bars diverge from red lines (showing user override)
- Checkbox action: Snaps all blue bars back to match red lines
- Red lines are **always visible** as reference baseline

**Editing Methods:**

*Method 1: Drag bars vertically*
- Click and drag top of blue bar up/down
- Shows live value update as you drag
- Snaps to quantized increments (see constraints below)

*Method 2: Edit in table below chart*
```
Week 1    Week 2    Week 3    Week 4    Week 5
[85000]   [60000]   [95000]   [75000]   [140000]
```
- Type new value directly into input field
- Chart updates in real-time as you type
- Tab key to move between weeks
- Value auto-rounds to quantized increment on blur

**Editing Constraints:**

*Quantization:*
- All purchase quantities must be in increments of **1,000 LF** (global across all rollstocks)
- Applies to both drag and table editing
- Example: User can enter 85,000 or 86,000, but not 85,500

*Minimum Order Quantity (MOQ):*
- Each rollstock/width combination has a minimum order quantity
- User cannot set purchase below MOQ for that SKU
- See **Data Models & Schema** section for MOQ values by rollstock-width combination
- If user tries to drag/type below MOQ, value snaps to MOQ
- If resimulator recommendation is below MOQ, it gets rounded up to MOQ

*Visual Cue for MOQ Binding:*
- **[TBD - LEAVE FOR NOW]** Need visual indicator when recommended quantity is constrained by MOQ
- Ideas: Different color for red line? Annotation? Tooltip?

**Interaction Flow:**
1. Load state: Blue bars = Red lines (user hasn't changed anything)
2. User drags Week 1 bar OR edits table → Blue bar moves, red line stays fixed
3. User sees visual divergence from AI recommendation
4. User can continue editing other weeks
5. **Changes are local to Panel 1 only** - Panels 2, 3, 4 still reflect last saved state
6. User has two shortcut options:
   - Click **"Do Nothing"** → All blue bars set to zero (compare no-purchase scenario)
   - Click **"Reset to Recommended Levels"** → All blue bars snap back to red lines
7. User clicks **"Save"** → Commits current purchase schedule and **updates all other panels**
   - Panel 2 (Inventory) recalculates based on new purchase schedule
   - Panel 3 (Arrivals) updates to reflect new order timing
   - Panel 4 (Consumption) remains unchanged (demand-driven, not affected by purchases)

**Save Button Behavior:**
- Acts as transaction commit point
- All panels refresh to reflect new purchase schedule
- Prevents confusion from seeing conflicting data across panels during editing
- Optional: Show "unsaved changes" indicator when blue bars ≠ last saved values

**Data Source:**
- Red lines driven by **resimulator/replay table**
- Primary key: **[TBD - COME BACK TO THIS]**
  - Options to consider:
    - `(rollstock, width, simulation_date, week)`
    - `(rollstock_width_id, forecast_run_id, week)`
    - `(sku_id, planning_period, week_offset)`

**ACTION ITEMS - JEREMY:**
- [ ] Define primary key structure for resimulator lookup table
- [ ] Synthesize minimum order quantity (MOQ) data by rollstock/width combination
- [ ] Confirm quantization level: 1,000 LF or different increment?
- [ ] Decide: Should table show recommended values alongside current values?
- [ ] Design visual cue for when recommendation is bound by MOQ (future iteration)

#### Panel 2: Inventory - On Hand and In Transit

**Chart Title:** "Inventory - On Hand and In Transit"

**Visual Components:**

*Three rendered elements:*

1. **50th percentile inventory levels** (primary projection)
   - Rendered as **points connected by lines**
   - Represents median inventory trajectory
   - This is the main visual focus

2. **10th and 90th percentile inventory** (uncertainty band)
   - Rendered as **shaded area** or **dashed lines** (TBD based on visual preference)
   - Shows inventory range based on 10th/90th percentile order outcomes
   - Illustrates demand uncertainty impact on inventory

3. **Rollstock delivery** (TBD - clarify what this represents)
   - [NEED CLARIFICATION: Is this same as Panel 3 arrivals? Or different metric?]

**Hover Tooltip:**
When user hovers over any week, show:
```
Week 3
10th percentile: 95,000 LF
50th percentile: 115,000 LF
90th percentile: 145,000 LF
Rollstock delivery: [TBD]
```

**Calculation Logic:**
```
Inventory(week) = Starting Inventory - Consumption + Arrivals/Replenishment
```
- Starting inventory = previous week's ending inventory
- Consumption = demand from Panel 4
- Arrivals = purchase orders arriving (from Panel 3, accounting for lead time)

**Unit Toggle (Maybe - TBD):**
- Default view: **Lineal Feet (LF)**
- Alternative view: **Weeks of Demand**
- Toggle button switches between units
- Weeks of demand calculation: `Inventory (LF) / Average Weekly Consumption`
  - **ACTION ITEM - JEREMY:** Define method for calculating "average weekly consumption" (rolling average? forecasted average? specific window?)

**Exception/Alert System**

**Purpose:** Highlight rollstocks that might be in trouble given the large number of SKUs to monitor

**Configurable Thresholds (User-definable):**

*Option 1: Lineal Feet-Based*
- Minimum inventory threshold (e.g., 50,000 LF)
- Maximum inventory threshold (e.g., 500,000 LF)
- Flag weeks where inventory falls outside acceptable range

*Option 2: Weeks of Inventory-Based*
- Minimum weeks of coverage (e.g., 2 weeks)
- Maximum weeks of coverage (e.g., 8 weeks)
- Flag weeks where coverage is too low (stockout risk) or too high (excess inventory)

**Visual Indicators:**
- **Red highlight/marker** on chart when inventory breaches thresholds
- **Yellow warning** when approaching threshold (within 10%?)
- **Icon or badge** on rollstock selector showing number of flagged weeks
- **Filter option** to "Show only rollstocks with exceptions"

**Exception Details (on hover/click):**
```
⚠️ Week 4: Low Inventory Alert
50th percentile: 45,000 LF
Threshold: 50,000 LF minimum
Risk: Potential stockout if demand exceeds forecast
```

**Dashboard Integration:**
- Summary count: "5 rollstocks have inventory exceptions this week"
- Allows purchasing team to prioritize which SKUs need immediate attention
- Reduces decision fatigue across hundreds of rollstock/width combinations

**ACTION ITEMS - JEREMY:**
- [ ] Define default threshold values for PSC (based on their current practices)
- [ ] Decide: Should thresholds vary by rollstock/width or be global?
- [ ] Determine visual design for exception indicators (color, icons, etc.)
- [ ] Decide: Should exceptions be based on 50th percentile only, or also consider 10th/90th?

**Beginning vs. End of Period:**
- [TBD - JEREMY TO DECIDE] Does inventory represent:
  - Beginning of period (before consumption)?
  - End of period (after consumption)?
  - Note: "Probably won't matter that much" but should be consistent

**ACTION ITEMS - JEREMY:**
- [ ] Screenshot current app showing inventory chart
- [ ] Screenshot what forecast hover tooltip looks like in current app
- [ ] Clarify what "rollstock delivery" means in tooltip (vs. inventory arrivals)
- [ ] Define calculation method for "weeks of demand" unit conversion
- [ ] Decide: beginning-of-period or end-of-period inventory?
- [ ] Decide: shaded area or dashed lines for 10th/90th percentiles?

#### Panel 3: Inventory Arrivals

**Visual Components:**
- **Bar chart** showing when ordered inventory arrives
- Green bars = incoming shipments by week
- Shows which weeks have deliveries arriving
- Helps visualize lead time coverage

**Interaction: Hover vs. Click**

*On Hover:*
- Quick summary tooltip showing high-level info
- Example:
```
Week 3: 85,000 LF arriving
From 2 suppliers
Total value: $42,500
```

*On Click:*
- Expands to show detailed PO breakdown
- Opens side panel or modal with full PO-level data
- Shows all PO fields (see Data Models section for complete schema)
- Example:
```
Week 3 Arrivals (85,000 LF total)

PO #12345
  Supplier: Acme Paper Co.
  Rollstock: M23 | Width: 70.25
  Quantity: 50,000 LF
  Cost: $25,000
  Payment Status: Pending
  Ship From: Memphis, TN → Ship To: Charlotte, NC

PO #12346
  Supplier: Summit Materials
  [... full PO details]
```

**Key Insight: Multiple Suppliers Per Week**
- A given week's inventory arrival might come from multiple different suppliers
- Each bar can represent multiple POs aggregated
- Click interaction breaks down the aggregate into constituent POs
- Allows tracing exactly where material is coming from

**ACTION ITEMS - JEREMY:**
- [ ] Review PSC PO file to finalize schema (additional fields needed?)
- [ ] Determine which fields to show on hover vs. click
- [ ] Decide on side panel vs. modal for detailed PO view
- [ ] Identify if there are other PO statuses beyond payment (e.g., in_transit, delayed, etc.)

#### Panel 4: Consumption (Forecast Demand)

**Chart Title:** "Consumption" or "Forecast Demand"

**Visual Components:**
- **Bar chart** showing **forecast** demand/consumption by week
- Bars represent projected material consumption based on customer orders

**Three Interaction States:**

### State 1: Load (Default)

*Initial display:*
- Simple bar chart showing total forecast consumption per week
- Single color bars (e.g., light blue)
- No decomposition or detail

*Behavior:*
- Hover shows basic tooltip: "Week 3: 85,000 LF forecast consumption"
- No click interaction available

### State 2: Checkbox Activated

*Checkbox text:* **"Decompose into confirmed and expected"**

*When checked:*
- Bars become **stacked** showing two segments:
  - **Confirmed demand** (darker blue) = Firm customer orders
  - **Expected demand** (lighter blue/yellow) = Forecasted/anticipated orders
- Visual breakdown shows composition of total demand

*Hover behavior:*
- Tooltip shows total lineal feet consumed in that week
- Example:
```
Week 4: 100,000 LF total
Confirmed: 80,000 LF
Expected: 20,000 LF
```

*Click interaction:*
- Clicking on a stacked bar opens the order detail view (State 3)
- Only works when checkbox is checked

### State 3: Bar Click (Detail View)

*Triggered by:* Clicking on any stacked bar when checkbox is active

*Behavior:*
- **Mini table pops up to the side** (right sidebar or modal)
- Shows detailed information about the orders driving that week's consumption
- Lists specific customer orders contributing to confirmed and expected demand

*Example detail view:*
```
Week 4 Consumption Details (100,000 LF total)

CONFIRMED ORDERS (80,000 LF)
Order #1
  Customer: ABC Corp
  Box Type: Box 2
  Quantity: 12,000 LF
  Ship Date: Nov 25
  [... other order fields]

Order #96
  Customer: XYZ Industries
  Box Type: Box 2
  Quantity: 48,000 LF
  Ship Date: Nov 28
  [... other order fields]

Order #145
  Customer: DEF Company
  Box Type: Box 7
  Quantity: 20,000 LF
  Ship Date: Nov 30
  [... other order fields]

EXPECTED ORDERS (20,000 LF)
[Forecast-based expected demand]
```

**Data Requirements:**
- Order schema should largely mirror PSC's existing order data structure
- See **Data Models & Schema** section for complete orders schema (to be added)

**ACTION ITEMS - JEREMY:**
- [ ] Dig up PSC orders file/schema to define exact fields needed
- [ ] Determine what fields to show in the order detail mini table
- [ ] Decide: Right sidebar vs. modal for order details?
- [ ] Define how "expected" demand is represented (is it order-based or just aggregate forecast?)
- [ ] Clarify distinction between "confirmed" and "expected" orders (status field? date-based?)

---

## Navigation Tabs (Bottom)

Three main views:
1. **Purchase** - Focus on what to buy (recommendations)
2. **Forecast** - Focus on demand projections
3. **Demand orders** - Focus on which customer orders drive needs

---

## Data Models & Schema

This section defines the data structures and schemas used across the application.

### Purchase Order (PO) Schema

Used in **Panel 3** to show detailed arrival information.

```javascript
const purchaseOrderSchema = {
  po_number: 'string',           // Unique PO identifier
  supplier: 'string',            // Supplier name
  rollstock: 'string',           // e.g., 'M23'
  width: 'number',               // e.g., 70.25
  quantity_lf: 'number',         // Lineal feet ordered
  cost: 'number',                // Total dollar amount
  payment_status: 'string',      // 'Paid', 'Pending', 'Overdue', etc.
  ship_from: 'string',           // Origin location
  ship_to: 'string',             // Destination warehouse/facility
  order_date: 'date',            // When PO was placed
  expected_arrival_week: 'number', // Which week it arrives (accounting for lead time)
  lead_time_weeks: 'number'      // Supplier lead time
  // Additional fields can be brainstormed based on PSC PO file
}
```

**Example PO data:**
```javascript
const purchaseOrders = [
  {
    po_number: 'PO-12345',
    supplier: 'Acme Paper Co.',
    rollstock: 'M23',
    width: 70.25,
    quantity_lf: 50000,
    cost: 25000,
    payment_status: 'Pending',
    ship_from: 'Memphis, TN',
    ship_to: 'Charlotte, NC',
    order_date: '2024-11-01',
    expected_arrival_week: 3,
    lead_time_weeks: 2
  },
  {
    po_number: 'PO-12346',
    supplier: 'Summit Materials',
    rollstock: 'M23',
    width: 70.25,
    quantity_lf: 35000,
    cost: 17500,
    payment_status: 'Paid',
    ship_from: 'Atlanta, GA',
    ship_to: 'Charlotte, NC',
    order_date: '2024-11-01',
    expected_arrival_week: 3,
    lead_time_weeks: 2
  }
]
```

### Rollstock-Width Combinations

Used in **Top Section** dropdowns to determine valid selections.

```javascript
const rollstockWidthCombinations = [
  { rollstock: 'M23', widths: [70.25, 72.5, 80.0] },
  { rollstock: 'M24', widths: [70.25, 75.0] },
  { rollstock: 'M25', widths: [80.0, 85.5] }
  // ... additional combinations from PSC data
]
```

### Minimum Order Quantities (MOQ)

Used in **Panel 1** editing constraints.

```javascript
const moqData = {
  'M23-70.25': 50000,  // 50K LF minimum
  'M23-72.5': 40000,
  'M23-80.0': 45000,
  'M24-70.25': 60000,
  'M24-75.0': 55000,
  'M25-80.0': 50000,
  'M25-85.5': 65000
}
```

### Global Constants

```javascript
const constants = {
  quantizationIncrement: 1000,  // Purchase quantities snap to 1K LF increments
  defaultTimeHorizon: 12,       // Default number of weeks to display
  defaultLeadTimeWeeks: 5       // Assumed lead time for deliveries
}
```

### Customer Orders Schema

Used in **Panel 4** to show consumption breakdown by order.

```javascript
const orderSchema = {
  // TBD - Schema to be defined based on PSC orders file
  // Expected fields:
  order_number: 'string',        // Unique order identifier
  customer: 'string',            // Customer name
  box_type: 'string',            // e.g., 'Box 2', 'Box 7'
  rollstock: 'string',           // e.g., 'M23'
  width: 'number',               // e.g., 70.25
  quantity_lf: 'number',         // Lineal feet required
  ship_date: 'date',             // Expected ship date
  order_status: 'string',        // 'Confirmed', 'Expected', etc.
  consumption_week: 'number',    // Which week this order consumes material (1-12)
  // Additional fields from PSC orders file
}
```

**ACTION ITEM - JEREMY:**
- [ ] Dig up PSC orders file and finalize complete schema
- [ ] Determine how to distinguish "confirmed" vs. "expected" orders

---

## Data Flow & Dependencies

This section clarifies how data elements relate to each other and when they update.

### Key Principle

The app has three types of data:
1. **Inputs** - Exogenous data that doesn't change based on user actions in the app
2. **User-Controlled** - Data the user can edit and save
3. **Derived** - Calculated outputs based on inputs and user-controlled data

### State Management Table

| Data Element | Type | Source | Updates When | Used By |
|--------------|------|--------|--------------|---------|
| **Consumption** (Panel 4) | Input | AI demand forecast model | Never (static in app session) | Panel 2 calculation, Panel 4 display |
| **Purchase Schedule** (Panel 1) | User Input | User edits (drag/table) | Continuously while editing; committed on Save | Panel 1 display, Panel 3 calculation |
| **Inventory Arrivals** (Panel 3) | Derived | Purchase Schedule + Lead Time | **Only when Save clicked** | Panel 2 calculation, Panel 3 display |
| **Inventory Projection** (Panel 2) | Derived | Starting Inventory - Consumption + Arrivals | **Only when Save clicked** (via Arrivals update) | Panel 2 display |
| **Starting Inventory** | Input | ERP/current warehouse state | Never (static in app session) | Panel 2 calculation |

### Calculation Formulas

```
Inventory Arrivals(week) = Purchase Schedule(week - lead_time)

Inventory Projection(week) = Starting Inventory 
                              - Σ Consumption(weeks 1 to week)
                              + Σ Arrivals(weeks 1 to week)
```

### Critical Behavior: Save Button

When the user clicks **Save** in Panel 1:
1. Purchase Schedule is committed (blue bars → new baseline)
2. Panel 3 (Arrivals) recalculates based on new purchase schedule
3. Panel 2 (Inventory) recalculates based on new arrivals
4. Panel 4 (Consumption) does NOT change - it's forecast-driven, not purchase-driven

**Why this matters:** Users can edit purchases in Panel 1 and see local changes to the bars, but Panels 2 and 3 stay frozen until Save is clicked. This prevents confusion from seeing conflicting projections while user is still deciding on purchase quantities.

---

## Mock Data Structure

```javascript
const mockData = {
  rollstockWidth: 'M23 70.25',
  
  // Panel 1: Purchase recommendations
  purchaseSchedule: [
    { week: 1, currentQty: 85000, recommendedQty: 85000 },  // initially matching
    { week: 2, currentQty: 60000, recommendedQty: 60000 },
    { week: 3, currentQty: 95000, recommendedQty: 95000 },
    { week: 4, currentQty: 75000, recommendedQty: 75000 },
    { week: 5, currentQty: 140000, recommendedQty: 140000 },
    { week: 6, currentQty: 70000, recommendedQty: 70000 },
    { week: 7, currentQty: 85000, recommendedQty: 85000 },
    { week: 8, currentQty: 90000, recommendedQty: 90000 },
    { week: 9, currentQty: 65000, recommendedQty: 65000 },
    { week: 10, currentQty: 80000, recommendedQty: 80000 },
    { week: 11, currentQty: 95000, recommendedQty: 95000 },
    { week: 12, currentQty: 75000, recommendedQty: 75000 }
  ],
  // Note: currentQty can be edited by user; recommendedQty is fixed from resimulator
  
  // Panel 2: Inventory projection
  inventoryProjection: [
    { week: 1, p10: 110000, p50: 120000, p90: 130000, rollstockDelivery: 0 },
    { week: 2, p10: 100000, p50: 115000, p90: 125000, rollstockDelivery: 0 },
    { week: 3, p10: 130000, p50: 145000, p90: 160000, rollstockDelivery: 85000 }, // week 1 order arrives
    { week: 4, p10: 115000, p50: 130000, p90: 145000, rollstockDelivery: 0 },
    { week: 5, p10: 135000, p50: 155000, p90: 175000, rollstockDelivery: 60000 }, // week 2 order arrives
    { week: 6, p10: 120000, p50: 140000, p90: 160000, rollstockDelivery: 0 },
    { week: 7, p10: 135000, p50: 160000, p90: 185000, rollstockDelivery: 95000 }, // week 3 order arrives
    { week: 8, p10: 115000, p50: 135000, p90: 155000, rollstockDelivery: 0 },
    { week: 9, p10: 125000, p50: 150000, p90: 175000, rollstockDelivery: 75000 }, // week 4 order arrives
    { week: 10, p10: 140000, p50: 165000, p90: 190000, rollstockDelivery: 0 },
    { week: 11, p10: 160000, p50: 190000, p90: 220000, rollstockDelivery: 140000 }, // week 5 order arrives
    { week: 12, p10: 145000, p50: 175000, p90: 205000, rollstockDelivery: 0 }
  ],
  // Note: p10/p50/p90 based on demand uncertainty; rollstockDelivery timing based on lead time
  
  // Panel 3: Incoming arrivals (5-week lead time assumed) WITH PO DETAILS
  arrivals: [
    { 
      week: 1, 
      totalQty: 0,
      pos: []
    },
    { 
      week: 2, 
      totalQty: 0,
      pos: []
    },
    { 
      week: 3, 
      totalQty: 85000,  // order from week 1 arrives
      pos: [
        {
          po_number: 'PO-12345',
          supplier: 'Acme Paper Co.',
          rollstock: 'M23',
          width: 70.25,
          quantity_lf: 50000,
          cost: 25000,
          payment_status: 'Pending',
          ship_from: 'Cleveland, OH',
          ship_to: 'PSC Warehouse A',
          order_date: '2025-11-01',
          expected_arrival_week: 3,
          lead_time_weeks: 2
        },
        {
          po_number: 'PO-12346',
          supplier: 'Beta Materials Inc.',
          rollstock: 'M23',
          width: 70.25,
          quantity_lf: 35000,
          cost: 17500,
          payment_status: 'Paid',
          ship_from: 'Chicago, IL',
          ship_to: 'PSC Warehouse A',
          order_date: '2025-11-01',
          expected_arrival_week: 3,
          lead_time_weeks: 2
        }
      ]
    },
    { 
      week: 4, 
      totalQty: 60000,  // order from week 2 arrives
      pos: [
        {
          po_number: 'PO-12347',
          supplier: 'Acme Paper Co.',
          rollstock: 'M23',
          width: 70.25,
          quantity_lf: 60000,
          cost: 30000,
          payment_status: 'Paid',
          ship_from: 'Cleveland, OH',
          ship_to: 'PSC Warehouse A',
          order_date: '2025-11-08',
          expected_arrival_week: 4,
          lead_time_weeks: 2
        }
      ]
    },
    { 
      week: 5, 
      totalQty: 95000,  // order from week 3 arrives
      pos: [
        {
          po_number: 'PO-12348',
          supplier: 'Gamma Suppliers LLC',
          rollstock: 'M23',
          width: 70.25,
          quantity_lf: 55000,
          cost: 27500,
          payment_status: 'Pending',
          ship_from: 'Detroit, MI',
          ship_to: 'PSC Warehouse B',
          order_date: '2025-11-15',
          expected_arrival_week: 5,
          lead_time_weeks: 2
        },
        {
          po_number: 'PO-12349',
          supplier: 'Beta Materials Inc.',
          rollstock: 'M23',
          width: 70.25,
          quantity_lf: 40000,
          cost: 20000,
          payment_status: 'Paid',
          ship_from: 'Chicago, IL',
          ship_to: 'PSC Warehouse A',
          order_date: '2025-11-15',
          expected_arrival_week: 5,
          lead_time_weeks: 2
        }
      ]
    },
    { week: 6, totalQty: 75000, pos: [/* abbreviated for brevity */] },
    { week: 7, totalQty: 140000, pos: [/* abbreviated for brevity */] },
    { week: 8, totalQty: 70000, pos: [/* abbreviated for brevity */] },
    { week: 9, totalQty: 85000, pos: [/* abbreviated for brevity */] },
    { week: 10, totalQty: 90000, pos: [/* abbreviated for brevity */] },
    { week: 11, totalQty: 65000, pos: [/* abbreviated for brevity */] },
    { week: 12, totalQty: 80000, pos: [/* abbreviated for brevity */] }
  ],
  // Note: Each week can have multiple POs from different suppliers
  
  // Panel 4: Consumption breakdown
  // Note: Orders array should follow Customer Orders schema (see Data Models section)
  // Current simplified structure for demo purposes - will be replaced with full schema
  consumption: [
    { 
      week: 1, 
      total: 65000, 
      confirmed: 50000, 
      expected: 15000,
      orders: [
        { id: 'order #123', box: 'box 2', qty: 30000 },
        { id: 'order #456', box: 'box 5', qty: 35000 }
      ]
    },
    { 
      week: 2, 
      total: 70000, 
      confirmed: 55000, 
      expected: 15000,
      orders: [
        { id: 'order #789', box: 'box 2', qty: 40000 },
        { id: 'order #234', box: 'box 3', qty: 30000 }
      ]
    },
    { 
      week: 3, 
      total: 85000, 
      confirmed: 65000, 
      expected: 20000,
      orders: [
        { id: 'order #567', box: 'box 2', qty: 50000 },
        { id: 'order #890', box: 'box 4', qty: 35000 }
      ]
    },
    { 
      week: 4, 
      total: 100000, 
      confirmed: 80000, 
      expected: 20000,
      orders: [
        { id: 'order #1', box: 'box 2', qty: 12000 },
        { id: 'order #96', box: 'box 2', qty: 48000 },
        { id: 'order #145', box: 'box 7', qty: 40000 }
      ]
    },
    { 
      week: 5, 
      total: 115000, 
      confirmed: 90000, 
      expected: 25000,
      orders: [
        { id: 'order #298', box: 'box 2', qty: 60000 },
        { id: 'order #333', box: 'box 5', qty: 55000 }
      ]
    },
    { 
      week: 6, 
      total: 72000, 
      confirmed: 58000, 
      expected: 14000,
      orders: [
        { id: 'order #401', box: 'box 3', qty: 35000 },
        { id: 'order #402', box: 'box 2', qty: 37000 }
      ]
    },
    { 
      week: 7, 
      total: 88000, 
      confirmed: 70000, 
      expected: 18000,
      orders: [
        { id: 'order #501', box: 'box 4', qty: 45000 },
        { id: 'order #502', box: 'box 2', qty: 43000 }
      ]
    },
    { 
      week: 8, 
      total: 95000, 
      confirmed: 75000, 
      expected: 20000,
      orders: [
        { id: 'order #601', box: 'box 2', qty: 50000 },
        { id: 'order #602', box: 'box 5', qty: 45000 }
      ]
    },
    { 
      week: 9, 
      total: 68000, 
      confirmed: 52000, 
      expected: 16000,
      orders: [
        { id: 'order #701', box: 'box 3', qty: 32000 },
        { id: 'order #702', box: 'box 2', qty: 36000 }
      ]
    },
    { 
      week: 10, 
      total: 82000, 
      confirmed: 65000, 
      expected: 17000,
      orders: [
        { id: 'order #801', box: 'box 4', qty: 40000 },
        { id: 'order #802', box: 'box 2', qty: 42000 }
      ]
    },
    { 
      week: 11, 
      total: 98000, 
      confirmed: 78000, 
      expected: 20000,
      orders: [
        { id: 'order #901', box: 'box 2', qty: 55000 },
        { id: 'order #902', box: 'box 5', qty: 43000 }
      ]
    },
    { 
      week: 12, 
      total: 76000, 
      confirmed: 60000, 
      expected: 16000,
      orders: [
        { id: 'order #1001', box: 'box 3', qty: 38000 },
        { id: 'order #1002', box: 'box 2', qty: 38000 }
      ]
    }
  ]
}
```

---

## Key Interactive Features

### 1. Rollstock Selector
- Dropdown at top
- Changes all 4 panels when new rollstock/width selected
- Shows different mock data for each selection

### 2. Purchase Schedule Actions (Panel 1)
**Two action buttons:**
- **"Do Nothing"**: Sets all purchase quantities to zero (evaluate no-purchase scenario)
- **"Reset to Recommended Levels"**: Snaps all blue bars back to red recommendation lines
- **"Save"**: Commits current purchase schedule and updates Panels 2 & 3

### 3. Consumption Decomposition (Panel 4)
**Checkbox: "Decompose into confirmed and expected"**
- Default (unchecked): Simple bars showing total forecast consumption
- Checked: Stacked bars showing confirmed (darker) vs. expected (lighter) demand
- Hover (when checked): Shows breakdown tooltip with confirmed/expected split
- Click (only when checked): Opens order detail panel showing specific orders driving that week's consumption

### 4. Order Detail Panel (Panel 4 - Right side)
- Triggered by clicking on stacked consumption bars (only when decomposition checkbox is active)
- Mini table showing specific customer orders contributing to that week's demand
- Shows order number, customer, box type, quantity, and other order details
- Separates confirmed vs. expected orders

### 5. Tab Navigation
- Switch between Purchase/Forecast/Demand orders views
- Same data, different emphasis/layout

---

## Visual Design Notes

### Colors
- **Blue bars**: Purchase recommendations (editable)
- **Red horizontal lines**: AI resimulator recommendations (reference baseline)
- **Green bars**: Incoming arrivals (Panel 3)
- **Light/Dark blue stacked**: Confirmed demand (darker) and Expected demand (lighter) in Panel 4
- **Points + lines**: 50th percentile inventory projection (Panel 2)
- **Shaded area/dashed lines**: 10th/90th percentile inventory range (Panel 2)

### Layout
- 4 stacked panels, each roughly equal height
- Clean spacing between panels
- Consistent x-axis (weeks) across all charts
- Right sidebar for order details (slides in/out)

---

## Three View Modes (Tabs)

### Tab 1: Purchase View (Default)
- **Emphasizes**: Panel 1 (recommendations) and Panel 3 (arrivals)
- Use case: "What should I order and when will it arrive?"

### Tab 2: Forecast View
- **Emphasizes**: Panel 2 (inventory projection) and Panel 4 (consumption)
- Use case: "What's my inventory trend and demand outlook?"

### Tab 3: Demand Orders View
- **Emphasizes**: Panel 4 with expanded order details
- Use case: "Which specific customer orders are driving material needs?"

*(In demo, all panels always visible, tabs just change emphasis/ordering)*

---

## Questions for James After Demo

1. **Is the 4-panel view helpful or overwhelming?**
   - Would you prefer a simpler single-chart view?
   - Or do you need all these perspectives?

2. **Confirmed vs. Expected demand breakdown:**
   - Is this distinction important for your decision-making?
   - How do you currently think about "firm" vs. "forecast" orders?

3. **Order detail drill-down:**
   - Would you actually use the order-level detail?
   - Or is aggregate demand sufficient?

4. **Time horizon:**
   - What is the right forecast window for your decision-making?
   - Should each panel show the same time range?

5. **Action workflow:**
   - Is "check box + save" the right approval flow?
   - Or do you need to modify quantities before approving?

6. **Tab navigation:**
   - Do the three views (Purchase/Forecast/Demand) make sense?
   - Would you use them or always stay in one view?

---

## Tech Stack (Vibe Coding)

**Recommendation:** Single HTML file with:
- React (via CDN) for interactivity
- Chart.js or Recharts for the forecast visualization
- Tailwind CSS for styling (match Omnifold design)
- Static mock data in JavaScript objects

**Why:** Can build in 6 hours, easy to iterate based on James' feedback, share as simple file

---

## What This Demo Provides

✅ AI recommendations translated into actionable weekly purchase schedule  
✅ Inventory risk visualization (what happens if you don't follow recommendations)  
✅ Lead time transparency (when orders arrive)  
✅ Demand traceability (which customers drive material needs)  
✅ Complete decision support workflow in single interface  

**Goal:** James says "Yes, this gives me everything I need to confidently make purchase decisions"

---

## Deliverable

**Single HTML file** that:
- Opens in any browser
- Shows realistic-looking data for PSC
- Demonstrates the full interaction flow across 4 panels
- Can be screenshared or sent to James for async review

**Not included:**
- Backend connections
- Real data
- User authentication
- Data persistence
- Production-quality code

---

## Success Criteria

James says one of:
- ✅ "Yes, this is exactly what we need - build it"
- ✅ "This is close, but change X, Y, Z" (then iterate quickly)
- ✅ "This doesn't match our workflow, let me explain..." (learn before building wrong thing)

---

## Next Steps After Demo

1. **Show to James** → Get feedback
2. **Iterate if needed** → Quick changes
3. **Get approval** → "Yes, build this"
4. **Then write real spec** → For Lina/Ishaan to build production version with real data/backend

This prototype is meant to be **disposable** - it's not the actual app, just a way to align on requirements before investing in real development.

---