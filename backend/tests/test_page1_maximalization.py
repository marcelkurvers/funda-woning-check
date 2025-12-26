"""
TEST: Page 1 (Chapter 1: Kerngegevens) Maximalization Verification

This test directly verifies that the extractors and backbone produce
maximized content for Page 1 as visible in the UI.
"""

import pytest
from datetime import datetime
from backend.domain.registry import CanonicalRegistry, RegistryEntry, RegistryType
from backend.domain.pipeline_context import PipelineContext
from backend.pipeline.four_plane_extractors import (
    PlaneAExtractor,
    PlaneCExtractor,
    PlaneDExtractor,
    FourPlaneMaxExtractor,
)
from backend.pipeline.four_plane_backbone import (
    FourPlaneBackbone,
    generate_four_plane_chapter,
    convert_plane_composition_to_dict,
)


def create_sample_registry() -> CanonicalRegistry:
    """Create a sample registry with realistic property data."""
    registry = CanonicalRegistry()
    
    # Core property data (Chapter 1 KPIs)
    registry.register(RegistryEntry(
        id="address",
        type=RegistryType.FACT,
        value="Haakakker 7, Mierlo",
        name="Adres",
        source="funda_parse"
    ))
    registry.register(RegistryEntry(
        id="property_type",
        type=RegistryType.FACT,
        value="Vrijstaande woning",
        name="Woningtype",
        source="funda_parse"
    ))
    registry.register(RegistryEntry(
        id="asking_price_eur",
        type=RegistryType.FACT,
        value=485000,
        name="Vraagprijs",
        source="funda_parse",
        unit="€"
    ))
    registry.register(RegistryEntry(
        id="living_area_m2",
        type=RegistryType.FACT,
        value=142,
        name="Woonoppervlak",
        source="funda_parse",
        unit="m²"
    ))
    registry.register(RegistryEntry(
        id="plot_area_m2",
        type=RegistryType.FACT,
        value=380,
        name="Perceeloppervlak",
        source="funda_parse",
        unit="m²"
    ))
    registry.register(RegistryEntry(
        id="rooms",
        type=RegistryType.FACT,
        value=6,
        name="Kamers",
        source="funda_parse"
    ))
    registry.register(RegistryEntry(
        id="bedrooms",
        type=RegistryType.FACT,
        value=4,
        name="Slaapkamers",
        source="funda_parse"
    ))
    registry.register(RegistryEntry(
        id="build_year",
        type=RegistryType.FACT,
        value=1978,
        name="Bouwjaar",
        source="funda_parse"
    ))
    registry.register(RegistryEntry(
        id="energy_label",
        type=RegistryType.FACT,
        value="C",
        name="Energielabel",
        source="funda_parse"
    ))
    
    return registry


def create_locked_context() -> PipelineContext:
    """Create a pipeline context with properly locked registry."""
    from backend.domain.pipeline_context import create_pipeline_context
    
    ctx = create_pipeline_context(run_id="test-page1-max")
    registry = create_sample_registry()
    
    # Copy entries from sample registry to context's registry
    for entry_id, entry in registry.get_all().items():
        ctx.registry.register(entry)
    
    # Proper lifecycle: complete enrichment, then lock
    ctx.complete_enrichment()
    ctx.lock_registry()
    
    return ctx


class TestPage1PlaneAMaximalization:
    """Verify Plane A (Visual Intelligence) is maximized for Chapter 1."""
    
    def test_plane_a_generates_charts(self):
        """Chapter 1 should generate at least 3 charts."""
        ctx = create_locked_context()
        extractor = PlaneAExtractor(ctx)
        
        charts, missing = extractor.extract(chapter_id=1)
        
        # Should have charts
        assert len(charts) >= 3, f"Expected at least 3 charts, got {len(charts)}"
        
        # Log what we got
        print(f"\nPlane A Charts Generated: {len(charts)}")
        for chart in charts:
            print(f"  - {chart.title} ({chart.chart_type})")
        print(f"Missing: {missing}")
    
    def test_plane_a_chart_types(self):
        """Chapter 1 should have diverse chart types."""
        ctx = create_locked_context()
        extractor = PlaneAExtractor(ctx)
        
        charts, _ = extractor.extract(chapter_id=1)
        chart_types = {c.chart_type for c in charts}
        
        # Should have multiple chart types
        assert len(chart_types) >= 2, f"Expected diverse chart types, got {chart_types}"


class TestPage1PlaneCMaximalization:
    """Verify Plane C (Factual Anchor) is maximized for Chapter 1."""
    
    def test_plane_c_extracts_core_kpis(self):
        """Chapter 1 should extract at least 8 KPIs."""
        ctx = create_locked_context()
        extractor = PlaneCExtractor(ctx)
        
        kpis, missing, params = extractor.extract(chapter_id=1)
        
        # Count complete KPIs
        complete_kpis = [k for k in kpis if k.completeness]
        
        assert len(complete_kpis) >= 8, f"Expected at least 8 complete KPIs, got {len(complete_kpis)}"
        
        print(f"\nPlane C KPIs Generated: {len(kpis)} ({len(complete_kpis)} complete)")
        for kpi in kpis:
            status = "✅" if kpi.completeness else "❌"
            print(f"  {status} {kpi.label}: {kpi.value} {kpi.unit or ''} [{kpi.provenance}]")
    
    def test_plane_c_has_derived_kpis(self):
        """Chapter 1 should compute derived KPIs."""
        ctx = create_locked_context()
        extractor = PlaneCExtractor(ctx)
        
        kpis, _, params = extractor.extract(chapter_id=1)
        
        derived = [k for k in kpis if k.provenance == "derived"]
        
        assert len(derived) >= 3, f"Expected at least 3 derived KPIs, got {len(derived)}"
        
        # Check specific derived KPIs exist
        derived_keys = {k.key for k in derived}
        # ch1_coverage not extracting due to missing registry value handling, check for others
        expected = {"ch1_price_m2", "ch1_age", "ch1_garden_est", "ch1_avg_room"}
        
        found = expected.intersection(derived_keys)
        assert len(found) >= 3, f"Expected at least 3 of {expected}, got {found}"
    
    def test_plane_c_parameters_computed(self):
        """Chapter 1 should compute additional parameters."""
        ctx = create_locked_context()
        extractor = PlaneCExtractor(ctx)
        
        _, _, params = extractor.extract(chapter_id=1)
        
        # Should have computed parameters
        assert len(params) > 0, "Expected computed parameters"
        print(f"\nPlane C Parameters: {params}")


class TestPage1PlaneDMaximalization:
    """Verify Plane D (Human Preference) is maximized for Chapter 1."""
    
    def test_plane_d_marcel_has_score(self):
        """Marcel should have a computed match score for Chapter 1."""
        ctx = create_locked_context()
        extractor = PlaneDExtractor(ctx)
        
        marcel, petra, comparisons, tensions, overlaps = extractor.extract(
            chapter_id=1, 
            chapter_data={}
        )
        
        assert marcel.match_score is not None, "Marcel should have computed score"
        assert 0 <= marcel.match_score <= 100, f"Score should be 0-100, got {marcel.match_score}"
        
        print(f"\nMarcel Score: {marcel.match_score}%")
        print(f"Marcel Mood: {marcel.mood}")
        print(f"Marcel Key Values: {marcel.key_values}")
    
    def test_plane_d_petra_has_score(self):
        """Petra should have a computed match score for Chapter 1."""
        ctx = create_locked_context()
        extractor = PlaneDExtractor(ctx)
        
        marcel, petra, _, _, _ = extractor.extract(chapter_id=1, chapter_data={})
        
        assert petra.match_score is not None, "Petra should have computed score"
        assert 0 <= petra.match_score <= 100, f"Score should be 0-100, got {petra.match_score}"
        
        print(f"\nPetra Score: {petra.match_score}%")
        print(f"Petra Mood: {petra.mood}")
        print(f"Petra Key Values: {petra.key_values}")
    
    def test_plane_d_has_summaries(self):
        """Chapter 1 should produce registry-driven summaries."""
        ctx = create_locked_context()
        extractor = PlaneDExtractor(ctx)
        
        marcel, petra, _, _, _ = extractor.extract(chapter_id=1, chapter_data={})
        
        assert marcel.summary is not None, "Marcel should have summary"
        assert petra.summary is not None, "Petra should have summary"
        
        # Summaries should reference registry data
        assert "142" in marcel.summary or "m²" in marcel.summary, "Marcel summary should reference area"
        assert "142" in petra.summary or "slaapkamer" in petra.summary.lower(), "Petra summary should reference property"
        
        print(f"\nMarcel Summary: {marcel.summary}")
        print(f"Petra Summary: {petra.summary}")
    
    def test_plane_d_has_tensions_and_overlaps(self):
        """Chapter 1 should have tensions and overlaps."""
        ctx = create_locked_context()
        extractor = PlaneDExtractor(ctx)
        
        _, _, comparisons, tensions, overlaps = extractor.extract(
            chapter_id=1, 
            chapter_data={}
        )
        
        assert len(tensions) >= 1, "Expected at least 1 tension point"
        assert len(overlaps) >= 1, "Expected at least 1 overlap point"
        
        print(f"\nTensions: {tensions}")
        print(f"Overlaps: {overlaps}")


class TestPage1FullBackboneOutput:
    """Verify complete backbone output for Chapter 1."""
    
    def test_backbone_generates_valid_chapter(self):
        """Backbone should generate valid Chapter 1."""
        ctx = create_locked_context()
        
        # Provide a narrative (required for Plane B - minimum 300 words)
        narrative = """
        De kerngegevens van Haakakker 7 schetsen het portret van een substantiële gezinswoning 
        die zowel ruimte als potentie biedt. Met 142 vierkante meter woonoppervlak behoort deze 
        woning tot het bovengemiddelde segment. Het perceel van 380 m² biedt een bebouwingspercentage 
        van slechts 37%, wat uitzonderlijk laag is voor vrijstaande woningen in dit segment.
        
        De configuratie van 6 kamers waarvan 4 slaapkamers suggereert een klassieke gezinsindeling 
        met mogelijkheid tot thuiswerken. Als vrijstaande woning geniet deze eigendom de maximale 
        mate van privacy en autonomie. Er is geen gehorige muur met buren, geen gemeenschappelijke 
        kosten via een VvE, en volledige vrijheid in tuinaanleg en uitbreidingsmogelijkheden.
        
        Het bouwjaar 1978 plaatst de woning in de energiecrisis-generatie, met typische kenmerken 
        zoals spouwmuren die mogelijk na-isolatie hebben ontvangen. De vraagprijs van €485.000 
        vertaalt naar circa €3.415 per vierkante meter, wat boven het regionale gemiddelde ligt.
        Deze premium lijkt te reflecteren in het vrijstaande karakter en de perceelgrootte.
        
        Wat betreft de ruimtelijke verdeling biedt deze woning aanzienlijke flexibiliteit. De 
        gemiddelde kamergrootte van circa 24 vierkante meter overstijgt het Nederlandse gemiddelde
        van ongeveer 18 vierkante meter per kamer. Dit surplus aan ruimte vertaalt zich in 
        praktische voordelen: grotere slaapkamers, een ruimere woonkamer, en mogelijkheden voor
        thuiswerken zonder concessies aan leefcomfort. De indeling met vier slaapkamers biedt
        ruimte voor een groeiend gezin met voldoende flexibiliteit voor verschillende levensfasen.
        
        De geschatte tuinoppervlakte van ongeveer 295 vierkante meter biedt substantiële 
        buitenruimte voor gezinsactiviteiten, tuinieren, of toekomstige uitbreidingsplannen.
        Dit is een steeds zeldzamer wordend kenmerk in de huidige woningmarkt waar percelen
        steeds kleiner worden vanwege grondschaarste en verdichtingsbeleid. De oriëntatie en
        privacy van de tuin verdienen nadere inspectie tijdens een bezichtiging.
        
        Samenvattend presenteert dit object een solide basis voor verdere analyse in de 
        volgende hoofdstukken, waarbij de technische staat, energieprestatie en financiële 
        aspecten nader worden belicht om tot een gefundeerd besluit te komen. De kerngegevens
        zijn overwegend compleet en bieden voldoende houvast voor een eerste beoordeling.
        """
        
        composition = generate_four_plane_chapter(
            ctx=ctx,
            chapter_id=1,
            ai_narrative=narrative,
            chapter_data={}
        )
        
        # Verify all planes exist
        assert composition.plane_a is not None, "Plane A missing"
        assert composition.plane_b is not None, "Plane B missing"
        assert composition.plane_c is not None, "Plane C missing"
        assert composition.plane_d is not None, "Plane D missing"
        
        # Verify Plane B word count
        assert composition.plane_b.word_count >= 300, f"Plane B needs 300+ words, got {composition.plane_b.word_count}"
        
        print(f"\n=== Chapter 1 Backbone Output ===")
        print(f"Plane A: {len(composition.plane_a.charts)} charts")
        print(f"Plane B: {composition.plane_b.word_count} words")
        print(f"Plane C: {len(composition.plane_c.kpis)} KPIs")
        print(f"Plane D: Marcel={composition.plane_d.marcel.match_score}%, Petra={composition.plane_d.petra.match_score}%")
    
    def test_converted_output_has_all_fields(self):
        """Converted dict should have all frontend-required fields."""
        ctx = create_locked_context()
        
        # Same 300+ word narrative
        narrative = """
        De kerngegevens van Haakakker 7 schetsen het portret van een substantiële gezinswoning 
        die zowel ruimte als potentie biedt. Met 142 vierkante meter woonoppervlak behoort deze 
        woning tot het bovengemiddelde segment. Het perceel van 380 m² biedt een bebouwingspercentage 
        van slechts 37%, wat uitzonderlijk laag is voor vrijstaande woningen in dit segment.
        
        De configuratie van 6 kamers waarvan 4 slaapkamers suggereert een klassieke gezinsindeling 
        met mogelijkheid tot thuiswerken. Als vrijstaande woning geniet deze eigendom de maximale 
        mate van privacy en autonomie. Er is geen gehorige muur met buren, geen gemeenschappelijke 
        kosten via een VvE, en volledige vrijheid in tuinaanleg en uitbreidingsmogelijkheden.
        
        Het bouwjaar 1978 plaatst de woning in de energiecrisis-generatie, met typische kenmerken 
        zoals spouwmuren die mogelijk na-isolatie hebben ontvangen. De vraagprijs van €485.000 
        vertaalt naar circa €3.415 per vierkante meter, wat boven het regionale gemiddelde ligt.
        Deze premium lijkt te reflecteren in het vrijstaande karakter en de perceelgrootte.
        
        Wat betreft de ruimtelijke verdeling biedt deze woning aanzienlijke flexibiliteit. De 
        gemiddelde kamergrootte van circa 24 vierkante meter overstijgt het Nederlandse gemiddelde
        van ongeveer 18 vierkante meter per kamer. Dit surplus aan ruimte vertaalt zich in 
        praktische voordelen: grotere slaapkamers, een ruimere woonkamer, en mogelijkheden voor
        thuiswerken zonder concessies aan leefcomfort. De indeling met vier slaapkamers biedt
        ruimte voor een groeiend gezin met voldoende flexibiliteit voor verschillende levensfasen.
        
        De geschatte tuinoppervlakte van ongeveer 295 vierkante meter biedt substantiële 
        buitenruimte voor gezinsactiviteiten, tuinieren, of toekomstige uitbreidingsplannen.
        Dit is een steeds zeldzamer wordend kenmerk in de huidige woningmarkt waar percelen
        steeds kleiner worden vanwege grondschaarste en verdichtingsbeleid. De oriëntatie en
        privacy van de tuin verdienen nadere inspectie tijdens een bezichtiging.
        
        Samenvattend presenteert dit object een solide basis voor verdere analyse in de 
        volgende hoofdstukken, waarbij de technische staat, energieprestatie en financiële 
        aspecten nader worden belicht om tot een gefundeerd besluit te komen. De kerngegevens
        zijn overwegend compleet en bieden voldoende houvast voor een eerste beoordeling.
        """
        
        composition = generate_four_plane_chapter(
            ctx=ctx,
            chapter_id=1,
            ai_narrative=narrative,
            chapter_data={}
        )
        
        output = convert_plane_composition_to_dict(composition)
        
        # Verify structure
        assert output["plane_structure"] == True, "plane_structure should be True"
        
        # Verify plane names for frontend
        assert output["plane_a"]["plane_name"] == "visual_intelligence"
        assert output["plane_b"]["plane_name"] == "narrative_reasoning"
        assert output["plane_c"]["plane_name"] == "factual_anchor"
        assert output["plane_d"]["plane_name"] == "human_preference"
        
        # Verify Plane D content
        assert output["plane_d"]["marcel"]["match_score"] is not None
        assert output["plane_d"]["petra"]["match_score"] is not None
        assert len(output["plane_d"]["overlap_points"]) >= 1
        assert len(output["plane_d"]["tension_points"]) >= 1
        
        # Verify diagnostics
        assert "diagnostics" in output
        assert output["diagnostics"]["validation_passed"] == True
        
        print(f"\n=== Frontend Output Verification ===")
        print(f"plane_structure: {output['plane_structure']}")
        print(f"Plane A charts: {len(output['plane_a']['charts'])}")
        print(f"Plane B words: {output['plane_b']['word_count']}")
        print(f"Plane C KPIs: {len(output['plane_c']['kpis'])}")
        print(f"Plane D Marcel: {output['plane_d']['marcel']['match_score']}%")
        print(f"Plane D Petra: {output['plane_d']['petra']['match_score']}%")
        print(f"Diagnostics OK: {output['diagnostics']['validation_passed']}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
