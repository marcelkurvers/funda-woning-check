"""
Test suite for the new variable display strategy implementation.

Tests:
1. PropertyCoreData model creation and preference matching
2. Chapter variable filtering
3. Preference indicator generation
4. AI prompt generation per chapter
"""

import pytest
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from domain.property_core import PropertyCoreData
from domain.chapter_variables import (
    get_chapter_variables,
    should_show_core_data,
    filter_variables_for_chapter,
    get_chapter_ai_prompt,
    CHAPTER_0_VARIABLES,
    CHAPTER_2_VARIABLES
)


class TestPropertyCoreData:
    """Test PropertyCoreData model"""
    
    def test_property_core_creation(self):
        """Test creating PropertyCoreData from context"""
        ctx = {
            'adres': 'Teststraat 123',
            'prijs': '€ 450.000',
            'oppervlakte': '120 m²',
            'perceel': '250 m²',
            'bouwjaar': '1985',
            'label': 'C'
        }
        
        preferences = {
            'marcel': {'priorities': [], 'hidden_priorities': []},
            'petra': {'priorities': [], 'hidden_priorities': []}
        }
        
        property_core = PropertyCoreData.from_context(ctx, preferences)
        
        assert property_core.address == 'Teststraat 123'
        assert property_core.asking_price_eur == 450000
        assert property_core.living_area_m2 == 120
        assert property_core.plot_area_m2 == 250
        assert property_core.build_year == 1985
        assert property_core.energy_label == 'C'
    
    def test_preference_matching_marcel(self):
        """Test Marcel's preference matching"""
        ctx = {
            'adres': 'Teststraat 123',
            'prijs': '€ 450.000',
            'oppervlakte': '120 m²',
            'description': 'Moderne woning met glasvezel en zonnepanelen',
            'features': ['glasvezel', 'zonnepanelen']
        }
        
        preferences = {
            'marcel': {
                'priorities': ['glasvezel', 'zonnepanelen', 'garage'],
                'hidden_priorities': []
            },
            'petra': {
                'priorities': [],
                'hidden_priorities': []
            }
        }
        
        property_core = PropertyCoreData.from_context(ctx, preferences)
        
        assert property_core.marcel_match_score > 0
        assert 'glasvezel' in property_core.marcel_matches
        assert 'zonnepanelen' in property_core.marcel_matches
        assert 'garage' in property_core.marcel_misses
    
    def test_preference_matching_petra(self):
        """Test Petra's preference matching"""
        ctx = {
            'adres': 'Teststraat 123',
            'prijs': '€ 450.000',
            'oppervlakte': '120 m²',
            'description': 'Karakteristieke woning met prachtige tuin en veel licht',
            'features': ['tuin', 'licht']
        }
        
        preferences = {
            'marcel': {
                'priorities': [],
                'hidden_priorities': []
            },
            'petra': {
                'priorities': ['tuin', 'licht', 'sfeer'],
                'hidden_priorities': []
            }
        }
        
        property_core = PropertyCoreData.from_context(ctx, preferences)
        
        assert property_core.petra_match_score > 0
        assert 'tuin' in property_core.petra_matches
        assert 'licht' in property_core.petra_matches
        assert 'sfeer' in property_core.petra_misses
    
    def test_combined_match_score(self):
        """Test combined match score calculation"""
        ctx = {
            'adres': 'Teststraat 123',
            'prijs': '€ 450.000',
            'oppervlakte': '120 m²',
            'description': 'Woning met glasvezel en tuin',
            'features': ['glasvezel', 'tuin']
        }
        
        preferences = {
            'marcel': {
                'priorities': ['glasvezel'],
                'hidden_priorities': []
            },
            'petra': {
                'priorities': ['tuin'],
                'hidden_priorities': []
            }
        }
        
        property_core = PropertyCoreData.from_context(ctx, preferences)
        
        # Both should have 100% match
        assert property_core.marcel_match_score == 100.0
        assert property_core.petra_match_score == 100.0
        assert property_core.combined_match_score == 100.0
    
    def test_preference_indicator_generation(self):
        """Test preference indicator generation for variables"""
        ctx = {
            'adres': 'Teststraat 123',
            'prijs': '€ 450.000',
            'oppervlakte': '120 m²',
            'description': 'Woning met warmtepomp',
            'features': ['warmtepomp']
        }
        
        preferences = {
            'marcel': {
                'priorities': ['warmtepomp'],
                'hidden_priorities': []
            },
            'petra': {
                'priorities': [],
                'hidden_priorities': []
            }
        }
        
        property_core = PropertyCoreData.from_context(ctx, preferences)
        indicator = property_core.get_preference_indicator('heating')
        
        assert indicator['marcel_relevant'] == True
        assert indicator['marcel_match'] == True
        assert 'Marcel' in indicator['interpretation']


class TestChapterVariableStrategy:
    """Test chapter variable filtering strategy"""
    
    def test_chapter_0_shows_core_data(self):
        """Test that Chapter 0 is configured to show core data"""
        assert should_show_core_data(0) == True
        assert len(get_chapter_variables(0)) > 0
        assert 'address' in get_chapter_variables(0)
        assert 'asking_price_eur' in get_chapter_variables(0)
    
    def test_other_chapters_hide_core_data(self):
        """Test that other chapters don't show core data"""
        for chapter_id in range(1, 13):
            assert should_show_core_data(chapter_id) == False
            chapter_vars = get_chapter_variables(chapter_id)
            # Core data should NOT be in other chapters
            assert 'address' not in chapter_vars
            assert 'asking_price_eur' not in chapter_vars
    
    def test_chapter_2_preference_variables(self):
        """Test that Chapter 2 has preference-specific variables"""
        ch2_vars = get_chapter_variables(2)
        
        assert 'marcel_match_percentage' in ch2_vars
        assert 'petra_match_percentage' in ch2_vars
        assert 'combined_match_score' in ch2_vars
        assert 'bezichtiging_focus' in ch2_vars
    
    def test_variable_filtering(self):
        """Test variable filtering for chapters"""
        all_variables = {
            'address': {'value': 'Test', 'status': 'fact'},
            'asking_price_eur': {'value': 450000, 'status': 'fact'},
            'marcel_match_percentage': {'value': 75, 'status': 'inferred'},
            'energy_index_score': {'value': 85, 'status': 'fact'}
        }
        
        # Chapter 0 should show core data
        ch0_filtered = filter_variables_for_chapter(0, all_variables)
        assert 'address' in ch0_filtered
        assert 'asking_price_eur' in ch0_filtered
        
        # Chapter 2 should NOT show core data
        ch2_filtered = filter_variables_for_chapter(2, all_variables)
        assert 'address' not in ch2_filtered
        assert 'asking_price_eur' not in ch2_filtered
        assert 'marcel_match_percentage' in ch2_filtered
    
    def test_ai_prompt_generation(self):
        """Test AI prompt generation for chapters"""
        ch0_prompt = get_chapter_ai_prompt(0)
        # Check for semantic content (Executive Summary focus)
        assert 'Executive Summary' in ch0_prompt or 'executive' in ch0_prompt.lower()
        assert 'Marcel' in ch0_prompt or 'Petra' in ch0_prompt
        
        ch2_prompt = get_chapter_ai_prompt(2)
        assert 'Marcel' in ch2_prompt
        assert 'Petra' in ch2_prompt
        assert 'preference' in ch2_prompt.lower()
    
    def test_no_variable_overlap(self):
        """Test that chapter variables don't overlap (except Chapter 0)"""
        ch1_vars = get_chapter_variables(1)
        ch2_vars = get_chapter_variables(2)
        ch3_vars = get_chapter_variables(3)
        
        # No overlap between chapters 1, 2, 3
        assert len(ch1_vars & ch2_vars) == 0
        assert len(ch2_vars & ch3_vars) == 0
        assert len(ch1_vars & ch3_vars) == 0


class TestIntegration:
    """Integration tests for the complete flow"""
    
    def test_complete_flow(self):
        """Test complete flow from context to filtered variables"""
        ctx = {
            'adres': 'Teststraat 123',
            'prijs': '€ 450.000',
            'oppervlakte': '120 m²',
            'label': 'A++',
            'description': 'Woning met glasvezel, warmtepomp en tuin',
            'features': ['glasvezel', 'warmtepomp', 'tuin']
        }
        
        preferences = {
            'marcel': {
                'priorities': ['glasvezel', 'warmtepomp'],
                'hidden_priorities': []
            },
            'petra': {
                'priorities': ['tuin', 'licht'],
                'hidden_priorities': []
            }
        }
        
        # Create PropertyCoreData
        property_core = PropertyCoreData.from_context(ctx, preferences)
        
        # Verify preference matching worked
        assert property_core.marcel_match_score == 100.0  # 2/2
        assert property_core.petra_match_score == 50.0    # 1/2
        
        # Verify Chapter 0 gets all core data
        assert should_show_core_data(0) == True
        ch0_vars = get_chapter_variables(0)
        assert 'address' in ch0_vars
        assert 'energy_label' in ch0_vars
        
        # Verify Chapter 2 gets only preference data
        assert should_show_core_data(2) == False
        ch2_vars = get_chapter_variables(2)
        assert 'marcel_match_percentage' in ch2_vars
        assert 'address' not in ch2_vars


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
