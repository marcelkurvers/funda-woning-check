
import pytest
from backend.chapters.chapter_0 import ExecutiveSummary

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
        
        html = output.chapter_data['main_analysis']
        assert "€ 0" not in html
        assert "Geen directe investering" in html or "minimale investering" in html

    def test_maintenance_consistency(self):
        """Test that old houses with asbestos risks don't get 'Low' maintenance rating."""
        ctx = {
            'asking_price_eur': 450000,
            'living_area_m2': 120,
            'address': 'Kalverstraat 1',
            'build_year': 1920, # Old house -> Asbestos risk
            'energy_label': 'A' # Good label, but structure is old risk
        }
        chapter = ExecutiveSummary(ctx)
        output = chapter.generate()
        
        metrics = output.grid_layout['metrics']
        maint_metric = next(m for m in metrics if m['id'] == 'maintenance_intensity')
        
        # Should NOT be "Laag" (Low) if there are Asbestos/Roof risks
        assert maint_metric['value'] != "Laag", f"Old house with risks should not have Low maintenance. Got: {maint_metric['value']}"
        assert maint_metric['color'] != "green"
