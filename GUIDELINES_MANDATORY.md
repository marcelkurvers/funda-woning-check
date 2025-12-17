# Mandatory Development & Design Guidelines
**Last Updated:** 2025-12-17
**Status:** ENFORCED

This document outlines the **non-negotiable** standards for development, design, and testing within the `ai-woning-rapport` project. Failure to adhere to these will result in rejected changes.

---

## 1. Development & Testing Standards

### 1.1. Zero Regression Policy
- **Existing tests must pass** before any commit.
- If you modify code, you **must run** the relevant tests.
- If no test exists for the modified code, you **must create one**.

### 1.2. MCP Test Server & Docker Sync
- The **MCP Test Server** is the source of truth for CI/CD status.
- **Docker Sync Check**: The file `backend/tests/integration/test_docker_sync.py` is critical. It ensures the Docker container runs the exact code present in your editor.
    - **Usage**: You must ensure this test passes or is triggered whenever backend code changes to ensure the running container is fresh.

### 1.3. New Feature = New Test
- Any new Python module or class requires a corresponding unit test in `backend/tests/unit/`.
- Any new API endpoint requires an integration test in `backend/tests/integration/` (or addition to `test_integration.py`).

---

## 2. Design & UI Standards

### 2.1. The "Bento Grid" (Raster) Layout
- **Concept**: We do not use scrolling lists or sidebars. We use a **5-column grid** (Raster) layout.
- **Implementation**:
    - Use `<BentoGrid>` from `src/components/layout/BentoLayout.tsx`.
    - Map content to `<BentoCard>` components.
    - **Prioritize** "Above the Fold" content. The layout is dashboard-first.

### 2.2. CSS Framework (Tailwind v3)
- **Engine**: We use **Tailwind CSS v3**.
- **Configuration**:
    - `postcss.config.js`: must use the standard `tailwindcss` plugin key. **DO NOT** use `@tailwindcss/postcss`.
    - `index.css`: Use `@apply` directives permitted in v3.
- **Theme**:
    - Use `slate-50` for backgrounds and `slate-900` for text.
    - Semantic colors: `blue` (Primary/Info), `emerald` (Success/Strengths), `amber` (Warning/Advice).

---

## 3. Workflow Checklist

Before marking a task as "Done":
1. [ ] **Code**: Implemented cleanly following project structure.
2. [ ] **Design**: Checked against Bento Grid guidelines (if UI).
3. [ ] **Test**: Ran `test_docker_sync.py` (if backend) to ensure container matches code.
4. [ ] **Test**: Ran `pytest backend/tests` and confirmed all pass.
