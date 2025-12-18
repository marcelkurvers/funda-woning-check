# AI Woning Rapport - Frontend

The frontend is a modern React application built with TypeScript, Vite, and Tailwind CSS. It is designed to provide a premium, dashboard-like experience for real estate analysis.

## 🎨 UI/UX Philosophy

The interface follows a **"Bento Grid"** (Raster) layout system:
- **Maximized Vertical Space**: No scrolling where possible; data is presented in a structured grid.
- **Semantic Color Coding**: Blues for info, Emerald for strengths, Amber for warnings, and Rose for critical issues.
- **Split-View Chapters**: Narrative analysis on the left, visual KPI cards and widgets on the right.
- **4K Optimized**: The layout scale dynamically to support high-resolution displays.

## 🏗 Key Components

- **`src/components/layout/BentoLayout.tsx`**: The core grid system using CSS Grid.
- **`src/components/ui/BentoCard.tsx`**: Individual containers for metrics and charts.
- **`src/components/ChapterRenderer.tsx`**: Orchestrates the rendering of different chapter types based on backend data.
- **`src/hooks/useRunStatus.ts`**: React Hook for handling SSE updates and polling.

## 🛠 Tech Stack

- **Framework**: React 18
- **Build Tool**: Vite
- **Styling**: Tailwind CSS v3
- **Icons**: Lucide React
- **Type Checking**: TypeScript

## 🚀 Getting Started

### Installation
```bash
npm install
```

### Development
```bash
npm run dev
```
The app will be available at `http://localhost:5173`. Ensure the backend is running at `http://localhost:8000` for API requests.

### Build
```bash
npm run build
```
The production assets will be generated in the `dist/` folder, which is also served by the FastAPI backend in production mode.

## 📁 Structure

- `src/components/`: Reusable UI elements.
- `src/pages/`: Main page views (Landing, Preferences, Report).
- `src/types/`: TypeScript interfaces mirroring backend Pydantic models.
- `src/styles/`: Global CSS and Tailwind configurations.

## 📄 Documentation Links
- [React Architecture Spec](../REACT_ARCHITECTURE_SPEC.md)
- [Color System Guide](../docs/COLOR_SYSTEM_USER_GUIDE.md)
