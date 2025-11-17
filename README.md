# PSC Purchase Planning Demo

A clickable prototype for demonstrating multi-view analytics interface for purchase planning.

## Purpose

Build a demo matching the vision from the spec to showcase:
- AI-powered purchase recommendations
- Inventory risk visualization
- Lead time transparency
- Demand traceability

## How to Run

Simply open `index.html` in any modern web browser. No build process or server required.

## Features

### Panel 1: Recommended Purchase Schedule
- View AI recommendations vs current purchase plan
- Edit quantities via drag or table input
- Actions: "Do Nothing", "Reset to Recommended", "Save"
- Quantities snap to 1,000 LF increments

### Panel 2: Inventory - On Hand and In Transit
- Shows 10th, 50th, and 90th percentile inventory projections
- Visualizes inventory range based on demand uncertainty
- Updates when purchase schedule is saved

### Panel 3: Inventory Arrivals
- Bar chart showing incoming shipments by week
- Hover for quick summary, click for detailed PO breakdown
- Shows multiple suppliers per week

### Panel 4: Consumption (Forecast Demand)
- Toggle between simple and decomposed view
- Decomposed view shows confirmed vs expected demand
- Click on bars to see specific customer orders (when decomposed)

## Tech Stack

- React 18 (via CDN)
- Recharts 2.5 (for visualizations)
- Tailwind CSS (for styling)
- Single HTML file - no build process

## Data Structure

All data is currently mocked in JavaScript objects within the HTML file. See the spec document for complete data schemas:
- Purchase Order schema
- Rollstock-Width combinations
- Minimum Order Quantities (MOQ)
- Customer Orders schema

## Next Steps

1. Show demo to stakeholders
2. Gather feedback
3. Iterate on design/functionality
4. Build production version with real data and backend integration

## Notes

This is a disposable prototype meant to align on requirements before investing in full development. It is NOT production code.
