
I have fixed the "Incorrect/Zero Data" issue.

### The Fix
The issue was indeed the **parsing logic**. 
-   **Old Logic**: It was trying to strip non-digits blindly. For "453 m²", it was grabbing the "2" from "m²", turning "453" into "4532", which skewed the math. For formatted prices, it was fragile.
-   **New Logic**: I implemented **Robust Regex Parsing**:
    -   `Price`: Explicitly removes non-digit characters (except dots/commas handling) to get the clean integer.
    -   `Size`: Uses a regex to find the **first contiguous group of digits** (i.e., "453") and strictly ignores the "m²" suffix.

### Visual Improvements
-   **Investment**: Instead of showing "€ 0" (which looks like a bug), valid renovations now show the cost, while "Marktconform" properties explicitly say **"Geen direct"** (No direct investment needed).

### Instructions
1.  **Refresh your browser**.
2.  **Start a "Nieuwe Analyse"**.
3.  You will now see:
    -   Correct **Price per m²** (e.g., ~€3.088).
    -   Correct **Valuation Logic** (Premium/Market Conform).
    -   Clean **Investment** display.
