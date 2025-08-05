#!/usr/bin/env python
"""
AI-Researcher Tools - Minimal version for semantic search and paper details
Based on core functionalities from Stanford AI-Researcher project
"""

import json
from typing import Dict, List, Any
from semanticscholar import SemanticScholar

from agentverse.logging import logger

# LangChain tool wrappers
from langchain.tools import tool
from langchain.tools import BaseTool


class AIResearcherSearchTool(BaseTool):
    name: str = "ai_researcher_search"
    description: str = "AI-Researcher level enhanced literature search tool"
    
    def _run(self, query: str) -> str:
        return semantic_scholar_search(query)
    
    async def _arun(self, query: str) -> str:
        return semantic_scholar_search(query)


class GetPaperDetailsTool(BaseTool):
    name: str = "get_paper_details"
    description: str = "Tool for getting detailed paper information"
    
    def _run(self, paper_id: str) -> str:
        return get_paper_details(paper_id)
    
    async def _arun(self, paper_id: str) -> str:
        return get_paper_details(paper_id)


# Compatibility wrappers
@tool
def ai_researcher_search_tool(query: str) -> str:
    """AI-Researcher level enhanced literature search tool"""
    return semantic_scholar_search(query)

@tool  
def get_paper_details_tool(paper_id: str) -> str:
    """Tool for getting detailed paper information"""
    return get_paper_details(paper_id)


# Tool name mapping
TOOL_MAPPING = {
    "ai_researcher_search": AIResearcherSearchTool(),
    "get_paper_details": GetPaperDetailsTool(),
}


# Get tool function
def get_tool(tool_name: str):
    """Get tool function"""
    if tool_name in TOOL_MAPPING:
        return TOOL_MAPPING[tool_name]
    else:
        # Try to return function directly
        if tool_name == "ai_researcher_search":
            return AIResearcherSearchTool()
        elif tool_name == "get_paper_details":
            return GetPaperDetailsTool()
        else:
            raise ValueError(f"Unknown tool: {tool_name}")


class AIResearcherTools:
    """
    AI-Researcher integrated tool class (minimal version)
    Provides only semantic scholar search and paper details functionality
    """
    
    def __init__(self, semantic_scholar_api_key: str = None):
        """Initialize AI-Researcher tools"""
        import os
        if semantic_scholar_api_key is None:
            semantic_scholar_api_key = os.environ.get("SEMANTIC_SCHOLAR_API_KEY", "YOUR_SEMANTIC_SCHOLAR_API_KEY_HERE")
        self.s2_api_key = semantic_scholar_api_key
        self.sch = SemanticScholar(api_key=self.s2_api_key)
        
        # Paper cache
        self.search_cache = {}
        
        logger.info("AI-Researcher Tools initialized with Semantic Scholar API")
    
    def _semantic_scholar_search(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Semantic Scholar API search"""
        
        if query in self.search_cache:
            return self.search_cache[query]
        
        try:
            # Search papers
            results = self.sch.search_paper(
                query=query,
                limit=limit,
                fields=['paperId', 'title', 'authors', 'year', 'abstract', 
                       'citationCount', 'venue', 'url', 'publicationDate']
            )
            
            papers = []
            for paper in results:
                if paper and hasattr(paper, 'raw_data'):
                    paper_data = paper.raw_data
                    cleaned_paper = self._clean_paper_data(paper_data)
                    papers.append(cleaned_paper)
            
            self.search_cache[query] = papers
            return papers
            
        except Exception as e:
            logger.error(f"Semantic Scholar search failed: {e}")
            return []
    
    def _clean_paper_data(self, paper_data: Dict) -> Dict[str, Any]:
        """Clean paper data"""
        authors = []
        if paper_data.get('authors'):
            authors = [author.get('name', 'Unknown') for author in paper_data['authors']]
        
        return {
            'paperId': paper_data.get('paperId'),
            'title': paper_data.get('title', 'Unknown Title'),
            'authors': authors,
            'author_string': ', '.join(authors[:3]) + (' et al.' if len(authors) > 3 else ''),
            'year': paper_data.get('year'),
            'abstract': paper_data.get('abstract', ''),
            'citationCount': paper_data.get('citationCount', 0),
            'venue': paper_data.get('venue', ''),
            'url': paper_data.get('url', ''),
            'publicationDate': paper_data.get('publicationDate', '')
        }
    

# Instantiate global tool object
ai_researcher_tools = AIResearcherTools()


def semantic_scholar_search(query: str, limit: int = 10) -> str:
    """Direct Semantic Scholar search tool interface"""
    try:
        papers = ai_researcher_tools._semantic_scholar_search(query, limit)
        return json.dumps(papers, indent=2, ensure_ascii=False)
    except Exception as e:
        return f"Semantic Scholar search failed: {e}"


def get_paper_details(paper_id: str) -> str:
    """Get paper details tool interface"""
    try:
        paper = ai_researcher_tools.sch.get_paper(
            paper_id,
            fields=['paperId', 'title', 'authors', 'year', 'abstract', 
                   'citationCount', 'venue', 'url', 'references', 'citations']
        )
        
        if paper and hasattr(paper, 'raw_data'):
            return json.dumps(paper.raw_data, indent=2, ensure_ascii=False)
        else:
            return f"Paper not found: {paper_id}"
    except Exception as e:
        return f"Get paper details failed: {e}"