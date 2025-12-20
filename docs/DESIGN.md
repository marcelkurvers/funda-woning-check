# AI Woning Rapport - Design System

**Version**: 2.0
**Last Updated**: 2025-12-20

---

## 1. Color Coding System

### 1.1 Semantic Colors

The application uses a standardized color coding system to provide instant visual feedback:

| Color | Hex | Meaning | Use Cases |
|-------|-----|---------|-----------|
| 🟢 **Green** | `#059669` | Good/Positive | Energy A/B, ≥120m², <-5% price, ≥1990 build |
| 🟠 **Orange** | `#f59e0b` | Caution/Moderate | Energy C/D, 80-120m², ±5% price, 1970-1989 |
| 🔴 **Red** | `#dc2626` | Bad/Negative | Energy E/F/G, <80m², >+5% price, <1970 |

### 1.2 Color Thresholds by Metric

| Metric | Green | Orange | Red |
|--------|-------|--------|-----|
| **Energy Label** | A, A+, A++, B | C, D | E, F, G |
| **Living Area** | ≥ 120 m² | 80-119 m² | < 80 m² |
| **Price Deviation** | < -5% | -5% to +5% | > +5% |
| **Build Year** | ≥ 1990 | 1970-1989 | < 1970 |
| **Maintenance Costs** | < €10k | €10k-€30k | > €30k |
| **Energy Future Score** | ≥ 70 | 50-69 | < 50 |
| **Bedrooms** | ≥ 4 | 3 | < 3 |

### 1.3 Implementation

**CSS Classes:**
```css
/* Text Colors */
.text-green-600, .status-good → #059669
.text-orange-500, .status-caution → #f59e0b
.text-red-600, .status-bad → #dc2626

/* Background Colors */
.bg-status-good → #ecfdf5 (light green)
.bg-status-caution → #fffbeb (light orange)
.bg-status-bad → #fef2f2 (light red)
```

**Explanation Badges:**
Every colored metric includes an explanation badge:
```html
<div class="color-explanation good">
  <icon name="checkmark-circle"></icon>
  Uitstekende energie-efficiëntie
</div>
```

**Best Practices:**
1. ✅ Always provide explanations for colored metrics
2. ✅ Use consistent thresholds across all chapters
3. ✅ Context matters - not all metrics need colors
4. ✅ Use Dutch, user-friendly language
5. ✅ Red sparingly for truly concerning issues

---

## 2. Layout Patterns

### 2.1 Current Layout Architecture

**Bento Grid (Current Implementation):**
```
5-column responsive grid
- Grid gap: 12px (0.75rem)
- Auto-rows: minmax(120px, auto)
- Max width: 2560px (4K optimized)
- Breakpoints: mobile (1 col), tablet (3 col), desktop (5 col)
```

**Split View Layout:**
```
┌─────────────────────────────────────────────────┐
│                  Header                         │
├──────────────────┬──────────────────────────────┤
│                  │                              │
│   Narrative      │    Context Rail              │
│   (2/3 width)    │    (1/3 width, sticky)       │
│                  │                              │
│ - IntroBlock     │  - InsightHero (AI)          │
│ - AnalysisProse  │  - FeatureGrid (Pros/Cons)   │
│ - ConclusionBar  │  - AdvisorScore (Rings)      │
│                  │  - ActionList (Checkboxes)   │
│                  │                              │
└──────────────────┴──────────────────────────────┘
```

### 2.2 Context-Aware Chapter Layouts (Planned)

| Layout | Chapters | Visual Design | Key Components |
|--------|----------|---------------|----------------|
| **DashboardLayout** | 0 | Hero stats bar, metrics grid, summary card | Quick overview, key KPIs |
| **MetricsLayout** | 1, 5, 8 | Left metrics panel + right narrative | Data-driven, structured |
| **MatchLayout** | 2 | Split view: Marcel (left) vs Petra (right) | Comparison, preference matching |
| **RiskLayout** | 3, 9 | Risk matrix visual + warning cards | Visual risk assessment |
| **GaugeLayout** | 4 | Energy gauge/dial + improvement checklist | Progress indicators, action items |
| **ComparisonLayout** | 6, 7 | Before/after or indoor/outdoor side-by-side | Visual comparison |
| **FinancialLayout** | 10, 11 | Bar charts, waterfall charts, cost breakdown | Data visualization heavy |
| **ConclusionLayout** | 12 | Large recommendation card + final score | Decision-focused, clear CTA |

**Design Principle:** Each chapter type gets a unique layout that best presents its content type, not a one-size-fits-all grid.

---

## 3. Typography

### 3.1 Font Families

```css
--font-display: 'Inter', sans-serif;
--font-body: 'Noto Sans', sans-serif;
--font-mono: 'JetBrains Mono', monospace;
```

### 3.2 Type Scale

| Element | Size | Weight | Line Height |
|---------|------|--------|-------------|
| H1 (Page Title) | 2.5rem (40px) | 900 | 1.2 |
| H2 (Section) | 1.875rem (30px) | 700 | 1.3 |
| H3 (Subsection) | 1.5rem (24px) | 600 | 1.4 |
| H4 (Card Title) | 1.25rem (20px) | 600 | 1.4 |
| Body | 1rem (16px) | 400 | 1.6 |
| Small | 0.875rem (14px) | 400 | 1.5 |
| Tiny | 0.75rem (12px) | 500 | 1.4 |

---

## 4. Component Library

### 4.1 BentoCard

**Variants:**
- `default` - White background, slate border
- `primary` - Blue gradient, white text
- `highlight` - Amber background, dark text
- `alert` - Red background, dark text
- `ghost` - Transparent, no shadow

**Usage:**
```tsx
<BentoCard
  className="col-span-2"
  title="Energy Analysis"
  icon={<Zap />}
  variant="highlight"
>
  {children}
</BentoCard>
```

### 4.2 Metric Card

**Structure:**
```html
<div class="metric-card metric-{color}">
  <div class="icon-wrapper">
    <Icon />
  </div>
  <div class="label">Woonoppervlakte</div>
  <div class="value">135 m²</div>
  <div class="explanation">Ruim woonoppervlak</div>
</div>
```

### 4.3 Status Badge

```html
<span class="status-badge status-{type}">
  <Icon />
  <span>Label Text</span>
</span>
```

**Types:** `success`, `warning`, `error`, `info`, `neutral`

---

## 5. Design Tokens

### 5.1 New Color Palette (from funda.nl-huis-analyse.zip)

```javascript
colors: {
  primary: "#137fec",
  "background-light": "#f6f7f8",
  "background-dark": "#101922",
  "surface-dark": "#192633",
  "border-dark": "#233648"
}
```

### 5.2 Spacing Scale

```javascript
spacing: {
  px: '1px',
  0.5: '0.125rem',  // 2px
  1: '0.25rem',     // 4px
  2: '0.5rem',      // 8px
  3: '0.75rem',     // 12px
  4: '1rem',        // 16px
  5: '1.25rem',     // 20px
  6: '1.5rem',      // 24px
  8: '2rem',        // 32px
  10: '2.5rem',     // 40px
  12: '3rem',       // 48px
  16: '4rem',       // 64px
}
```

### 5.3 Border Radius

```javascript
borderRadius: {
  DEFAULT: '0.25rem',   // 4px
  lg: '0.5rem',         // 8px
  xl: '0.75rem',        // 12px
  '2xl': '1rem',        // 16px
  '3xl': '1.5rem',      // 24px
  full: '9999px'
}
```

---

## 6. Visual Effects

### 6.1 Glassmorphism

```css
.glass-panel {
  backdrop-filter: blur(12px);
  background: rgba(255, 255, 255, 0.7);
  border: 1px solid rgba(255, 255, 255, 0.2);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
}
```

### 6.2 Gradients

```css
.hero-glow {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.gradient-primary {
  background: linear-gradient(to right, #137fec, #4f46e5);
}

.gradient-success {
  background: linear-gradient(to right, #10b981, #059669);
}
```

### 6.3 Shadows

```css
--shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
--shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
--shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
--shadow-xl: 0 20px 25px -5px rgba(0, 0, 0, 0.1);
--shadow-2xl: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
```

---

## 7. Animation Principles

### 7.1 Framer Motion Patterns

**Page Transitions:**
```tsx
<motion.div
  initial={{ opacity: 0, y: 20 }}
  animate={{ opacity: 1, y: 0 }}
  exit={{ opacity: 0, y: -20 }}
  transition={{ duration: 0.3 }}
>
```

**Card Entrance (Stagger):**
```tsx
<motion.div
  initial={{ opacity: 0, y: 20 }}
  animate={{ opacity: 1, y: 0 }}
  transition={{ duration: 0.4, delay: index * 0.1 }}
>
```

**Hover Effects:**
```tsx
<motion.div
  whileHover={{ scale: 1.02, y: -4 }}
  whileTap={{ scale: 0.98 }}
>
```

### 7.2 Duration Guidelines

- **Micro interactions:** 150-200ms
- **Component animations:** 300-400ms
- **Page transitions:** 400-500ms
- **Skeleton loaders:** 1500ms (loop)

---

## 8. Responsive Design

### 8.1 Breakpoints

```javascript
screens: {
  'sm': '640px',   // Mobile landscape
  'md': '768px',   // Tablet
  'lg': '1024px',  // Desktop
  'xl': '1280px',  // Large desktop
  '2xl': '1536px', // 2K
  '4k': '2560px'   // 4K (custom)
}
```

### 8.2 4K Optimization

**Targets:**
- Hero banner: ~100-120px height (reduced from 200px)
- Metrics cards: gap 0.75rem (tighter spacing)
- Content grid: proportions optimized for width
- Font sizes: slightly smaller for density
- More content visible without scrolling (30-40% improvement)

---

## 9. Accessibility

### 9.1 WCAG AA Compliance

**Color Contrast Requirements:**
- Normal text: 4.5:1 minimum
- Large text (≥18px): 3:1 minimum
- UI components: 3:1 minimum

**Current Status:**
- ✅ Text colors meet 4.5:1 on white backgrounds
- ✅ Icon backgrounds meet 3:1 contrast
- ⚠️ Some glassmorphism effects may need testing

### 9.2 Keyboard Navigation

- ✅ All interactive elements focusable
- ✅ Focus indicators visible
- ✅ Logical tab order
- ⚠️ Skip links needed for long pages

### 9.3 Screen Reader Support

- ✅ Semantic HTML (headings, lists, sections)
- ✅ Alt text for images
- ⚠️ ARIA labels needed for complex components
- ⚠️ Color explanations available for color-blind users

---

## 10. Icon System

### 10.1 Providers

- **Lucide React** - Primary icon set (clean, consistent)
- **Heroicons** - Supplementary icons
- **Material Symbols** - Specific use cases

### 10.2 Sizes

| Context | Size | Usage |
|---------|------|-------|
| Tiny | 16px | Inline text icons |
| Small | 20px | Card headers |
| Medium | 24px | Default |
| Large | 32px | Hero sections |
| XL | 48px | Empty states |

---

## 11. Design Checklist

Before marking a UI component as "done":

- [ ] Applies semantic color coding where appropriate
- [ ] Includes explanation badges for colored metrics
- [ ] Responsive across mobile/tablet/desktop/4K
- [ ] Meets WCAG AA contrast requirements
- [ ] Has smooth animations (Framer Motion)
- [ ] Uses design tokens (not hardcoded values)
- [ ] Follows typography scale
- [ ] Has proper hover/focus states
- [ ] Works with screen readers
- [ ] Tested on different screen sizes

---

**Last Updated:** 2025-12-20
**Version:** 2.0
