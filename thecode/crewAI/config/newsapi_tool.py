from crewai_tools import BaseTool
import requests
import os
from pydantic import BaseModel, Field
from typing import Any, Optional, Type


class NewsAPITopToolSchema(BaseModel):
    country: Optional[str] = Field(
        "us", 
        description="The country code (e.g., 'us' for the United States)."
    )
    category: Optional[str] = Field(
        "general", 
        description=("The category of news. Possible values include:\n"
                     "- general\n"
                     "- business\n"
                     "- entertainment\n"
                     "- health\n"
                     "- science\n"
                     "- sports\n"
                     "- technology")
    )
    language: Optional[str] = Field(
        "en", 
        description="The language of the news articles. Possible values include 'ar', 'de', 'en', 'es', 'fr', 'he', 'it', 'nl', 'no', 'pt', 'ru', 'se', 'ud', 'zh'."
    )
    pageSize: Optional[int] = Field(
        40, 
        description="The number of results to return per page. Default is 40."
    )

class NewsAPIEverythingToolSchema(BaseModel):
    query: str = Field(
        ...,
        description=("The search query to fetch articles. Advanced search options:\n"
                     "- Use quotes \"\" to search for exact phrases.\n"
                     "- Use the + symbol to include terms that are normally ignored.\n"
                     "- Use the - symbol to exclude terms.\n"
                     "- Use the AND, OR, and NOT operators to combine or exclude search terms.")
    )
    from_param: Optional[str] = Field(
        None,
        alias="from",
        description="The start date for the news search (e.g., '2023-01-01')."
    )
    to: Optional[str] = Field(
        None,
        description="The end date for the news search (e.g., '2023-01-31')."
    )
    language: Optional[str] = Field(
        "en",
        description=("The language of the news articles. Possible values include:\n"
                     "- 'ar': Arabic\n"
                     "- 'de': German\n"
                     "- 'en': English\n"
                     "- 'es': Spanish\n"
                     "- 'fr': French\n"
                     "- 'he': Hebrew\n"
                     "- 'it': Italian\n"
                     "- 'nl': Dutch\n"
                     "- 'no': Norwegian\n"
                     "- 'pt': Portuguese\n"
                     "- 'ru': Russian\n"
                     "- 'se': Swedish\n"
                     "- 'ud': Urdu\n"
                     "- 'zh': Chinese")
    )
    sortBy: Optional[str] = Field(
        "publishedAt",
        description=("The order to sort the articles in. Possible values are:\n"
                     "- 'relevancy': Articles more closely related to the query come first.\n"
                     "- 'popularity': Articles from popular sources come first.\n"
                     "- 'publishedAt': Newest articles come first.")
    )
    pageSize: Optional[int] = Field(
        20,
        description="The number of results to return per page. Default is 20."
    )
    page: Optional[int] = Field(
        1,
        description="The page number to retrieve. Default is 1."
    )


class NewsAPITopTool(BaseTool):
    name: str = "News API Tool"
    description: str = "Fetches top and breaking news headlines from various countries in different categories using the News API."
    args_schema: Type[BaseModel] = NewsAPITopToolSchema
    
    def _run(
        self, 
        category: str = "general",
        country: str = "us",
        language: str = "en",
        pageSize: int = 40, 
    ) -> str:
        """
        Fetch top and breaking news headlines using the News API.
        
        Args:
            country (str): The country code (e.g., 'us' for the United States).
            category (str): The category of news (e.g., 'technology', 'science').

        Returns:
            str: A summary of the top headlines.
        """
        api_key = os.getenv("NEWSAPI_KEY")  # Retrieve the News API key from environment variables
        base_url = "https://newsapi.org/v2/top-headlines" 
        if not api_key:
            raise ValueError("NEWS_API_KEY environment variable not set")
        params = {
            'country': country,
            'category': category,
            'language': language,
            'pageSize': pageSize,
            'apiKey': api_key,
        }        
        response = requests.get(base_url, params=params)        
        if response.status_code == 200:
            return response.json()
            #articles = response.json().get('articles', [])
            #headlines = [article['title'] for article in articles]
            #return "Top headlines:\n" + "\n".join(headlines)
        else:
            return f"Failed to fetch news: {response.status_code}"

class NewsAPIEverythingTool(BaseTool):
    name: str = "News API Everything Tool"
    description: str = "Fetches news articles from various sources, filtering by keyword, date, language, and other criteria using the News API Everything endpoint."
    args_schema: Type[BaseModel] = NewsAPIEverythingToolSchema
    
    
    def _run(self, query: str, **kwargs) -> str:
        """
        Fetches news articles using the News API Everything endpoint.
        
        Args:
            query (str): Keywords or phrases to search for in the article title and body.
            **kwargs: Additional filters such as from_date, to_date, language, sort_by, pageSize, and page.

        Returns:
            str: A summary of the articles found.
        """
        api_key = os.getenv("NEWSAPI_KEY")  # Retrieve the News API key from environment variables
        base_url = "https://newsapi.org/v2/everything"
        if not api_key:
            raise ValueError("NEWS_API_KEY environment variable not set")
        
        params = {
            'q': query,
            'apiKey': api_key,
        }
        params.update(kwargs)
        
        response = requests.get(base_url, params=params)
        if response.status_code == 200:
            return response.json()
            # articles = response.json().get('articles', [])
            # article_summaries = [
            #     f"{article['title']} by {article.get('author', 'Unknown')} - {article['url']}"
            #     for article in articles
            # ]
            # return "Articles:\n" + "\n".join(article_summaries)
        else:
            return f"Failed to fetch articles: {response.status_code}"

