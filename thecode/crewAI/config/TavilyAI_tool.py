
from crewai_tools import BaseTool
from tavily import TavilyClient, MissingAPIKeyError, InvalidAPIKeyError, UsageLimitExceededError
import os

class TavilySearchGeneralTool(BaseTool):
    name: str = "Tavily Search Tool"
    description: str = "Performs general search queries using the Tavily API."

    def _run(self, query: str, **kwargs) -> dict:
        """
        Perform a general search query using the Tavily API.

        Args:
            query (str): The search query string.
            **kwargs: Additional search parameters including:
                max_results (int): Maximum number of results to return. Default is 25.
                include_answer (bool): If True, include an answer summary in the results. Default is True.
                search_depth (str): Depth of the search, can be "basic" or "advanced". Default is "basic".
                days (int): Time range (in days) for the search content. Default is 30.
                include_domains (list): List of domains to include in the search. Default is None.
                exclude_domains (list): List of domains to exclude from the search. Default is None.
                include_raw_content (bool): If True, include raw content in the results. Default is False.
                include_images (bool): If True, include images in the results. Default is False.
                include_image_descriptions (bool): If True, include image descriptions in the results. Default is False.

        Returns:
            dict: The search results returned by the Tavily API.

        """
        api_key = os.getenv("TAVILY_API_KEY")
        if not api_key:
            raise ValueError("TAVILY_API_KEY must be set as an environment variable.")
        
        try:
            tavily_client = TavilyClient(api_key=api_key)
            response = tavily_client.search(
                query,
                max_results=kwargs.get('max_results', 25),
                include_answer=kwargs.get('include_answer', True),
                search_depth=kwargs.get('search_depth', "basic"),
                topic="general",
                days=kwargs.get('days', 30),
                include_domains=kwargs.get('include_domains'),
                exclude_domains=kwargs.get('exclude_domains'),
                include_raw_content=kwargs.get('include_raw_content', False),
                include_images=kwargs.get('include_images', False),
                include_image_descriptions=kwargs.get('include_image_descriptions', False)
            )
            return response
        except (MissingAPIKeyError, InvalidAPIKeyError, UsageLimitExceededError) as e:
            raise RuntimeError(f"An error occurred while performing search: {e}") from e

class TavilySearchNewsTool(BaseTool):
    name: str = "Tavily News Search Tool"
    description: str = "Performs news-specific search queries using the Tavily API."

    def _run(self, query: str, **kwargs) -> dict:
        """
        Perform a news-specific search query using the Tavily API.

        Args:
            query (str): The search query string.
            **kwargs: Additional search parameters including:
                max_results (int): Maximum number of results to return. Default is 25.
                include_answer (bool): If True, include an answer summary in the results. Default is False.
                search_depth (str): Depth of the search, can be "basic" or "advanced". Default is "basic".
                days (int): Time range (in days) for the search content. Default is 3.
                include_domains (list): List of domains to include in the search. Default is None.
                exclude_domains (list): List of domains to exclude from the search. Default is None.
                include_raw_content (bool): If True, include raw content in the results. Default is False.
                include_images (bool): If True, include images in the results. Default is False.
                include_image_descriptions (bool): If True, include image descriptions in the results. Default is False.

        Returns:
            dict: The search results returned by the Tavily API.

        """
        api_key = os.getenv("TAVILY_API_KEY")
        if not api_key:
            raise ValueError("TAVILY_API_KEY must be set as an environment variable.")
        
        try:
            tavily_client = TavilyClient(api_key=api_key)
            response = tavily_client.search(
                query,
                max_results=kwargs.get('max_results', 25),
                include_answer=kwargs.get('include_answer', False),
                search_depth=kwargs.get('search_depth', "basic"),
                topic="news",
                days=kwargs.get('days', 3),
                include_domains=kwargs.get('include_domains'),
                exclude_domains=kwargs.get('exclude_domains'),
                include_raw_content=kwargs.get('include_raw_content', False),
                include_images=kwargs.get('include_images', False),
                include_image_descriptions=kwargs.get('include_image_descriptions', False)
            )
            return response
        except (MissingAPIKeyError, InvalidAPIKeyError, UsageLimitExceededError) as e:
            raise RuntimeError(f"An error occurred while performing search: {e}") from e


class TavilyContextTool(BaseTool):
    name: str = "Tavily Context Tool"
    description: str = "Generates search context using the Tavily API."

    def _run(self, query: str, **kwargs) -> str:
        """
        Perform a context-generating query using the Tavily API.

        Args:
            query (str): The search query string.
            **kwargs: Additional search parameters including:
                search_depth (str): Depth of the search, can be "basic" or "advanced". Default is "basic".
                topic (str): The topic of the search. Default is "general".
                days (int): Time range (in days) for the search content. Default is 30.
                max_tokens (int): Maximum number of tokens to return. Default is 4000.
                max_results (int): Maximum number of results to return. Default is 5.
                include_domains (list): List of domains to include in the search. Default is None.
                exclude_domains (list): List of domains to exclude from the search. Default is None.

        Returns:
            str: The search context returned by the Tavily API.

        """
        api_key = os.getenv("TAVILY_API_KEY")
        if not api_key:
            raise ValueError("TAVILY_API_KEY must be set as an environment variable.")
        
        try:
            tavily_client = TavilyClient(api_key=api_key)
            context = tavily_client.get_search_context(
                query,
                search_depth=kwargs.get('search_depth', "basic"),
                topic=kwargs.get('topic', "general"),
                days=kwargs.get('days', 30),
                max_tokens=kwargs.get('max_tokens', 4000),
                max_results=kwargs.get('max_results', 5),
                include_domains=kwargs.get('include_domains'),
                exclude_domains=kwargs.get('exclude_domains')
            )
            return context
        except (MissingAPIKeyError, InvalidAPIKeyError, UsageLimitExceededError) as e:
            raise RuntimeError(f"An error occurred while generating context: {e}") from e


class TavilyQnATool(BaseTool):
    name: str = "Tavily QnA Tool"
    description: str = "Provides concise answers to queries using the Tavily API."

    def _run(self, query: str, **kwargs) -> str:
        """
        Perform a question-and-answer search using the Tavily API.

        Args:
            query (str): The search query string.
            **kwargs: Additional search parameters including:
                search_depth (str): Depth of the search, can be "basic" or "advanced". Default is "advanced".
                topic (str): The topic of the search. Default is "general".
                days (int): Time range (in days) for the search content. Default is 30.
                max_results (int): Maximum number of results to return. Default is 5.
                include_domains (list): List of domains to include in the search. Default is None.
                exclude_domains (list): List of domains to exclude from the search. Default is None.

        Returns:
            str: The answer returned by the Tavily API.
        """
        api_key = os.getenv("TAVILY_API_KEY")
        if not api_key:
            raise ValueError("TAVILY_API_KEY must be set as an environment variable.")
        
        try:
            tavily_client = TavilyClient(api_key=api_key)
            answer = tavily_client.qna_search(
                query,
                search_depth=kwargs.get('search_depth', "advanced"),
                topic=kwargs.get('topic', "general"),
                days=kwargs.get('days', 30),
                max_results=kwargs.get('max_results', 5),
                include_domains=kwargs.get('include_domains'),
                exclude_domains=kwargs.get('exclude_domains')
            )
            return answer
        except (MissingAPIKeyError, InvalidAPIKeyError, UsageLimitExceededError) as e:
            raise RuntimeError(f"An error occurred while performing QnA search: {e}") from e

