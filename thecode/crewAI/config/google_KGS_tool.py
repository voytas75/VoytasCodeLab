#!python
"""
google_KGS_tool.py: This CrewAI's tool is designed to perform searches using the Google Knowledge Graph Search API. 

KGS docs: https://developers.google.com/knowledge-graph/reference/rest/v1/?apix=true

author: https://github.com/voytas75
repo: https://github.com/voytas75/VoytasCodeLab
"""

__author__ = 'https://github.com/voytas75'
__name__ = 'Google Knowledge Graph Search Tool'


import requests
import os
import json
import urllib

from crewai_tools import Tool, BaseTool
from pydantic import BaseModel, Field
from typing import Any, Optional, Type, Annotated


class GoogleKnowledgeGraphSearchToolSchema(BaseModel):
    query: Annotated[
        str, 
        Field(
            description="A literal string to search for in the Knowledge Graph." 
        )
    ]
    limit: Annotated[
        Optional[int], 
        Field(
            description="Limits the number of entities to be returned. Maximum is 500. Default is 10.",
            ge=1,
            le=500
        )
    ] = 10
    #indent: Annotated[
    #    Optional[bool], 
    #    Field(
    #        description="Enables indenting of JSON results. Choose from [True, False]. Default is True."
    #    )
    #] = True
    languages: Annotated[
        Optional[str], 
        Field(
            description="The list of language codes (defined in ISO 639) to run the query with, for instance 'en'."
        )
    ] = 'en'
    types: Annotated[
        Optional[str], 
        Field(
            description="Restricts returned entities to those of the specified types, e.g., 'Person'."
        )
    ] = None
    prefix: Annotated[
        Optional[bool], 
        Field(
            description="Enables prefix (initial substring) match against names and aliases of entities. Default is False."
        )
    ] = False


class GoogleKnowledgeGraphSearchTool(BaseTool):
    name: Annotated[str, Field(default="Google Knowledge Graph Search Tool", description="The name of the tool")]
    description: Annotated[str, Field(default="A tool for performing searches using the Google Knowledge Graph API", description="The description of the tool")]
    args_schema: Annotated[Type[BaseModel], Field(default=GoogleKnowledgeGraphSearchToolSchema, description="The schema for the tool's arguments")]
    
    def _run(self, 
             query: Annotated[str, Field(description="A literal string to search for in the Knowledge Graph")], 
             **kwargs: Annotated[dict, Field(description="Additional search parameters")]
            ) -> str:
        """
        Executes a search using the Google Knowledge Graph API and returns the results.

        Args:
            query (str): The search query.
            **kwargs: Additional arguments including:
                      limit (int): Limits the number of entities to be returned. Default is 10.
                      indent (bool): Enables indenting of JSON results. Default is 'True'.
                      languages (str): The list of language codes to run the query with. Default is 'en'.
                      types (str): Restricts returned entities to those of the specified types.
                      prefix (bool): Enables prefix match against names and aliases of entities. Default is False.

        Returns:
            str: A list of search results.
        """
        limit = kwargs.get("limit", 10)
        indent = kwargs.get("indent", True)
        languages = kwargs.get("languages", 'en')
        types = kwargs.get("types", None)
        prefix = kwargs.get("prefix", False)

        print("Step 1: Retrieve API key from environment variables or file")
        # Retrieve API key from environment variables or file
        api_key = os.getenv("GOOGLE_KG_API_KEY") or open('.api_key').read().strip()

        print("Step 2: Set up request parameters")
        # Set up request parameters
        params = {
            'query': query,
            'limit': limit,
            'indent': indent,
            'key': api_key,
            'languages': languages,
            'prefix': prefix
        }
        if types:
            params['types'] = types

        print("Step 3: Set up the service URL")
        # Set up the service URL
        service_url = 'https://kgsearch.googleapis.com/v1/entities:search'
        url = service_url + '?' + urllib.parse.urlencode(params)

        print("Step 4: Make the request to the Google Knowledge Graph API")
        # Make the request to the Google Knowledge Graph API
        response = json.loads(urllib.request.urlopen(url).read())
        #print(response)
        print("Step 5: Parse the response and extract relevant information")
        # Parse the response and extract relevant information
        result_list = []
        for element in response.get('itemListElement', []):
            result = element.get('result', {})
            detailedDescription = result.get('detailedDescription',{})
            result_list.append(
                "\n".join(
                    [
                        f"Name: {result.get('name', 'N/A')}",
                        f"Result Score: {element.get('resultScore', 'N/A')}",
                        f"Description: {result.get('description', 'N/A')}",
                        f"URL: {result.get('url', 'N/A')}",
                        f"Detailed Description URL: {detailedDescription.get('url', 'N/A')}",
                        "---"
                    ]
                )
            )
        content = "\n".join(result_list)
        
        return content

class GoogleKnowledgeGraphSearchJSONTool(BaseTool):
    name: Annotated[str, Field(default="Google Knowledge Graph Search Tool", description="The name of the tool")]
    description: Annotated[str, Field(default="A tool for performing searches using the Google Knowledge Graph API", description="The description of the tool")]
    args_schema: Annotated[Type[BaseModel], Field(default=GoogleKnowledgeGraphSearchToolSchema, description="The schema for the tool's arguments")]
    
    def _run(self, 
             query: Annotated[str, Field(description="A literal string to search for in the Knowledge Graph")],
             **kwargs: Annotated[dict, Field(description="Additional search parameters")]
            ) -> str:
        """
        Executes a search using the Google Knowledge Graph API and returns the results.

        Args:
            query (str): The search query.
            **kwargs: Additional arguments including:
                      limit (int): Limits the number of entities to be returned. Default is 10.
                      indent (bool): Enables indenting of JSON results. Default is 'True'.
                      languages (str): The list of language codes to run the query with. Default is 'en'.
                      types (str): Restricts returned entities to those of the specified types.
                      prefix (bool): Enables prefix match against names and aliases of entities. Default is False.

        Returns:
            str: A JSON string containing the search results from the Google Knowledge Graph API.
        """
        limit = kwargs.get("limit", 10)
        indent = kwargs.get("indent", True)
        languages = kwargs.get("languages", 'en')
        types = kwargs.get("types", None)
        prefix = kwargs.get("prefix", False)

        #print(f"Query: {query}")
        #print(f"Limit: {limit}")
        #print(f"Indent: {indent}")
        #print(f"Languages: {languages}")
        #print(f"Types: {types}")
        #print(f"Prefix: {prefix}")
        try:
            # Retrieve API key from environment variables or file
            api_key = os.getenv("GOOGLE_KG_API_KEY") or open('.api_key').read().strip()

            # Set up request parameters
            params = {
                'query': query,
                'limit': limit,
                'indent': indent,
                'key': api_key,
                'languages': languages,
                'prefix': prefix
            }
            if types:
                params['types'] = types

            # Set up the service URL
            service_url = 'https://kgsearch.googleapis.com/v1/entities:search'
            url = service_url + '?' + urllib.parse.urlencode(params)

            # Make the request to the Google Knowledge Graph API
            response = json.loads(urllib.request.urlopen(url).read())
            
            
            #print("Parse the response and extract relevant information")
            # Parse the response and extract relevant information
            result_list = []
            for element in response.get('itemListElement', []):
                result = element.get('result', {})
                detailedDescription = result.get('detailedDescription',{})
                result_list.append(
                    "\n".join(
                        [
                            f"Name: {result.get('name', 'N/A')}",
                            f"Result Score: {element.get('resultScore', 'N/A')}",
                            f"Description: {result.get('description', 'N/A')}",
                            f"URL: {result.get('url', 'N/A')}",
                            f"Detailed Description URL: {detailedDescription.get('url', 'N/A')}",
                            "---"
                        ]
                    )
                )
            content = "\n".join(result_list)
            #return response
            return content

        except urllib.error.URLError as e:
            return json.dumps({"error": f"URL Error: {e.reason}"})
        except urllib.error.HTTPError as e:
            return json.dumps({"error": f"HTTP Error: {e.code} - {e.reason}"})
        except Exception as e:
            return json.dumps({"error": f"An unexpected error occurred: {str(e)}"})
