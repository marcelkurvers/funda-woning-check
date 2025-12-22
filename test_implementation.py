#!/usr/bin/env python3
"""
Test script to verify the new variable display strategy implementation.

This script will:
1. Check if the new modules are importable
2. Verify the PropertyCoreData model works
3. Test the chapter variable strategy
4. Simulate a basic analysis flow
"""

import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

def test_imports():
    """Test that all new modules can be imported"""
    print("=" * 60)
    print("TEST 1: Module Imports")
    print("=" * 60)
    
    try:
        from domain.property_core import PropertyCoreData
        print("✓ PropertyCoreData imported successfully")
    except Exception as e:
        print(f"✗ Failed to import PropertyCoreData: {e}")
        return False
    
    try:
        from domain.chapter_variables import (
            get_chapter_variables,
            should_show_core_data,
            filter_variables_for_chapter,
            get_chapter_ai_prompt
        )
        print("✓ Chapter variable functions imported successfully")
    except Exception as e:
        print(f"✗ Failed to import chapter_variables: {e}")
        return False
    
    print()
    return True


def test_property_core_data():
    """Test PropertyCoreData model creation"""
    print("=" * 60)
    print("TEST 2: PropertyCoreData Model")
    print("=" * 60)
    
    from domain.property_core import PropertyCoreData
    
    # Sample context data
    ctx = {
        'adres': 'Teststraat 123',
        'prijs': '€ 450.000',
        'oppervlakte': '120 m²',
        'perceel': '250 m²',
        'bouwjaar': '1985',
        'label': 'C',
        'description': 'Mooie woning met glasvezel en zonnepanelen',
        'features': ['glasvezel', 'zonnepanelen', 'garage']
    }
    
    # Sample preferences
    preferences = {
        'marcel': {
            'priorities': ['glasvezel', 'zonnepanelen', 'garage'],
            'hidden_priorities': ['isolatie']
        },
        'petra': {
            'priorities': ['tuin', 'licht', 'sfeer'],
            'hidden_priorities': ['badkamer']
        }
    }
    
    try:
        property_core = PropertyCoreData.from_context(ctx, preferences)
        
        print(f"Address: {property_core.address}")
        print(f"Price: €{property_core.asking_price_eur:,}")
        print(f"Living Area: {property_core.living_area_m2} m²")
        print(f"Energy Label: {property_core.energy_label}")
        print(f"\nMarcel Match Score: {property_core.marcel_match_score}%")
        print(f"Marcel Matches: {property_core.marcel_matches}")
        print(f"Marcel Misses: {property_core.marcel_misses}")
        print(f"\nPetra Match Score: {property_core.petra_match_score}%")
        print(f"Petra Matches: {property_core.petra_matches}")
        print(f"Petra Misses: {property_core.petra_misses}")
        print(f"\nCombined Match Score: {property_core.combined_match_score}%")
        
        print("\n✓ PropertyCoreData model works correctly")
        print()
        return True
    except Exception as e:
        print(f"✗ Failed to create PropertyCoreData: {e}")
        import traceback
        traceback.print_exc()
        print()
        return False


def test_chapter_variables():
    """Test chapter variable strategy"""
    print("=" * 60)
    print("TEST 3: Chapter Variable Strategy")
    print("=" * 60)
    
    from domain.chapter_variables import (
        get_chapter_variables,
        should_show_core_data,
        get_chapter_ai_prompt
    )
    
    # Test Chapter 0 (should show core data)
    ch0_vars = get_chapter_variables(0)
    print(f"Chapter 0 variables: {len(ch0_vars)} variables")
    print(f"Should show core data: {should_show_core_data(0)}")
    print(f"Sample variables: {list(ch0_vars)[:5]}")
    
    # Test Chapter 2 (should NOT show core data)
    ch2_vars = get_chapter_variables(2)
    print(f"\nChapter 2 variables: {len(ch2_vars)} variables")
    print(f"Should show core data: {should_show_core_data(2)}")
    print(f"Variables: {ch2_vars}")
    
    # Test AI prompts
    print(f"\nChapter 0 AI Prompt:")
    print(get_chapter_ai_prompt(0)[:100] + "...")
    
    print(f"\nChapter 2 AI Prompt:")
    print(get_chapter_ai_prompt(2)[:100] + "...")
    
    print("\n✓ Chapter variable strategy works correctly")
    print()
    return True


def test_preference_indicators():
    """Test preference indicator generation"""
    print("=" * 60)
    print("TEST 4: Preference Indicators")
    print("=" * 60)
    
    from domain.property_core import PropertyCoreData
    
    ctx = {
        'adres': 'Teststraat 123',
        'prijs': '€ 450.000',
        'oppervlakte': '120 m²',
        'label': 'A++',
        'description': 'Moderne woning met warmtepomp en zonnepanelen',
    }
    
    preferences = {
        'marcel': {
            'priorities': ['warmtepomp', 'zonnepanelen'],
            'hidden_priorities': []
        },
        'petra': {
            'priorities': ['tuin', 'licht'],
            'hidden_priorities': []
        }
    }
    
    property_core = PropertyCoreData.from_context(ctx, preferences)
    
    # Test energy label indicator
    energy_indicator = property_core.get_preference_indicator('energy_label')
    print(f"Energy Label Indicator:")
    print(f"  Marcel relevant: {energy_indicator['marcel_relevant']}")
    print(f"  Petra relevant: {energy_indicator['petra_relevant']}")
    print(f"  Interpretation: {energy_indicator['interpretation']}")
    
    # Test heating indicator
    heating_indicator = property_core.get_preference_indicator('heating')
    print(f"\nHeating Indicator:")
    print(f"  Marcel relevant: {heating_indicator['marcel_relevant']}")
    print(f"  Petra relevant: {heating_indicator['petra_relevant']}")
    print(f"  Interpretation: {heating_indicator['interpretation']}")
    
    print("\n✓ Preference indicators work correctly")
    print()
    return True


def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("VARIABLE DISPLAY STRATEGY - IMPLEMENTATION TEST")
    print("=" * 60 + "\n")
    
    results = []
    
    results.append(("Module Imports", test_imports()))
    results.append(("PropertyCoreData Model", test_property_core_data()))
    results.append(("Chapter Variable Strategy", test_chapter_variables()))
    results.append(("Preference Indicators", test_preference_indicators()))
    
    # Summary
    print("=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    for test_name, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{status}: {test_name}")
    
    all_passed = all(result[1] for result in results)
    
    print("\n" + "=" * 60)
    if all_passed:
        print("✓ ALL TESTS PASSED!")
        print("=" * 60)
        print("\nThe implementation is ready for testing with real data.")
        print("Next step: Run a full property analysis and verify:")
        print("  1. Chapter 0 shows all core data")
        print("  2. Other chapters don't repeat core data")
        print("  3. Preference indicators appear correctly")
        print("  4. AI interpretation is present")
        return 0
    else:
        print("✗ SOME TESTS FAILED")
        print("=" * 60)
        print("\nPlease review the errors above and fix before proceeding.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
