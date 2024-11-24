from crewai_tools import BaseTool
import os
from serpapi import GoogleSearch
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
SERPAPI_API_KEY = os.getenv('SERPAPI_API_KEY')

# Knowledge Graph Tool
class KnowledgeGraphTool(BaseTool):
    name: str = "Knowledge Graph Extractor"
    description: str = (
        "This tool extracts specific information from Google's Knowledge Graph. "
        "Falls back to other tools if no Knowledge Graph data is available."
    )

    def _run(self, query: str) -> dict:
        params = {
            'engine': 'google',
            'q': query,
            'api_key': SERPAPI_API_KEY
        }
        search = GoogleSearch(params)
        results = search.get_dict()
        knowledge_graph = results.get('knowledge_graph', None)
        return {"knowledge_graph": knowledge_graph} if knowledge_graph else {"error": "No Knowledge Graph data found."}

# General Organic Google Search Tool
class OrganicSearchTool(BaseTool):
    name: str = "General Google Search"
    description: str = (
        "Performs a general organic Google search and retrieves organic results. "
        "Use this tool if no Knowledge Graph data is available."
    )

    def _run(self, query: str) -> dict:
        params = {
            "engine": "google",
            "q": query,
            "api_key": SERPAPI_API_KEY
        }
        search = GoogleSearch(params)
        results = search.get_dict()
        organic_results = results.get("organic_results", None)

        return organic_results