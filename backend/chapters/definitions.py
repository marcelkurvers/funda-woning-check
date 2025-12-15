from chapters.base import BaseChapter
from chapters.content_loader import load_and_enrich_template
from domain.models import ChapterOutput

# Import new refactored chapters
from chapters.chapter_1 import GeneralFeatures
from chapters.chapter_2 import LocationAnalysis
from chapters.chapter_3 import TechnicalState
from chapters.chapter_4 import EnergySustainability
from chapters.chapter_5 import LayoutAnalysis
from chapters.chapter_6 import MaintenanceFinish
from chapters.chapter_7 import GardenOutdoor
from chapters.chapter_8 import ParkingAccessibility
from chapters.chapter_9 import LegalAspects
from chapters.chapter_10 import FinancialAnalysis
from chapters.chapter_11 import MarketPosition
from chapters.chapter_12 import AdviceConclusion

def standard_generation(chapter: BaseChapter, id: int, title: str):
    # This function is now only a fallback for unexpected IDs or debugging
    content = load_and_enrich_template(id, title, chapter.context)
    layout = chapter._create_layout(
        left=[], 
        center=[{"type": "markdown", "content": content}], 
        right=[{"type": "advisor", "title": "Info", "content": "Generieke weergave."}]
    )
    return ChapterOutput(title=f"{id}. {title}", grid_layout=layout, blocks=[])

# --- Mapping ---

# All Chapters Refactored
Chapter1 = GeneralFeatures
Chapter2 = LocationAnalysis
Chapter3 = TechnicalState
Chapter4 = EnergySustainability
Chapter5 = LayoutAnalysis
Chapter6 = MaintenanceFinish
Chapter7 = GardenOutdoor
Chapter8 = ParkingAccessibility
Chapter9 = LegalAspects
Chapter10 = FinancialAnalysis
Chapter11 = MarketPosition
Chapter12 = AdviceConclusion
