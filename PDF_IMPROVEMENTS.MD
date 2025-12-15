
# PDF Export Improvements

## Current Status
- **Functionality**: The PDF export logic is implemented using `WeasyPrint` and `Jinja2` templates.
- **Testing**: A new E2E test `backend/tests/e2e/test_pdf_export.py` verifies the HTML generation, layout structure, and formatting.
- **Issues**: Automatic tests confirm `WeasyPrint` requires system dependencies (`pango`, `cairo`, `gobject`, `libffi`) which are missing in some environments (like macOS without brew).

## Critical Fixes
1.  **System Dependencies**: 
    - The application crashes if `WeasyPrint` is imported but system libraries are missing.
    - **Fix**: Wrap imports in `try/except OSError` blocks, not just `ImportError`.
    - **Action**: Update `backend/main.py` to handle `OSError` gracefully and disable PDF features if libraries are missing.

2.  **Docker Support**:
    - Ensure the `Dockerfile` includes `weasyprint` dependencies.
    - Add: `RUN apt-get update && apt-get install -y build-essential python3-dev python3-pip python3-setuptools python3-wheel python3-cffi libcairo2 libpango-1.0-0 libpangocairo-1.0-0 libgdk-pixbuf2.0-0 libffi-dev shared-mime-info`

## Design & "Wow" Factor Improvements
The current design is clean but basic. To reach "Premium/4K" standards:

### 1. Visual Aesthetics
- **Fonts**: Move away from standard `Helvetica/Arial`. Embed branded fonts (e.g., *Inter*, *Outfit*) using `@font-face` in CSS.
- **Cover Page**: 
    - Use a high-quality property image as a background with an overlay (if available).
    - Add a sleek, modern geometric pattern or gradient background if no image is available.
- **Header/Footer**:
    - **Header**: Add a subtle colored bar or logo transparency on every page.
    - **Footer**: Include "Property Address" and "Generated on [Date]" alongside page numbers.

### 2. Layout & Structure
- **Table of Contents**: Insert a TOC on Page 2 using CSS `target-counter` or simple link generation.
- **Grid System**: The "Modern Dashboard" layout works, but ensure it degrades gracefully on A4 portrait width (approx 700px usable width). 
- **Icons**: Use SVG icons or FontAwesome (converted to images) for "Bedrooms", "Energy Label", etc., instead of text labels.

### 3. Data Visualization
- **Charts**: PDF cannot run JavaScript charts (Chart.js/Recharts). 
- **Solution**: Use a Python library (matplotlib / seaborn) to generate static chart PNGs during the `generate_chapters` or `render_pdf` phase and embed them.
- **Trends**: Visualize "Price Comparison" and "History" with sparklines or bar charts.

## Code Recommendations

### Error Handling in `main.py`
```python
try:
    from weasyprint import HTML
    WEASYPRINT_AVAILABLE = True
except (ImportError, OSError): 
    # Catch OSError for missing system libraries (dlopen failures)
    WEASYPRINT_AVAILABLE = False
```

### Enhanced CSS (`report_pdf.html`)
```css
@page {
    @top-right {
        content: "AI Woning Rapport";
        font-size: 9pt;
        color: #94a3b8;
    }
}
```
