# Color Coding System - AI Woning Rapport

## Overview
This document explains the semantic color coding system used throughout the AI Woning Rapport application. Colors are used to provide instant visual feedback about property metrics, helping users quickly identify positive aspects, areas of concern, and items requiring caution.

## Color Meanings

### 🟢 Green - Good/Positive
**Meaning:** Indicates favorable conditions, good performance, or desirable characteristics.

**When to use:**
- High energy efficiency (Labels A, B)
- Large living spaces (≥120 m²)
- Modern construction (≥1990)
- Below market pricing
- Low maintenance costs
- Good long-term quality

**Examples:**
- "Uitstekende energie-efficiëntie" - Energy label A or B
- "Ruim woonoppervlak" - Living area ≥120 m²
- "Moderne bouw, goede kwaliteit" - Built after 1990
- "Onder marktprijs" - Price deviation < -5%

### 🟠 Orange/Yellow - Caution/Moderate
**Meaning:** Indicates average performance, areas requiring attention, or moderate concerns.

**When to use:**
- Moderate energy efficiency (Labels C, D)
- Average living spaces (80-120 m²)
- Older construction requiring attention (1970-1990)
- Around market pricing
- Moderate maintenance costs
- Average long-term quality

**Examples:**
- "Gemiddeld, verbetering aanbevolen" - Energy label C or D
- "Gemiddeld woonoppervlak" - Living area 80-120 m²
- "Oudere bouw, aandacht nodig" - Built 1970-1990
- "Rond marktprijs" - Price deviation -5% to +5%
- "Gemiddelde onderhoudskosten (€25,000)" - Moderate renovation costs

### 🔴 Red - Bad/Negative
**Meaning:** Indicates poor performance, significant concerns, or urgent action required.

**When to use:**
- Poor energy efficiency (Labels E, F, G)
- Small living spaces (<80 m²)
- Old construction (< 1970)
- Above market pricing
- High maintenance costs
- Poor long-term quality

**Examples:**
- "Slecht, renovatie dringend nodig" - Energy label E, F, or G
- "Beperkt woonoppervlak" - Living area < 80 m²
- "Oude bouw, mogelijk grote renovatie nodig" - Built before 1970
- "Boven marktprijs" - Price deviation > +5%
- "Hoge onderhoudskosten verwacht (€45,000)" - High renovation costs

## Implementation Details

### CSS Classes

#### Text Colors
```css
.text-green-600, .status-good, .metric-positive
  → Green (#059669) for positive values

.text-orange-500, .text-yellow-600, .status-caution, .metric-warning
  → Orange (#f59e0b) for caution values

.text-red-600, .status-bad, .metric-negative
  → Red (#dc2626) for negative values
```

#### Background Colors
```css
.bg-status-good → Light green background (#ecfdf5)
.bg-status-caution → Light orange background (#fffbeb)
.bg-status-bad → Light red background (#fef2f2)
```

#### Metric Card Styling
```css
.dash-metric-card.metric-good → Green icon background
.dash-metric-card.metric-caution → Orange icon background
.dash-metric-card.metric-bad → Red icon background
```

### Explanation Badges
Each colored metric includes an explanation badge that tells users WHY the metric received its color:

```html
<div class="color-explanation good">
  <ion-icon name="checkmark-circle"></ion-icon>
  Uitstekende energie-efficiëntie
</div>
```

## Metric-Specific Color Logic

### Energy Label (Energielabel)
- **Green:** A, A+, A++, B
- **Orange:** C, D
- **Red:** E, F, G

### Living Area (Woonoppervlakte)
- **Green:** ≥ 120 m²
- **Orange:** 80-119 m²
- **Red:** < 80 m²

### Price Deviation (Prijsafwijking)
- **Green:** < -5% (below market)
- **Orange:** -5% to +5% (around market)
- **Red:** > +5% (above market)

### Construction Year (Bouwjaar)
- **Green:** ≥ 1990 (modern)
- **Orange:** 1970-1989 (attention needed)
- **Red:** < 1970 (old, major renovation likely)

### Maintenance Intensity (Onderhoudsintensiteit)
- **Green:** Low costs (< €10,000)
- **Orange:** Moderate costs (€10,000-€30,000)
- **Red:** High costs (> €30,000)

### Energy Future Score (Energie Toekomstscore)
- **Green:** ≥ 70 (excellent)
- **Orange:** 50-69 (moderate)
- **Red:** < 50 (poor)

### Family Suitability (Gezinsgeschiktheid)
- **Green:** ≥ 120 m² AND ≥ 3 bedrooms
- **Orange:** < 120 m² OR < 3 bedrooms

### Bedrooms (Slaapkamers)
- **Green:** ≥ 4 rooms
- **Orange:** 3 rooms
- **Red:** < 3 rooms

## Best Practices

1. **Always provide explanations:** Every colored metric should include an explanation badge telling users why it has that color.

2. **Be consistent:** Use the same thresholds across all chapters for the same metrics.

3. **Context matters:** Some metrics may not have color coding if they're purely informational (e.g., bathrooms count).

4. **User-friendly language:** Explanations should be in Dutch and easy to understand for non-technical users.

5. **Visual hierarchy:** 
   - Red should be used sparingly for truly concerning issues
   - Green for genuinely positive aspects
   - Orange for everything in between

## Future Enhancements

- Add color-blind friendly patterns/icons
- Implement user preferences for color intensity
- Add tooltips with more detailed explanations
- Create a legend/key on each page explaining the color system
- Add accessibility features (ARIA labels, screen reader support)

## Testing

When adding new colored metrics:
1. Verify the color appears correctly in the UI
2. Check that the explanation badge displays
3. Test with various data values to ensure thresholds work
4. Validate color contrast for accessibility (WCAG AA minimum)
5. Test on different screen sizes and devices

---

**Last Updated:** 2025-12-17
**Version:** 1.0
