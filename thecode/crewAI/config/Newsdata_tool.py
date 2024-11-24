from crewai_tools import BaseTool
import requests
import os


class LatestNewsTool(BaseTool):
    name: str = "LatestNewsTool"
    description: str = "Fetches the latest news articles from Newsdata.io."

    def _run(self, query: str, size: int = 10,language: str = "en",category:str = "science,technology,other",removeduplicate:int = 1) -> dict:
        api_key = os.getenv("NEWSDATA_API_KEY")
        if not api_key:
            raise ValueError("NEWSDATA_API_KEY must be set as an environment variable.")
        
        # Ensure size does not exceed the limit for free users
        if size > 10:
            size = 10
            
        #url = f"https://newsdata.io/api/1/news?apikey={api_key}&q={query}&size={size}"
        base_url = "https://newsdata.io/api/1/latest"
        
        params = {
            'q': query,
            'apikey': api_key,
            'size': size,
            'language': language,
            'category': category,
            'removeduplicate': removeduplicate,
        }
        
        response = requests.get(base_url,params)
        
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": response.status_code, "message": response.text}
