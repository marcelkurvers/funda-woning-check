from typing import Dict, Any
from chapters.base import BaseChapter
from domain.models import ChapterOutput, UIComponent
from intelligence import IntelligenceEngine

class MediaLibraryChapter(BaseChapter):
    def get_title(self) -> str:
        return "Media Bibliotheek"

    def generate(self) -> ChapterOutput:
        # Get data from IntelligenceEngine fallback for consistency
        narrative = IntelligenceEngine.generate_chapter_narrative(13, self.data)
        
        # Render the standard magazine layout
        content_html = self._render_rich_narrative(narrative)
        
        # Create standard layout
        layout = self._create_layout(
            center=[UIComponent(type="markdown", content=content_html)],
            right=[UIComponent(type="advisor_card", title="Visuele Audit", content="De AI heeft de foto's geanalyseerd op onderhoud, kwaliteit en risico's.")]
        )
        
        return ChapterOutput(
            id="13",
            title=self.get_title(),
            grid_layout=layout,
            blocks=[],
            chapter_data=narrative
        )
