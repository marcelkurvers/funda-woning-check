import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))
import pytest
from chapters.chapter_0 import ExecutiveSummary
from enrichment import DataEnricher

class TestChapter0Logic:

    def test_address_cleanup(self):
        """Test that 'Mijn Huis' is not used as a street address."""
        ctx = {
            'asking_price_eur': 450000,
            'living_area_m2': 120,
            'address': 'Mijn Huis',
            'build_year': 2010,
            'energy_label': 'A'
        }
        chapter = ExecutiveSummary(ctx)
        output = chapter.generate()
        
        # Check intro text
        intro = output.chapter_data['intro']
        assert "aan de Mijn Huis" not in intro, "Should replace generic title address"
        assert "aan dit object" in intro or "aan dit adres" in intro or "locatie" in intro or "van dit object" in intro

    def test_robotic_currency(self):
        """Test that € 0 is formatted naturally."""
        ctx = {
            'asking_price_eur': 450000,
            'living_area_m2': 120,
            'address': 'Kalverstraat 1',
            'build_year': 2010,
            'energy_label': 'A' # Implies 0 reno cost in current logic
        }
        chapter = ExecutiveSummary(ctx)
        output = chapter.generate()
        
        # Check metrics for investment display (not main_analysis)
        metrics = output.grid_layout['metrics']
        investment_metric = next((m for m in metrics if m['id'] == 'investment'), None)
        
        assert investment_metric is not None, "Investment metric should exist"
        # Should show "Geen directe investering" for good energy label
        assert "Geen directe investering" in investment_metric['value'] or investment_metric['value'] == "Geen directe investering"

    def test_maintenance_consistency(self):
        """Test that old houses with asbestos risks don't get 'Low' maintenance rating."""
        ctx = {
            'asking_price_eur': 450000,
            'living_area_m2': 120,
            'address': 'Kalverstraat 1',
            'build_year': 1920, # Old house -> Asbestos risk
            'energy_label': 'A' # Good label, but structure is old risk
        }
        ctx = DataEnricher.enrich(ctx)
        chapter = ExecutiveSummary(ctx)
        output = chapter.generate()
        
        metrics = output.grid_layout['metrics']
        maint_metric = next(m for m in metrics if m['id'] == 'maintenance_intensity')
        
        # Should NOT be "Laag" (Low) if there are Asbestos/Roof risks
        assert maint_metric['value'] != "Laag", f"Old house with risks should not have Low maintenance. Got: {maint_metric['value']}"
        assert maint_metric['color'] != "green"
