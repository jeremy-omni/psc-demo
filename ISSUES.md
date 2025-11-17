# Issues

## #1 - Charts redrawing on every page action (High Priority - UX Issue)

**Type:** Performance / User Experience
**Priority:** High
**Status:** Open

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
- [ ] Charts only redraw when their actual data changes
- [ ] No chart redrawing when editing inputs
- [ ] No chart redrawing when clicking unrelated buttons
- [ ] Smooth chart updates when data does change

---

*Created: 2024-11-16*
*Reported by: User feedback during demo testing*
