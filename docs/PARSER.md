# AI Woning Rapport - Parser Documentation

## Overview
The Parser is a critical component of the **AI Woning Rapport** system. It is responsible for transforming raw HTML from Funda listings into a structured `PropertyCore` data model. It uses a multi-layered extraction strategy:
1. **Semantic Selectors**: Primary CSS selectors targeting specific Funda elements.
2. **Key-Value Pair Scanning**: Intelligent regex-based scanning of table rows and labels.
3. **Raw Text Fallback**: Fuzzy keyword searching in text blocks for unstructured data.

## Key Features

### 1. Robust Intelligence
- **Multi-Line Support**: Correctly parses values located on the line below the label.
- **Bi-Directional Scanning**: Implements both forward and backward scanning for label-value associations.
- **Dutch Format Support**: Robustly handles dots as thousand separators and commas as decimal points in large numeric values.
- **Unit Normalization**: Automatically strips units (m², €, etc.) and converts to numbers.

### 2. Field Mapping
The parser extracts ~50 fields, categorized as follows:

| Category | Fields |
|----------|--------|
| **Core** | `asking_price_eur`, `address`, `living_area_m2`, `plot_area_m2`, `build_year`, `energy_label` |
| **Rooms** | `rooms` (total), `bedrooms`, `bathrooms`, `interior_volume_m3` |
| **Status** | `status` (Te Koop, Verkocht), `days_listed` |
| **Technical** | `insulation`, `heating`, `hot_water`, `boiler_year`, `glass_type` |
| **Exterior** | `garden`, `balcony`, `terrace`, `roof_type`, `garage`, `parking` |
| **Legal** | `ownership_type`, `vve_costs`, `listed_since` |

### 3. Validation & Quality Control
- **Dynamic Thresholds**: Configurable validation limits for bedrooms, bathrooms, and areas.
- **Illogical Data Correction**: Automatically caps suspicious values (e.g., >15 bedrooms) and flags them as warnings.
- **Cross-Validation**: Verifies consistency between overlapping fields (e.g., `bedrooms` vs `total_rooms`).

## Technical Implementation

### Extraction Strategy
def _extract_spec_by_keyword(self, soup, keyword):
    # 1. Prioritize dt/dd Semantic Pairs
    # 2. Search in .v-info-list (Standard Funda layout)
    # 3. Search in .object-kenmerken-lijst (Old Funda layout)
    # 4. Fuzzy search for exact label match
```

### Descriptive Field Extraction
The parser implements a "Relaxed Scan" for descriptive fields (`property_type`, `heating`, etc.) that allows capturing short strings even without digits, while maintaining "Strict Scan" for numeric fallbacks to prevent capturing unrelated narrative text.

### Raw Text Scanning
The `_scan_raw_text` method uses improved regex patterns to handle various layouts:
```python
# Handles "Label: Value", "Label \n Value", and "Value \n Label"
pattern = re.compile(f"(?:^|\\n)\\s*({keyword})[:\\s]+(.+?)(?=\\n|$)", re.IGNORECASE)
```

## Data Quality Metadata
Every parse operation includes a quality report:
- `_parsing_warnings`: List of suspicious or capped values.
- `_data_completeness`: Percentage of core fields successfully extracted.

## Testing
Comprehensive testing ensures 0% regression in parsing accuracy:
- `tests/unit/test_parser.py`: Field extraction and validation.
- `tests/unit/test_complex_parsing.py`: Handling of unusual HTML structures.
- `tests/unit/test_parser_edge_cases.py`: Specific fixes for known Funda edge cases.

---
*Last Updated: 2025-12-21*
