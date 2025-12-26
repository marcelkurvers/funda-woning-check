# TEST_REGIME: STRUCTURAL
# REQUIRES: None (mocked PDF generation)
"""
PDF Export Tests - Four-Plane Contract Validation

This test suite validates that the PDF export correctly renders
all Four Planes and maintains parity with the UI output.

CONTRACT REQUIREMENTS:
- plane_structure MUST be True for chapters 1-12
- Plane A2 MUST be visible or explicitly OPERATIONALLY_LIMITED
- Plane D MUST show 5 positives + 5 concerns per persona (no truncation)
- Plane C MUST show KPI uncertainty status
- No silent degradation
"""

import sys
import os
import unittest
import json
import uuid
from unittest.mock import patch, MagicMock


# Add backend to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from fastapi.testclient import TestClient

# Mock WeasyPrint BEFORE importing main to avoid OSError due to missing system libs (pango/cairo)
# This allows us to test the Application Logic (HTML generation, Formatting) without needing the physical PDF engine working.
sys.modules["weasyprint"] = MagicMock()
sys.modules["weasyprint.HTML"] = MagicMock()

import main


class TestPDFExport(unittest.TestCase):
    def setUp(self):
        self.test_db_path = f"test_{uuid.uuid4()}.db"
        # Patch the DB_PATH in main module
        self.db_patcher = patch("main.DB_PATH", self.test_db_path)
        self.db_patcher.start()
        
        # Initialize the DB
        main.init_db()
        
        # Force WeasyPrint available to True for testing logic
        main.WEASYPRINT_AVAILABLE = True
        if not hasattr(main, "HTML"):
            main.HTML = MagicMock()
        
        self.client = TestClient(main.app)

    def tearDown(self):
        self.db_patcher.stop()
        if os.path.exists(self.test_db_path):
            os.remove(self.test_db_path)

    def _create_four_plane_chapters(self):
        """Create chapters with FULL Four-Plane structure."""
        chapters = {}
        
        # Chapter 0 - Executive Summary (may be legacy)
        chapters["0"] = {
            "id": "0",
            "title": "Executive Dashboard",
            "plane_structure": False,  # Chapter 0 can be legacy
            "chapter_data": {
                "intro": "Executive summary introduction.",
                "main_analysis": "Detailed analysis content here. " * 50
            }
        }
        
        # Chapters 1-12 - MUST have Four-Plane structure
        for i in range(1, 13):
            chapters[str(i)] = {
                "id": str(i),
                "title": f"Hoofdstuk {i} - Test Title",
                "plane_structure": True,  # MANDATORY for chapters 1-12
                
                # PLANE A - Visual Intelligence
                "plane_a": {
                    "plane": "A",
                    "plane_name": "visual_intelligence",
                    "charts": [
                        {
                            "chart_type": "bar",
                            "title": f"Test Chart {i}",
                            "data": [
                                {"label": "Metric A", "value": 75, "unit": "%"},
                                {"label": "Metric B", "value": 60, "unit": "%"},
                            ],
                            "max_value": 100,
                            "show_legend": True
                        }
                    ],
                    "data_source_ids": ["asking_price_eur", "living_area_m2"],
                    "not_applicable": False,
                    "not_applicable_reason": None
                },
                
                # PLANE A2 - Synthesized Visual Intelligence
                "plane_a2": {
                    "plane": "A2",
                    "plane_name": "synth_visual_intelligence",
                    "hero_infographic": {
                        "title": f"Hero Infographic {i}",
                        "visual_type": "infographic",
                        "prompt": "Test prompt for infographic",
                        "data_used": ["asking_price_eur"],
                        "insight_summary": "Key insight from this visualization.",
                        "uncertainties": [],
                        "image_uri": None,
                        "image_base64": None,
                        "generation_status": "pending",
                        "generation_error": None
                    },
                    "concepts": [
                        {
                            "title": f"Concept A - Chapter {i}",
                            "visual_type": "diagram",
                            "data_used": ["living_area_m2"],
                            "insight_explained": "This concept visualizes the relationship between space and value.",
                            "uncertainty_notes": None
                        },
                        {
                            "title": f"Concept B - Chapter {i}",
                            "visual_type": "infographic",
                            "data_used": ["build_year"],
                            "insight_explained": "Historical context and condition assessment.",
                            "uncertainty_notes": "Data from listing may be approximate."
                        }
                    ],
                    "data_source_ids": ["asking_price_eur", "living_area_m2", "build_year"],
                    "not_applicable": False,
                    "not_applicable_reason": None
                },
                
                # PLANE B - Narrative Reasoning
                "plane_b": {
                    "plane": "B",
                    "plane_name": "narrative_reasoning",
                    "narrative_text": (
                        "This is the detailed narrative analysis for this chapter. " * 50 +
                        "It provides context and interpretation of the data. " * 20 +
                        "The narrative explains the significance of findings. " * 15
                    ),
                    "word_count": 350,  # Above 300 word minimum
                    "not_applicable": False,
                    "not_applicable_reason": None,
                    "ai_generated": True,
                    "ai_provider": "test",
                    "ai_model": "test-model"
                },
                
                # PLANE C - Factual Anchor
                "plane_c": {
                    "plane": "C",
                    "plane_name": "factual_anchor",
                    "kpis": [
                        {"key": "asking_price_eur", "label": "Vraagprijs", "value": "€ 450.000", "unit": None, "provenance": "fact", "registry_id": "asking_price_eur", "completeness": True, "missing_reason": None},
                        {"key": "living_area_m2", "label": "Woonoppervlak", "value": "120", "unit": "m²", "provenance": "fact", "registry_id": "living_area_m2", "completeness": True, "missing_reason": None},
                        {"key": "build_year", "label": "Bouwjaar", "value": "1985", "unit": None, "provenance": "fact", "registry_id": "build_year", "completeness": True, "missing_reason": None},
                        {"key": "energy_label", "label": "Energielabel", "value": "C", "unit": None, "provenance": "inferred", "registry_id": "energy_label", "completeness": True, "missing_reason": None},
                        {"key": "plot_area", "label": "Perceeloppervlak", "value": None, "unit": "m²", "provenance": "unknown", "registry_id": None, "completeness": False, "missing_reason": "Niet vermeld in listing"},
                    ],
                    "parameters": {"source": "funda", "extracted_at": "2024-01-01"},
                    "data_sources": ["funda", "registry", "kadaster"],
                    "missing_data": ["VvE bijdrage", "Servicekosten"],
                    "uncertainties": ["Energielabel is geschat", "Bouwjaar niet geverifieerd"],
                    "not_applicable": False,
                    "not_applicable_reason": None
                },
                
                # PLANE D - Human Preference
                "plane_d": {
                    "plane": "D",
                    "plane_name": "human_preference",
                    "marcel": {
                        "match_score": 78.5,
                        "mood": "positive",
                        "key_values": [
                            "Goede technische staat van de woning",
                            "Moderne CV-installatie aanwezig",
                            "Stevige constructie en funderingskwaliteit",
                            "Potentieel voor smart home integratie",
                            "Gunstige prijs per vierkante meter"
                        ],
                        "concerns": [
                            "Energielabel kan verbeterd worden",
                            "Dakbedekking nadert onderhoudscyclus",
                            "Elektrische installatie niet gecontroleerd",
                            "Warmtepomp zou efficiënter zijn",
                            "Beperkte uitbreidingsmogelijkheden"
                        ],
                        "summary": "Marcel ziet deze woning als een solide technische investering met goede basis maar verbeterpotentieel in duurzaamheid."
                    },
                    "petra": {
                        "match_score": 82.0,
                        "mood": "positive",
                        "key_values": [
                            "Lichte en ruime woonkamer met goede daglichttoetreding",
                            "Prettige doorkijk en ruimtelijke flow",
                            "Moderne keuken met voldoende werkruimte",
                            "Rustige slaapkamers aan de achterzijde",
                            "Sfeervolle tuin met privacy"
                        ],
                        "concerns": [
                            "Badkamer is wat gedateerd qua stijl",
                            "Gang is enigszins donker",
                            "Bergruimte zou beter georganiseerd kunnen",
                            "Vloerbedekking past niet bij moderne interieurstijl",
                            "Keuken-woonkamerverbinding kan opener"
                        ],
                        "summary": "Petra ervaart dit als een prettige woning met goede sfeer, maar ziet cosmetische aanpassingen als wenselijk."
                    },
                    "comparisons": [
                        {
                            "aspect": "Prijs",
                            "marcel_view": "Goede investering gezien technische staat",
                            "petra_view": "Betaalbaar maar renovatiebudget nodig",
                            "alignment": "aligned",
                            "requires_discussion": False
                        }
                    ],
                    "overlap_points": [
                        "Beiden positief over de locatie",
                        "Eens over de potentie van de tuin",
                        "Gezamenlijke voorkeur voor moderne keuken"
                    ],
                    "tension_points": [
                        "Marcel prioriteert techniek, Petra prioriteert sfeer",
                        "Verschil in urgentie voor badkamerrenovatie"
                    ],
                    "joint_synthesis": "Marcel en Petra zien beiden potentieel in deze woning, met complementaire aandachtspunten.",
                    "not_applicable": False,
                    "not_applicable_reason": None
                }
            }
        
        return chapters

    def test_pdf_export_basic_functionality(self):
        """Test basic PDF export returns 200 and valid PDF."""
        run_id = str(uuid.uuid4())
        chapters = self._create_four_plane_chapters()
        
        core = {
            "address": "Teststraat 123, 1234 AB Teststad",
            "asking_price_eur": "€ 450.000",
            "living_area_m2": 120,
            "build_year": 1985,
            "energy_label": "C"
        }
        
        # Insert into DB (without core_summary_json which may not exist in all setups)
        con = main.db()
        cur = con.cursor()
        cur.execute(
            """INSERT INTO runs (id, funda_url, funda_html, status, steps_json, 
               property_core_json, chapters_json, kpis_json, sources_json, 
               unknowns_json, artifacts_json, created_at, updated_at) 
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                run_id, 
                "http://test.url", 
                None, 
                "done", 
                json.dumps(main.default_steps()), 
                json.dumps(core), 
                json.dumps(chapters), 
                "{}", "[]", "[]", "{}", 
                main.now(), main.now()
            )
        )
        con.commit()
        con.close()

        # Setup WeasyPrint mock
        captured_html = []
        mock_html_instance = MagicMock()
        mock_html_instance.write_pdf.return_value = b"%PDF-1.4 Mock PDF Content"
        
        def side_effect_HTML(string=None, **kwargs):
            if string:
                captured_html.append(string)
            return mock_html_instance

        with patch("main.HTML", side_effect=side_effect_HTML):
            response = self.client.get(f"/api/runs/{run_id}/pdf")

        # Validate response
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers["content-type"], "application/pdf")
        self.assertTrue(response.content.startswith(b"%PDF"))
        self.assertTrue(len(captured_html) > 0, "HTML was not passed to WeasyPrint")

    def test_pdf_four_plane_structure_rendered(self):
        """Test that PDF correctly renders Four-Plane structure elements."""
        run_id = str(uuid.uuid4())
        chapters = self._create_four_plane_chapters()
        
        core = {
            "address": "Teststraat 123, 1234 AB Teststad",
            "asking_price_eur": "€ 450.000",
            "living_area_m2": 120
        }

        # Insert into DB
        con = main.db()
        cur = con.cursor()
        cur.execute(
            """INSERT INTO runs (id, funda_url, funda_html, status, steps_json, 
               property_core_json, chapters_json, kpis_json, sources_json, 
               unknowns_json, artifacts_json, created_at, updated_at) 
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                run_id, "http://test.url", None, "done", 
                json.dumps(main.default_steps()), 
                json.dumps(core), json.dumps(chapters), 
                "{}", "[]", "[]", "{}", 
                main.now(), main.now()
            )
        )
        con.commit()
        con.close()

        captured_html = []
        mock_html_instance = MagicMock()
        mock_html_instance.write_pdf.return_value = b"%PDF-1.4 Mock"
        
        def side_effect_HTML(string=None, **kwargs):
            if string:
                captured_html.append(string)
            return mock_html_instance

        with patch("main.HTML", side_effect=side_effect_HTML):
            response = self.client.get(f"/api/runs/{run_id}/pdf")

        self.assertEqual(response.status_code, 200)
        html = captured_html[0]

        # CHECK 1: Four-Plane grid layout exists
        self.assertIn('class="four-plane-grid"', html, "Four-Plane grid layout not found")

        # CHECK 2: All plane badges present
        self.assertIn('class="plane-badge plane-badge-a"', html, "Plane A badge not found")
        self.assertIn('class="plane-badge plane-badge-a2"', html, "Plane A2 badge not found")
        self.assertIn('class="plane-badge plane-badge-b"', html, "Plane B badge not found")
        self.assertIn('class="plane-badge plane-badge-c"', html, "Plane C badge not found")
        self.assertIn('class="plane-badge plane-badge-d"', html, "Plane D badge not found")

        # CHECK 3: Cover page exists
        self.assertIn('class="page cover-page"', html, "Cover page not found")
        self.assertIn("Teststraat 123", html, "Address not on cover")

        # CHECK 4: Branding present
        self.assertIn("KURVERS PROPERTY CONSULTING", html, "Branding not found")

    def test_pdf_plane_a2_always_visible(self):
        """Test that Plane A2 is always visible or explicitly limited."""
        run_id = str(uuid.uuid4())
        chapters = self._create_four_plane_chapters()
        
        core = {"address": "Test 1, Teststad"}

        con = main.db()
        cur = con.cursor()
        cur.execute(
            """INSERT INTO runs (id, funda_url, funda_html, status, steps_json, 
               property_core_json, chapters_json, kpis_json, sources_json, 
               unknowns_json, artifacts_json, created_at, updated_at) 
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (run_id, "http://test.url", None, "done", 
             json.dumps(main.default_steps()), 
             json.dumps(core), json.dumps(chapters), 
             "{}", "[]", "[]", "{}", main.now(), main.now())
        )
        con.commit()
        con.close()

        captured_html = []
        mock_html_instance = MagicMock()
        mock_html_instance.write_pdf.return_value = b"%PDF-1.4"
        
        def side_effect_HTML(string=None, **kwargs):
            if string:
                captured_html.append(string)
            return mock_html_instance

        with patch("main.HTML", side_effect=side_effect_HTML):
            response = self.client.get(f"/api/runs/{run_id}/pdf")

        html = captured_html[0]
        
        # A2 must have concepts or hero infographic rendered
        self.assertIn("Synthesized Intelligence", html, "Plane A2 header not found")
        self.assertIn("concept-item", html, "Plane A2 concepts not found")

    def test_pdf_plane_d_full_persona(self):
        """Test that Plane D shows full persona analysis without truncation."""
        run_id = str(uuid.uuid4())
        chapters = self._create_four_plane_chapters()
        
        core = {"address": "Test 1, Teststad"}

        con = main.db()
        cur = con.cursor()
        cur.execute(
            """INSERT INTO runs (id, funda_url, funda_html, status, steps_json, 
               property_core_json, chapters_json, kpis_json, sources_json, 
               unknowns_json, artifacts_json, created_at, updated_at) 
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (run_id, "http://test.url", None, "done", 
             json.dumps(main.default_steps()), 
             json.dumps(core), json.dumps(chapters), 
             "{}", "[]", "[]", "{}", main.now(), main.now())
        )
        con.commit()
        con.close()

        captured_html = []
        mock_html_instance = MagicMock()
        mock_html_instance.write_pdf.return_value = b"%PDF-1.4"
        
        def side_effect_HTML(string=None, **kwargs):
            if string:
                captured_html.append(string)
            return mock_html_instance

        with patch("main.HTML", side_effect=side_effect_HTML):
            response = self.client.get(f"/api/runs/{run_id}/pdf")

        html = captured_html[0]
        
        # CHECK: Persona names present
        self.assertIn("Marcel", html, "Marcel persona not found")
        self.assertIn("Petra", html, "Petra persona not found")
        
        # CHECK: Full positives visible (not truncated)
        self.assertIn("Goede technische staat", html, "Marcel positive not fully rendered")
        self.assertIn("Lichte en ruime woonkamer", html, "Petra positive not fully rendered")
        
        # CHECK: Concerns visible
        self.assertIn("Energielabel kan verbeterd", html, "Marcel concern not rendered")
        self.assertIn("Badkamer is wat gedateerd", html, "Petra concern not rendered")
        
        # CHECK: Overlaps and tensions present
        self.assertIn("Overlap", html, "Overlap section not found")
        self.assertIn("Spanning", html, "Tension section not found")

    def test_pdf_plane_c_kpi_status(self):
        """Test that Plane C shows KPI uncertainty status."""
        run_id = str(uuid.uuid4())
        chapters = self._create_four_plane_chapters()
        
        core = {"address": "Test 1, Teststad"}

        con = main.db()
        cur = con.cursor()
        cur.execute(
            """INSERT INTO runs (id, funda_url, funda_html, status, steps_json, 
               property_core_json, chapters_json, kpis_json, sources_json, 
               unknowns_json, artifacts_json, created_at, updated_at) 
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (run_id, "http://test.url", None, "done", 
             json.dumps(main.default_steps()), 
             json.dumps(core), json.dumps(chapters), 
             "{}", "[]", "[]", "{}", main.now(), main.now())
        )
        con.commit()
        con.close()

        captured_html = []
        mock_html_instance = MagicMock()
        mock_html_instance.write_pdf.return_value = b"%PDF-1.4"
        
        def side_effect_HTML(string=None, **kwargs):
            if string:
                captured_html.append(string)
            return mock_html_instance

        with patch("main.HTML", side_effect=side_effect_HTML):
            response = self.client.get(f"/api/runs/{run_id}/pdf")

        html = captured_html[0]
        
        # CHECK: KPI status indicators present
        self.assertIn("kpi-status", html, "KPI status class not found")
        self.assertIn("status-fact", html, "Fact status not found")
        self.assertIn("status-inferred", html, "Inferred status not found")
        self.assertIn("status-unknown", html, "Unknown status not found")
        
        # CHECK: Missing data box present
        self.assertIn("Ontbrekende Data", html, "Missing data section not found")
        self.assertIn("VvE bijdrage", html, "Missing data item not rendered")

    def test_pdf_missing_plane_structure_shows_error(self):
        """Test that chapters missing plane_structure show error page."""
        run_id = str(uuid.uuid4())
        
        # Create chapter WITHOUT plane_structure
        chapters = {
            "1": {
                "id": "1",
                "title": "Broken Chapter",
                "plane_structure": False,  # MISSING - should trigger error
                "grid_layout": {"main": {"content": "Legacy content"}}
            }
        }
        
        core = {"address": "Test"}

        con = main.db()
        cur = con.cursor()
        cur.execute(
            """INSERT INTO runs (id, funda_url, funda_html, status, steps_json, 
               property_core_json, chapters_json, kpis_json, sources_json, 
               unknowns_json, artifacts_json, created_at, updated_at) 
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (run_id, "http://test.url", None, "done", 
             json.dumps(main.default_steps()), 
             json.dumps(core), json.dumps(chapters), 
             "{}", "[]", "[]", "{}", main.now(), main.now())
        )
        con.commit()
        con.close()

        captured_html = []
        mock_html_instance = MagicMock()
        mock_html_instance.write_pdf.return_value = b"%PDF-1.4"
        
        def side_effect_HTML(string=None, **kwargs):
            if string:
                captured_html.append(string)
            return mock_html_instance

        with patch("main.HTML", side_effect=side_effect_HTML):
            response = self.client.get(f"/api/runs/{run_id}/pdf")

        html = captured_html[0]
        
        # CHECK: Error box should be visible for broken chapter
        self.assertIn("FOUR-PLANE CONTRACT VIOLATION", html, "Contract violation error not shown")
        self.assertIn("plane_structure", html, "plane_structure mentioned in error")


if __name__ == "__main__":
    unittest.main()
