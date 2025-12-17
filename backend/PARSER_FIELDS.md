# Parser Field Mapping and Quality Check

## Overview
This document describes the enhanced parser fields, validation rules, and how they should be used throughout the application.

## Parsed Fields

### Core Fields (Always Extracted)
| Field Name | Description | Example | Validation |
|------------|-------------|---------|------------|
| `asking_price_eur` | Asking price | "€ 1.400.000" | - |
| `asking_price_per_m2` | Price per square meter | "€ 3.091" | - |
| `address` | Property address | "Haakakker 7" | - |
| `living_area_m2` | Living area | "453 m²" | 10-2000 m² |
| `plot_area_m2` | Plot/land area | "1.016 m²" | - |
| `build_year` | Construction year | "1979" | 1500-2030 |
| `energy_label` | Energy efficiency label | "B" | - |

### Room Information
| Field Name | Description | Example | Validation |
|------------|-------------|---------|------------|
| `rooms` | Total rooms (raw) | "13 kamers (6 slaapkamers)" | Max 30 |
| `bedrooms` | Number of bedrooms | "6" | Max 15 |
| `bathrooms` | Number of bathrooms | "2" | Max 10 |

### Property Details
| Field Name | Description | Example |
|------------|-------------|---------|
| `property_type` | Type of property | "Villa, vrijstaande woning" |
| `construction_type` | New/existing construction | "Bestaande bouw" |
| `garage` | Garage information | "Niet aanwezig, wel mogelijk" |
| `garden` | Garden information | "Achtertuin, voortuin, zijtuin en zonneterras" |
| `balcony` | Balcony/terrace info | "aanwezig" |
| `roof_type` | Type of roof | "Samengesteld dak bedekt met..." |
| `heating` | Heating system | "Cv-ketel, gashaard..." |
| `insulation` | Insulation details | "Dakisolatie, muurisolatie en vloerisolatie" |

### Quality Metadata
| Field Name | Description | Example |
|------------|-------------|---------|
| `_parsing_warnings` | List of validation warnings | ["Suspicious bedroom count: 33..."] |

## Validation Rules

### Bedroom Validation
- **Maximum**: 15 bedrooms
- **Minimum**: 0 bedrooms (but flagged as suspicious)
- **Cross-check**: Must be ≤ total rooms
- **Auto-cap**: Values > 15 are capped to 15 with warning

### Bathroom Validation
- **Maximum**: 10 bathrooms
- **Auto-cap**: Values > 10 are capped to 10 with warning

### Living Area Validation
- **Minimum**: 10 m²
- **Maximum**: 2000 m²
- **Warning**: Values outside range are flagged

### Build Year Validation
- **Minimum**: 1500
- **Maximum**: 2030
- **Warning**: Values outside range are flagged

### Total Rooms Validation
- **Maximum**: 30 rooms
- **Warning**: Values > 30 are flagged

## Field Name Migration

### Old → New Field Names
For backward compatibility, chapters should support both old and new field names:

| Old Field Name | New Field Name | Notes |
|----------------|----------------|-------|
| `prijs` | `asking_price_eur` | Keep both |
| `adres` | `address` | Keep both |
| `oppervlakte` | `living_area_m2` | Keep both |
| `perceel` | `plot_area_m2` | Keep both |
| `bouwjaar` | `build_year` | Keep both |
| `label` | `energy_label` | Keep both |
| N/A | `bedrooms` | NEW - separate from rooms |
| N/A | `bathrooms` | NEW |
| N/A | `property_type` | NEW |
| N/A | `construction_type` | NEW |
| N/A | `garage` | NEW |
| N/A | `garden` | NEW |
| N/A | `balcony` | NEW |
| N/A | `roof_type` | NEW |
| N/A | `heating` | NEW |
| N/A | `insulation` | NEW |

## Usage in Chapters

### Accessing Parsed Data
```python
# Preferred: Use new field names with fallback
bedrooms = ctx.get('bedrooms') or self._extract_from_rooms(ctx.get('rooms'))
bathrooms = ctx.get('bathrooms', '?')
property_type = ctx.get('property_type', 'Woonhuis')

# Backward compatible
living_area = IntelligenceEngine._parse_int(
    ctx.get('living_area_m2') or ctx.get('oppervlakte', '0')
)
```

### Checking for Quality Warnings
```python
# Check if data has quality issues
warnings = ctx.get('_parsing_warnings', [])
if warnings:
    # Display warning to user or log
    logger.warning(f"Data quality issues: {warnings}")
```

## Quality Check Integration

### When to Show Warnings
1. **In Chapter 0 (Executive Summary)**: Display data quality overview
2. **In Relevant Chapters**: Show specific warnings (e.g., bedroom count in Chapter 1)
3. **In PDF Reports**: Include data quality disclaimer if warnings exist

### Example Quality Card
```python
if ctx.get('_parsing_warnings'):
    quality_card = {
        "type": "warning_card",
        "title": "Data Kwaliteit",
        "content": "Sommige gegevens lijken ongebruikelijk en zijn mogelijk onjuist geïnterpreteerd.",
        "warnings": ctx['_parsing_warnings']
    }
```

## Testing

### Test Coverage
- ✅ Basic field extraction
- ✅ Illogical data detection (33 bedrooms)
- ✅ Cross-validation (bedrooms vs rooms)
- ✅ Data capping and warnings
- ✅ Real fixture parsing
- ✅ Quality report generation

### Running Tests
```bash
cd backend
python3 -m pytest tests/unit/test_parser.py -v
```

### Expected Results
- All 7 tests should pass
- Quality report should show 100% completeness for complete listings
- Illogical data should be flagged and capped

## Future Improvements

1. **Additional Fields**:
   - Parking spaces
   - Storage area
   - Outdoor space details
   - Amenities (pool, sauna, etc.)

2. **Enhanced Validation**:
   - Price reasonableness check (price per m² vs market)
   - Energy label vs build year consistency
   - Plot area vs living area ratio

3. **Machine Learning**:
   - Learn from user corrections
   - Improve extraction accuracy over time
   - Detect anomalies based on historical data

## Changelog

### 2025-12-17
- ✅ Added 11 new fields (bedrooms, bathrooms, property_type, etc.)
- ✅ Implemented validation with thresholds
- ✅ Added automatic capping for illogical values
- ✅ Created comprehensive test suite
- ✅ Added quality warnings system
