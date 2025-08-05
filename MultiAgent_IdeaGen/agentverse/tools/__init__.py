"""
AgentVerse Tools Module
"""

# Only import tools used by the config.yaml
from .ai_researcher_tools import (
    semantic_scholar_search,
    get_paper_details
)

__all__ = [
    'semantic_scholar_search',
    'get_paper_details'
] 