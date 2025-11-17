# Issues

## #1 - Charts redrawing on every page action (High Priority - UX Issue)

**Type:** Performance / User Experience
**Priority:** High
**Status:** Resolved

### Description
Charts are redrawing/re-rendering on every user action (clicking buttons, typing in inputs, etc.), which creates a distracting visual flash/flicker.

### Impact
- Poor user experience during interaction
- Visually distracting when editing purchase quantities
- Makes the app feel less polished

### Expected Behavior
Charts should only redraw when their data actually changes, not on every state update.

### Technical Details
The issue is likely in the `ChartComponent`'s `useEffect` dependency array. Currently it recreates the chart whenever `type`, `data`, or `options` change. Since these objects are being recreated on every render, the chart destroys and recreates itself unnecessarily.

### Proposed Solution
1. Memoize chart data and options using `useMemo`
2. Use deep comparison for chart data/options changes
3. Only call `chart.update()` instead of destroying/recreating when data changes
4. Separate chart initialization from data updates

### Code Location
`index.html` - `ChartComponent` function (around line 135-165)

### Steps to Reproduce
1. Open the app
2. Type in any purchase quantity input field
3. Notice all charts flash/redraw
4. Click any button
5. Notice charts redraw again

### Acceptance Criteria
- [x] Charts only redraw when their actual data changes
- [x] No chart redrawing when editing inputs
- [x] No chart redrawing when clicking unrelated buttons
- [x] Smooth chart updates when data does change

### Resolution
**Date Resolved:** 2025-11-16

**Changes Made:**
1. Updated `ChartComponent` to separate initialization from updates
   - Chart is now created once on mount
   - Subsequent changes use `chart.update('none')` instead of destroying/recreating
2. Memoized all chart data using `useMemo` with proper dependencies
   - `purchaseChartData` depends on `purchaseData`
   - `inventoryChartData` has no dependencies (static data)
   - `arrivalsChartData` has no dependencies (static data)
   - `consumptionChartData` depends on `showDecomposed`
3. Memoized all chart options using `useMemo` with proper dependencies
   - Prevents recreation of options objects on every render
   - Callbacks now properly reference memoized data

**Result:** Charts no longer flash/redraw on unrelated actions. Only update when their actual data changes.

---

*Created: 2024-11-16*
*Reported by: User feedback during demo testing*
*Resolved: 2025-11-16*
