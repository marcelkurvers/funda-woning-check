# React Migration Specification: Magazine Dashboard

## 🏗 High-Level Component Hierarchy

We move from a flat HTML stream to a composed tree of functional components.

```text
<ReportApp>
  ├── <SidebarNavigation />         # Global Left Nav
  │
  ├── <ChapterLayout>               # 4K-Optimized "Magazine" Wrapper
  │   │
  │   ├── <ChapterHeader />         # Title, "Kicker", Meta info
  │   │
  │   └── <SplitLayout>             # The 2/3 + 1/3 Grid Controller
  │       │
  │       ├── <NarrativeColumn>     # (Left) The "Story"
  │       │   ├── <IntroBlock />
  │       │   ├── <AnalysisProse />
  │       │   └── <ConclusionBar />
  │       │
  │       └── <ContextRail>         # (Right) Sticky Visual Stack
  │           ├── <InsightHero />   # The Gradient AI Card
  │           ├── <FeatureGrid />   # Pros/Cons (Green/Yellow)
  │           ├── <AdvisorScore />  # Score Rings
  │           └── <ActionList />    # Checkbox Lists
  │
  └── <MetricsStrip />              # Sticky Top Data Bar
```

---

## 🔄 Data Architecture & Flow

Instead of "policing" the DOM with `querySelector`, we use **Data-Driven Rendering**.

**1. Data Source (Props)**
The `Chapter` component receives a single raw data object (`chapterData`) from the API/State.

**2. Derived State (Hooks)**
We separate the "Narrative" data from the "Context" data using a custom hook or simple selector.

```typescript
// Example: Derived Data Flow
const { narrative, visualContext, features } = useChapterData(chapterData);

// narrative ranges -> <NarrativeColumn />
// visualContext (scores, ai) -> <ContextRail />
// features (pros/cons) -> <ContextRail />
```

**3. Rendering Pattern**
All lists (Pros, Cons, Actions) are rendered via `.map()`:
```jsx
{features.strengths.map(feat => (
  <StatusBadge key={feat.id} type="success" label={feat.label} />
))}
```

---

## 🧩 Component Examples (The "React Way")

### 1. The Layout Controller (`SplitLayout`)
*Encapsulates the CSS Grid & Responsive Logic*

```tsx
import { motion } from 'framer-motion';

export const SplitLayout = ({ children }) => {
  return (
    <div className="grid grid-cols-1 lg:grid-cols-[2fr_1fr] gap-10 items-start w-full max-w-[98vw] mx-auto">
      {children}
    </div>
  );
};

export const ContextRail = ({ children }) => {
  return (
    <motion.aside 
      initial={{ opacity: 0, x: 20 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ delay: 0.2 }}
      className="flex flex-col gap-5 sticky top-4"
    >
      {children}
    </motion.aside>
  );
};
```

### 2. The Insight Hero (`InsightHero`)
*Replaces the Blue Gradient Card with a reusable Component*

```tsx
import { SparklesIcon } from '@heroicons/react/24/solid';

interface InsightHeroProps {
  content: string;
  variant?: 'blue' | 'purple';
}

export const InsightHero = ({ content, variant = 'blue' }: InsightHeroProps) => {
  const gradientClass = variant === 'blue' 
    ? 'bg-gradient-to-br from-blue-600 to-blue-800' 
    : 'bg-gradient-to-br from-purple-600 to-purple-800';

  return (
    <motion.div 
      layout
      className={`rounded-2xl p-6 shadow-xl text-white ${gradientClass}`}
    >
      <div className="flex items-center gap-3 mb-4 border-b border-white/20 pb-3">
        <div className="bg-white/20 p-2 rounded-lg">
          <SparklesIcon className="w-6 h-6 text-white" />
        </div>
        <h3 className="font-bold text-lg tracking-wide uppercase">AI Interpretatie</h3>
      </div>
      
      <p className="text-blue-50 leading-relaxed font-medium">
        {content}
      </p>
    </motion.div>
  );
};
```

### 3. Feature Badges (`StatusBadge`)
*Replaces the hardcoded HTML strings for Pros/Cons*

```tsx
import { CheckCircleIcon, ExclamationTriangleIcon } from '@heroicons/react/24/solid';

interface BadgeProps {
  type: 'success' | 'warning' | 'neutral';
  label: string;
}

export const StatusBadge = ({ type, label }: BadgeProps) => {
  const styles = {
    success: 'bg-emerald-50 text-emerald-900 icon-emerald-600',
    warning: 'bg-amber-50 text-amber-900 icon-amber-600',
    neutral: 'bg-slate-50 text-slate-700 icon-slate-500',
  };

  const Icon = type === 'success' ? CheckCircleIcon : ExclamationTriangleIcon;

  return (
    <motion.div 
      whileHover={{ scale: 1.02 }}
      className={`flex items-center gap-3 p-3 rounded-lg border border-transparent hover:border-black/5 hover:shadow-sm transition-all ${styles[type]}`}
    >
      <div className={`p-1.5 rounded-md bg-white/50`}>
        <Icon className="w-5 h-5" />
      </div>
      <span className="text-sm font-semibold">{label}</span>
    </motion.div>
  );
};
```

---

## 🎨 Design System Tokens

To maintain the gradient/glassmorphism aesthetics without CSS file bloat:

**Gradients**
- `bg-glass-panel` → `backdrop-blur-md bg-white/70 border border-white/20`
- `bg-hero-glow` → `bg-gradient-to-r from-blue-600 to-indigo-600`

**Animations**
- Using **Framer Motion** for exit/entry transitions ensures that when you switch chapters, the content doesn't just "snap" — the old content slides out left, and the new content slides in right.

---

## 🚀 Migration Strategy

Since you currently have a Python backend serving HTML, the migration path is:

1.  **Initialize React Root**: Create a mounting point in `index.html` (`<div id="react-root"></div>`).
2.  **Hybrid Mode**: Use a tool like **Vite** to build a `main.jsx` bundle and inject it into your Python templates.
3.  **Component-by-Component**:
    *   Start by replacing the *Right Sidebar* with a React Root. Pass the sidebar JSON data to it.
    *   Next, replace the *Main Content* area.
    *   Finally, take over the *Navigation* and *Routing*.

This allows you to keep the Python backend logic while progressively enhancing the UI with React.
