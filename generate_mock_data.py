#!/usr/bin/env -S uv run --script
# /// script
# dependencies = [
#   "pandas>=2.0.0",
#   "openpyxl>=3.1.0",
#   "sdv>=1.0.0",
#   "numpy>=1.24.0",
# ]
# ///
"""
Generate realistic mock data for PSC demo using SDV (Synthetic Data Vault)
Outputs data in the exact format needed by the demo (12-week structure)
"""

import json
import pandas as pd
import numpy as np
from pathlib import Path
from sdv.single_table import GaussianCopulaSynthesizer
from sdv.metadata import SingleTableMetadata
from datetime import datetime, timedelta

# Paths
DATA_DIR = Path("/Users/jeremymcgee/Documents/GitHub/psc_demand/data")
OUTPUT_DIR = Path(__file__).parent / "data"
OUTPUT_DIR.mkdir(exist_ok=True)

# Demo constants
NUM_WEEKS = 12
BASE_DATE = datetime(2025, 11, 1)

def extract_rollstock_width_combinations():
    """Extract top 10 rollstocks by volume with all their widths from last 2 years"""
    print("📊 Extracting top 10 rollstocks by volume with all widths...")

    # Try multiple data sources to get rollstock/width combinations
    cutoff_date = pd.Timestamp.now() - pd.DateOffset(years=2)

    # Load inventory data
    print("  - Loading inventory data...")
    inv_df = pd.read_excel(DATA_DIR / "inventory.xlsx")

    # Filter for last 2 years if date column exists
    if 'PO_Order_Date' in inv_df.columns:
        inv_df['PO_Order_Date'] = pd.to_datetime(inv_df['PO_Order_Date'], errors='coerce')
        recent_inv = inv_df[inv_df['PO_Order_Date'] >= cutoff_date].copy()
        print(f"    Found {len(recent_inv)} inventory records from last 2 years")
    else:
        recent_inv = inv_df.copy()
        print(f"    No date filter available, using all {len(recent_inv)} records")

    # Extract rollstock column
    rollstock_col = 'Corr_RS_Desc' if 'Corr_RS_Desc' in recent_inv.columns else 'RS_desc'
    recent_inv['rollstock'] = recent_inv[rollstock_col].fillna(recent_inv.get('RS_desc', ''))

    # Calculate volume by rollstock
    print("  - Calculating volume by rollstock...")
    qty_cols = ['Qty_Recieved', 'Qty_Ordered', 'Expected_Incoming_qty']
    qty_col = None
    for col in qty_cols:
        if col in recent_inv.columns:
            qty_col = col
            break

    if qty_col is None:
        print("  ⚠️  No quantity column found, using record count")
        rollstock_volumes = recent_inv.groupby('rollstock').size()
    else:
        rollstock_volumes = recent_inv.groupby('rollstock')[qty_col].sum()

    # Get top 10 rollstocks by volume
    top_10_rollstocks = rollstock_volumes.nlargest(10).index.tolist()

    print(f"  - Top 10 rollstocks by volume:")
    for i, rollstock in enumerate(top_10_rollstocks, 1):
        vol = rollstock_volumes[rollstock]
        print(f"    {i}. {rollstock}: {vol:,.0f}")

    # Extract all widths for these top 10 rollstocks
    print("  - Extracting all widths for top 10 rollstocks...")
    rollstock_widths = {}

    if 'Avg_Width' in recent_inv.columns:
        for rollstock in top_10_rollstocks:
            rollstock_data = recent_inv[recent_inv['rollstock'] == rollstock]
            widths = rollstock_data['Avg_Width'].dropna()
            widths = widths[widths > 0].unique()

            if len(widths) > 0:
                rollstock_widths[rollstock] = sorted([float(w) for w in widths])

    # Convert to output format
    combinations = []
    total_combos = 0
    for rollstock in top_10_rollstocks:
        if rollstock in rollstock_widths and len(rollstock_widths[rollstock]) > 0:
            widths = rollstock_widths[rollstock]
            combinations.append({
                'rollstock': rollstock,
                'widths': widths
            })
            total_combos += len(widths)

    # If we didn't find any, use a sensible fallback
    if len(combinations) == 0:
        print("  ⚠️  No rollstock/width combinations found, using defaults")
        combinations = [
            {'rollstock': 'M23', 'widths': [70.25, 72.5, 80.0]},
            {'rollstock': 'M24', 'widths': [70.25, 75.0]},
            {'rollstock': 'M25', 'widths': [80.0, 85.5]}
        ]
        total_combos = sum(len(c['widths']) for c in combinations)

    print(f"\n✅ Extracted {len(combinations)} rollstock types with {total_combos} total combinations:")
    for combo in combinations:
        print(f"    - {combo['rollstock']}: {len(combo['widths'])} widths")

    return combinations

def generate_purchase_schedule(orders_df):
    """Generate 12-week purchase schedule with AI recommendations"""
    print("\n🎲 Generating 12-week purchase schedule...")

    # Analyze order quantities to get realistic ranges
    if 'RELEASE_QTY' in orders_df.columns:
        qty_stats = orders_df['RELEASE_QTY'].describe()
        mean_qty = qty_stats['mean'] if not pd.isna(qty_stats['mean']) else 80000
        std_qty = qty_stats['std'] if not pd.isna(qty_stats['std']) else 20000
    else:
        mean_qty = 80000
        std_qty = 20000

    schedule = []
    for week in range(1, NUM_WEEKS + 1):
        # Generate realistic quantity (rounded to 1000s)
        base_qty = np.random.normal(mean_qty, std_qty)
        qty = max(0, round(base_qty / 1000) * 1000)

        schedule.append({
            'week': week,
            'currentQty': int(qty),
            'recommendedQty': int(qty)  # Initially same as current
        })

    print(f"✅ Generated {len(schedule)} weeks of purchase data")
    return schedule

def generate_inventory_projection():
    """Generate 12-week inventory projection with percentiles"""
    print("\n🎲 Generating inventory projection (10th/50th/90th percentiles)...")

    projection = []
    base_inventory = 120000  # Starting inventory

    for week in range(1, NUM_WEEKS + 1):
        # Simulate inventory growth with uncertainty
        trend = base_inventory + (week * 5000)
        uncertainty = 15000

        projection.append({
            'week': week,
            'p10': int(trend - uncertainty),
            'p50': int(trend),
            'p90': int(trend + uncertainty)
        })

    print(f"✅ Generated {len(projection)} weeks of inventory projection")
    return projection

def generate_arrivals_with_pos(inventory_df, rollstock_combos):
    """Generate 12-week arrivals schedule with realistic PO details"""
    print("\n🎲 Generating arrivals with PO details...")

    # Extract real vendor names from inventory data
    vendors = []
    if 'Vendor_name' in inventory_df.columns:
        vendors = inventory_df['Vendor_name'].dropna().unique()[:5].tolist()
    if not vendors:
        vendors = ['Acme Paper Co.', 'Beta Materials Inc.', 'Clearwater Paper']

    # Extract realistic cost patterns
    if 'avg_Cost_per_item_Recieved' in inventory_df.columns:
        costs = inventory_df['avg_Cost_per_item_Recieved'].dropna()
        avg_cost_per_unit = costs.mean() if len(costs) > 0 else 0.50
    else:
        avg_cost_per_unit = 0.50  # $0.50 per LF

    # Build list of all possible rollstock/width combinations
    all_combos = []
    for combo in rollstock_combos:
        for width in combo['widths']:
            all_combos.append((combo['rollstock'], width))

    arrivals = []
    po_counter = 12345

    for week in range(1, NUM_WEEKS + 1):
        # Not every week has arrivals
        if week < 3 or np.random.random() < 0.3:
            arrivals.append({'week': week, 'totalQty': 0, 'pos': []})
            continue

        # Generate 1-3 POs for this week
        num_pos = np.random.randint(1, 3)
        pos = []
        total_qty = 0

        for _ in range(num_pos):
            qty = np.random.randint(30000, 100000)
            qty = round(qty / 1000) * 1000  # Round to 1000s
            total_qty += qty

            cost = qty * avg_cost_per_unit

            # Pick a random rollstock/width combo from the top 10
            rollstock, width = all_combos[np.random.randint(0, len(all_combos))]

            po = {
                'po_number': f'PO-{po_counter}',
                'supplier': np.random.choice(vendors),
                'rollstock': rollstock,
                'width': width,
                'quantity_lf': qty,
                'cost': round(cost, 2),
                'payment_status': np.random.choice(['Paid', 'Pending'], p=[0.6, 0.4]),
                'ship_from': np.random.choice(['Cleveland, OH', 'Chicago, IL', 'Memphis, TN']),
                'ship_to': 'PSC Warehouse A',
                'order_date': (BASE_DATE + timedelta(weeks=week-2)).strftime('%Y-%m-%d'),
                'lead_time_weeks': 2
            }
            pos.append(po)
            po_counter += 1

        arrivals.append({
            'week': week,
            'totalQty': total_qty,
            'pos': pos
        })

    print(f"✅ Generated {len(arrivals)} weeks of arrival data with POs")
    return arrivals

def generate_consumption_with_orders(orders_df):
    """Generate 12-week consumption forecast with order details"""
    print("\n🎲 Generating consumption forecast with order details...")

    # Extract real customer info from orders
    customers = []
    if 'CSCODE' in orders_df.columns:
        customers = orders_df['CSCODE'].dropna().unique()[:10].tolist()
    if not customers:
        customers = ['ABC Corp', 'XYZ Ltd', 'Acme Industries', 'GlobalTech', 'MegaCorp']

    consumption = []
    order_counter = 1

    for week in range(1, NUM_WEEKS + 1):
        # Generate total consumption
        total = np.random.randint(60000, 120000)
        total = round(total / 1000) * 1000

        # Split into confirmed and expected (70-80% confirmed)
        confirmed_pct = np.random.uniform(0.7, 0.85)
        confirmed = int(total * confirmed_pct)
        expected = total - confirmed

        # Generate 2-4 orders for weeks with details
        orders = []
        if week <= 5:  # Only first 5 weeks have detailed orders
            num_orders = np.random.randint(2, 4)
            remaining = confirmed

            for i in range(num_orders):
                if i == num_orders - 1:
                    qty = remaining
                else:
                    qty = np.random.randint(10000, min(50000, remaining))
                    qty = round(qty / 1000) * 1000
                    remaining -= qty

                orders.append({
                    'id': f'ORD-{order_counter:03d}',
                    'customer': np.random.choice(customers),
                    'box': f'Box {np.random.randint(2, 8)}',
                    'qty': qty,
                    'status': 'Confirmed',
                    'shipDate': (BASE_DATE + timedelta(weeks=week)).strftime('%Y-%m-%d')
                })
                order_counter += 1

        consumption.append({
            'week': week,
            'total': total,
            'confirmed': confirmed,
            'expected': expected,
            'orders': orders
        })

    print(f"✅ Generated {len(consumption)} weeks of consumption data")
    return consumption

def main():
    """Generate all mock datasets matching demo structure"""
    print("🚀 Starting realistic mock data generation for PSC demo\n")
    print("=" * 70)

    try:
        # Load real data for learning patterns
        print("\n📥 Loading real data files...")
        orders_df = pd.read_excel(DATA_DIR / "orders.xlsx", nrows=5000)
        inventory_df = pd.read_excel(DATA_DIR / "inventory.xlsx", nrows=5000)

        # Generate demo-specific datasets
        print("\n" + "=" * 70)
        print("🎯 Generating demo-specific datasets...")
        print("=" * 70)

        rollstock_combos = extract_rollstock_width_combinations()
        purchase_schedule = generate_purchase_schedule(orders_df)
        inventory_projection = generate_inventory_projection()
        arrivals = generate_arrivals_with_pos(inventory_df, rollstock_combos)
        consumption = generate_consumption_with_orders(orders_df)

        # Combine into single output matching demo structure
        demo_data = {
            'rollstockWidthCombinations': rollstock_combos,
            'purchaseSchedule': purchase_schedule,
            'inventoryProjection': inventory_projection,
            'arrivals': arrivals,
            'consumption': consumption
        }

        # Save as single JSON file
        output_file = OUTPUT_DIR / "demo_mock_data.json"
        with open(output_file, 'w') as f:
            json.dump(demo_data, f, indent=2)

        print("\n" + "=" * 70)
        print("✨ Mock data generation complete!")
        print("=" * 70)
        print(f"\n📁 Output file: {output_file}")
        print(f"📊 File size: {output_file.stat().st_size / 1024:.1f} KB")
        print(f"\n📈 Data summary:")
        print(f"  - Rollstock combinations: {len(rollstock_combos)}")
        print(f"  - Purchase schedule weeks: {len(purchase_schedule)}")
        print(f"  - Inventory projection weeks: {len(inventory_projection)}")
        print(f"  - Arrival weeks: {len(arrivals)}")
        print(f"  - Total POs: {sum(len(w['pos']) for w in arrivals)}")
        print(f"  - Consumption weeks: {len(consumption)}")
        print(f"  - Total orders: {sum(len(w['orders']) for w in consumption)}")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
