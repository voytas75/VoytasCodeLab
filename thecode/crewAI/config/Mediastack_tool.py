from crewai_tools import BaseTool
import requests
import os
from pydantic import BaseModel, Field
from typing import Any, Optional, Type


class MediastackNewsTool(BaseTool):
    name: str = "MediastackNewsTool"
    description: str = "Fetches the latest news articles from the Mediastack API."

    def _run(self, keywords: str, **kwargs) -> dict:
        """
        Fetches the latest news articles from the Mediastack API based on the provided parameters.

        Args:
            keywords (str): Keywords to search in the news articles.
                To narrow down your search for articles even more, you can specify one or multiple comma-separated search keywords. 
                As with other parameters, you can also exclude keywords by prepending a - symbol. 
                Find a few clarifications about this parameter below:
                & keywords = food industry - Search for keyword "food industry"
                & keywords = food industry, meat - Search for keywords "food industry" and "meat"
                & keywords = food industry, -meat - Search for keywords "food industry", but exclude "meat"
                & keywords = -food industry, -meat - Search for all news, excluding "food industry" and "meat"
                & keywords = a-plus - Search for keyword "a-plus"
                & keywords = a, -plus - Search for keyword "a", but exclude "plus"
                
            **kwargs: Additional arguments for filtering the news articles.
                languages (str, optional): Languages of the news articles. Defaults to "en".
                countries (str, optional): Countries of the news sources. Defaults to "us".
                categories (str, optional): Categories of the news articles. Possible values are:
                    - general: Uncategorized News
                    - business: Business News
                    - entertainment: Entertainment News
                    - health: Health News
                    - science: Science News
                    - sports: Sports News
                    - technology: Technology News
                    Defaults to "general".
                sort (str, optional): Sort order of the news articles. Defaults to "published_desc".
                limit (int, optional): Maximum number of news articles to retrieve. Defaults to 10.
                offset (int, optional): Number of news articles to skip. Defaults to 0.

        Returns:
            dict: A dictionary containing the news articles or an error message.
        """
        api_key = os.getenv("MEDIASTACK_API_KEY")
        if not api_key:
            raise ValueError("MEDIASTACK_API_KEY must be set as an environment variable.")
        
        base_url = "http://api.mediastack.com/v1/news"
        
        params = {
            "access_key": api_key,
            "keywords": keywords,
            "languages": kwargs.get('languages', "en"),
            "countries": kwargs.get('countries', "us"),
            "categories": kwargs.get('categories', "general"),
            "sort": kwargs.get('sort', "published_desc"),
            "limit": kwargs.get('limit', 10),
            "offset": kwargs.get('offset', 0),
        }
        
        response = requests.get(base_url, params=params)
        
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": response.status_code, "message": response.text}
