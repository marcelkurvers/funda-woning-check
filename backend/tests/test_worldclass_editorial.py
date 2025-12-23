import pytest
from chapters.formatter import EditorialEngine
from datetime import datetime

class TestWorldClassEditorial:
    
    @pytest.fixture
    def dummy_data(self):
        return {
            "address": "Prinsengracht 123",
            "price": 1250000,
            "area": 150,
            "label": "A",
            "year": 2015
        }
    
    @pytest.fixture
    def dummy_narrative(self):
        return {
            "main_analysis": "<p>Deze woning is cruciaal voor de toekomst. Het is een technisch hoogstandje.</p><p>De tweede paragraaf gaat over sfeer.</p>",
            "variables": {
                "test_var": {"value": "10", "status": "fact", "reasoning": "Test"}
            }
        }

    def test_chapter_0_quality(self, dummy_data, dummy_narrative):
        """Checks if Chapter 0 has the gauge and world-class markers."""
        html = EditorialEngine.format_narrative(0, dummy_narrative, dummy_data)
        
        # 1. Check Lede (Quote agnostic)
        assert "magazine-lede" in html
        
        # 2. Check Section Marker
        assert "magazine-section-marker" in html
        assert "EXECUTIVE / STRATEGIE" in html
        
        # 3. Check Market Pulse Gauge
        assert "market-pulse-box" in html
        assert "Market Position Index" in html
        
        # 4. Check Byline
        assert "magazine-byline" in html
        assert "Authorized by" in html
        assert datetime.now().strftime("%Y") in html

    def test_pull_quote_extraction(self, dummy_data):
        """Verifies that key sentences are promoted to pull quotes."""
        narrative = {
            "main_analysis": "<p>Start.</p><p>Deze zin is cruciaal voor het begrijpen van de waarde van dit object en moet serieus genomen worden!</p><p>Einde.</p>",
            "variables": {}
        }
        html = EditorialEngine.format_narrative(1, narrative, dummy_data)
        
        assert "magazine-pull-quote" in html
        assert "cruciaal voor het begrijpen" in html

    def test_visual_signposts(self, dummy_data, dummy_narrative):
        """Checks if keywords are highlighted with icons."""
        narrative = {
            "main_analysis": "<p>De technische staat is goed en de sfeer is uitstekend.</p>",
            "variables": {}
        }
        html = EditorialEngine.format_narrative(1, narrative, dummy_data)
        
        assert "data-icon=\"🛠️\"" in html
        assert "data-icon=\"✨\"" in html

    def test_persona_styling(self, dummy_data, dummy_narrative):
        """Checks if Marcel & Petra mentions are stylized."""
        narrative = {
            "main_analysis": "<p>Marcel vindt het technisch goed, Petra houdt van de sfeer.</p>",
            "variables": {}
        }
        html = EditorialEngine.format_narrative(1, narrative, dummy_data)
        
        assert "class=\"persona-mention marcel\">Marcel</span>" in html
        assert "class=\"persona-mention petra\">Petra</span>" in html

    def test_all_chapters_consecutively(self, dummy_data, dummy_narrative):
        """Runs the editorial check for a range of chapters."""
        # Visual markers for each chapter to verify specialized infographics
        chapter_visuals = {
            0: "market-pulse-box",
            1: "grid-cols-3",
            2: "synergy-meter",
            3: "risk-shield",
            4: "energy-ribbon",
            5: "layout-audit",
            6: "maintenance-bar",
            7: "outdoor-card",
            8: "mobility-bento",
            9: "legal-shield",
            10: "financial-card",
            11: "leverage-bar",
            12: "verdict-scoreboard"
        }
        
        for i in range(13):
            html = EditorialEngine.format_narrative(i, dummy_narrative, dummy_data)
            # Every page must have the elite editor's signature and markers
            assert "magazine-section-marker" in html
            assert "magazine-byline" in html
            assert "magazine-lede" in html
            
            # Verify specialized visual for EVERY page
            visual_marker = chapter_visuals.get(i)
            if visual_marker:
                assert visual_marker in html, f"Chapter {i} missing its specialized visual component: {visual_marker}"
