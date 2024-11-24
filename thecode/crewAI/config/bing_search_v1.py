import requests
import os
from typing import Annotated
from crewai_tools import Tool, BaseTool
from pydantic import BaseModel, Field
from typing import Any, Optional, Type


class BingWebSearchToolSchema(BaseModel):
    query: Annotated[
        str, 
        Field(
            description="The search query for the Bing Web Search Tool." 
        )
    ]
    count: Annotated[
        Optional[int], 
        Field(
            description="The number of search results to return. Default is 50.",
            ge=1
        )
    ] = 50
    responseFilter: Annotated[
        Optional[str], 
        Field(
            description=(
                "A comma-delimited list of answers to include in the response. "
                "If not specified, the response includes all search answers for "
                "which there's relevant data. Possible filter values include: "
                "- Computation\n- Entities\n- Images\n- News\n- Places\n- RelatedSearches\n"
                "- SpellSuggestions\n- TimeZone\n- Translations\n- Videos\n- Webpages\n"
                "To exclude specific types of content (e.g., images), prefix a hyphen "
                "(minus) to the responseFilter value (e.g., &responseFilter=-images)."
            ),
        )
    ] = "Webpages"
    safeSearch: Annotated[
        Optional[str], 
        Field(
            description=(
                "Level of safe search. Used to filter webpages, images, and videos for adult content. "
                "Possible values: Off, Moderate, Strict. Default is 'Moderate'."
            )
        )   
    ] = 'Moderate'


class BingWebSearchTool(BaseTool):
    name: Annotated[str, Field(default="Bing Web Search Tool", description="The name of the tool")]
    description: Annotated[str, Field(default="A tool for performing web searches with query", description="The description of the tool")]
    args_schema: Annotated[Type[BaseModel], Field(default=BingWebSearchToolSchema, description="The schema for the tool's arguments")]
    
    def _run(self, 
             query: Annotated[str, Field(description="The search query string")], 
             **kwargs: Annotated[dict, Field(description="Additional search parameters")]
            ) -> str:
        """
        Executes a web search using the Bing Search API and returns the results.

        Args:
            query (str): The search query. Advanced search options:
                Find what you're looking for faster. Use the following symbols to quickly refine your search term or search function:
                - Symbol FN +: Finds web pages containing all terms preceded by the + symbol. You can also include terms that are usually ignored.
                - " ": Finds the exact words in the phrase.
                - (): Finds or excludes web pages containing a group of words.
                - AND or &: Finds web pages containing all terms or phrases.
                - NOT or -: Excludes web pages containing a specific term or phrase.
                - OR or |: Finds web pages containing any of the terms or phrases.

                Notes:
                - By default, all searches are AND searches.
                - Use the NOT and OR operators; otherwise, Bing ignores stop words (words and numbers frequently omitted to speed up full-text searches).
                - Stop words and all punctuation marks, except the symbols mentioned here, are ignored unless they are enclosed in quotation marks or preceded by the + symbol.
                - Only the first 10 terms are used to get search results.
                - Grouping periods and logical operators are supported in the following preferred order:
                  1. (),
                  2. "",
                  3. NOT — +,
                  4. AND &,
                  5. OR |
                - The OR operator has the lowest precedence, so when searching, include OR terms in parentheses combined with other operators.
                - Some of the features described here may not be available in your country or region.

            **kwargs: Additional arguments including:
                      count (int): The number of search results to return. Default is 50.
                      responseFilter (str): A comma-delimited list of answers to include in the response. If not specified, the response includes all search answers for which there's relevant data. Possible filter values include:
                        - Computation
                        - Entities
                        - Images
                        - News
                        - Places
                        - RelatedSearches
                        - SpellSuggestions
                        - TimeZone
                        - Translations
                        - Videos
                        - Webpages
                        To exclude specific types of content (e.g., images), prefix a hyphen (minus) to the responseFilter value. For example, &responseFilter=-images. Note that while this filter can be used to get a single answer type, it's recommended to use the answer-specific endpoint (if exists) for richer results. For instance, to receive only images, send the request to one of the Image Search API endpoints. To include answers that would otherwise be excluded due to ranking, see the promote query parameter. The default is 'Webpages'.
                      safeSearch (str): Level of safe search. Used to filter webpages, images, and videos for adult content. The following are the possible filter values:
                        - Off: Returns content with adult text and images but not adult videos.
                        - Moderate: Returns webpages with adult text, but not adult images or videos.
                        - Strict: Does not return adult text, images, or videos.
                        The default is Moderate.
                        NOTE: For video results, if safeSearch is set to Off, Bing ignores it and uses Moderate.
                        NOTE: If the request comes from a market that Bing's adult policy requires that safeSearch be set to Strict, Bing ignores the safeSearch value and uses Strict.
                        NOTE: If you use the site: query operator, there is a chance that the response may contain adult content regardless of what the safeSearch query parameter is set to. Use site: only if you are aware of the content on the site and your scenario supports the possibility of adult content.
                      freshness (str): Freshness of the content. Valid case-insensitive values include:
                        'Day' — Return webpages discovered by Bing within the last 24 hours.
                        'Week' — Return webpages discovered by Bing within the last 7 days.
                        'Month' — Return webpages discovered by Bing within the last 30 days.
                        Date range in the form 'YYYY-MM-DD..YYYY-MM-DD' to specify articles discovered within a specific timeframe.
                        Specific date in the form 'YYYY-MM-DD' to limit results to that date.
                      offset (int): The zero-based offset that indicates the number of search results to skip before returning results. The default is 0. The offset should be less than (totalEstimatedMatches - count). Use this parameter along with the count parameter to page results.
                      mkt (str): The market where the results come from. Typically, mkt is the country where the user is making the request from. However, it could be a different country if the user is not located in a country where Bing delivers results. The market must be in the form <language>-<country/region>. For example, en-US. The string is case insensitive. For a list of possible market values, see Market codes. NOTE: If known, you are encouraged to always specify the market. Specifying the market helps Bing route the request and return an appropriate and optimal response. If you specify a market that is not listed in Market codes, Bing uses a best fit market code based on an internal mapping that is subject to change. To know which market Bing used, get the BingAPIs-Market header in the response. This parameter and the cc query parameter are mutually exclusive — do not specify both.
                      answerCount (int): The number of answers that you want the response to include. The answers that Bing returns are based on ranking. For example, if Bing returns webpages, images, videos, and relatedSearches for a request and you set this parameter to two (2), the response includes webpages and images.
                        If you included the responseFilter query parameter in the same request and set it to webpages and news, the response would include only webpages. For information about promoting a ranked answer into the response, see the promote query parameter. Default is None.

        Returns:
            str: A list of search results.
        """
        count = kwargs.get("count", 50)
        responseFilter = kwargs.get("responseFilter", "Webpages")
        safeSearch = kwargs.get("safeSearch", "Moderate")
        freshness = kwargs.get("freshness", "Month")
        offset = kwargs.get("offset", 0)
        mkt = kwargs.get("mkt")
        answerCount = kwargs.get("answerCount")

        # Retrieve API key and endpoint from environment variables
        api_key = os.getenv("AZURE_BING_API_KEY")
        endpoint = os.getenv("AZURE_BING_SEARCH_ENDPOINT")

        # Check if the API key is set
        if not api_key:
            raise ValueError("AZURE_BING_API_KEY must be set as an environment variable.")

        # Set up request headers and parameters
        headers = {"Ocp-Apim-Subscription-Key": api_key}
        params = {
            "q": query,
            "count": count,
            "responseFilter": responseFilter,
            "safeSearch": safeSearch,
            "freshness": freshness,
            "offset": offset,
            "mkt": mkt,
            "answerCount": answerCount
        }

        # Ensure the endpoint URL is correctly formatted
        if not endpoint.endswith("/v7.0/search"):
            endpoint = f"{endpoint.rstrip('/')}/v7.0/search"

        # Make the request to the Bing Search API
        response = requests.get(endpoint, headers=headers, params=params)
        response.raise_for_status()

        # Parse the response and extract web pages
        result_list = []
        webpages = response.json().get("webPages", {}).get("value", [])

        
        # Check if the response is empty and return an adequate message if it is
        if not webpages:
            return "No search results found for the given query."

        # Extract relevant information from each web page
        for page in webpages:
            result_list.append(
                "\n".join(
                    [
                        f"Name: {page.get('name', 'N/A')}",
                        f"URL: {page.get('url', 'N/A')}",
                        f"Date Published: {page.get('datePublished', 'N/A')}",
                        #f"Date Published Freshness: {page.get('datePublishedFreshnessText', 'N/A')}",
                        #f"Family Friendly: {page.get('isFamilyFriendly', 'N/A')}",
                        f"Display URL: {page.get('displayUrl', 'N/A')}",
                        f"Snippet: {page.get('snippet', 'N/A')}",
                        #f"Date Last Crawled: {page.get('dateLastCrawled', 'N/A')}",
                        f"Language: {page.get('language', 'N/A')}",
                        "---"
                    ]
                )
            )
        content = "\n".join(result_list)
        
        return content


def Autogen_run_bing_web_search_tool(
    input: Annotated[
        BingWebSearchToolSchema, 
        "Input schema for Bing Web Search Tool"
    ]
) -> str:
    """
    Autogen_run_bing_web_search_tool is a function designed to perform a web search using the Bing Search API.
    It takes an input of type BingWebSearchToolSchema, which includes parameters such as query, count, responseFilter, and safeSearch.
    The function constructs the necessary headers and parameters for the API request, makes the request, and processes the response.
    If the search yields results, it formats and returns them as a string. If no results are found, it returns an appropriate message.

    How to use:
    1. Ensure that the necessary environment variables are set:
       - BING_SEARCH_ENDPOINT or AZURE_BING_SEARCH_ENDPOINT
       - BING_SEARCH_API_KEY or AZURE_BING_API_KEY
    2. Create an instance of BingWebSearchToolSchema with the desired search parameters.
    3. Call the function Autogen_run_bing_web_search_tool with the BingWebSearchToolSchema instance as the input.
    4. The function will return the search results as a formatted string or an appropriate message if no results are found.

    Example:
    ```
    from bing_search_v1 import Autogen_run_bing_web_search_tool, BingWebSearchToolSchema

    search_input = BingWebSearchToolSchema(
        query="OpenAI",
        count=10,
        responseFilter="Webpages",
        safeSearch="Moderate"
    )

    results = Autogen_run_bing_web_search_tool(input=search_input)
    print(results)
    ```
    """

    print("Starting Bing Web Search Tool with the following input parameters:")
    print(f"Query: {input.query}")
    print(f"Count: {input.count}")
    print(f"Response Filter: {input.responseFilter}")
    print(f"Safe Search: {input.safeSearch}")
    endpoint = os.getenv("BING_SEARCH_ENDPOINT") or os.getenv("AZURE_BING_SEARCH_ENDPOINT")
    api_key = os.getenv("BING_SEARCH_API_KEY") or os.getenv("AZURE_BING_API_KEY")

    if not endpoint or not api_key:
        raise ValueError("Bing andpoint and Api key must be set as environment variables.")

    headers = {
        "Ocp-Apim-Subscription-Key": api_key
    }

    """  
        count = kwargs.get("count", 50)
        responseFilter = kwargs.get("responseFilter", "Webpages")
        safeSearch = kwargs.get("safeSearch", "Moderate")
        freshness = kwargs.get("freshness", "Month")
        offset = kwargs.get("offset", 0)
        mkt = kwargs.get("mkt")
        answerCount = kwargs.get("answerCount")

        params = {
            "q": query,
            "count": count,
            "responseFilter": responseFilter,
            "safeSearch": safeSearch,
            "freshness": freshness,
            "offset": offset,
            "mkt": mkt,
            "answerCount": answerCount
        }
    """

    params = {
        "q": input.query,
        "count": input.count,
        #"freshness": input.freshness,
        #"offset": input.offset,
        #"mkt": input.mkt,
        "responseFilter": input.responseFilter,
        "safeSearch": input.safeSearch,
        #"answerCount": input.answerCount
    }

    # Ensure the endpoint URL is correctly formatted
    if not endpoint.endswith("/v7.0/search"):
        endpoint = f"{endpoint.rstrip('/')}/v7.0/search"

    # Make the request to the Bing Search API
    response = requests.get(endpoint, headers=headers, params=params)
    print(f"Request URL: {response.url}")
    print(f"Response Status Code: {response.status_code}")
    response.raise_for_status()
    print(f"Response Content: {response.text}")

    # Parse the response and extract web pages
    result_list = []
    webpages = response.json().get("webPages", {}).get("value", [])

    # Check if the response is empty and return an adequate message if it is
    if not webpages:
        return "No search results found for the given query."

    # Extract relevant information from each web page
    for page in webpages:
        result_list.append(
            "\n".join(
                [
                    f"Name: {page.get('name', 'N/A')}",
                    f"URL: {page.get('url', 'N/A')}",
                    f"Date Published: {page.get('datePublished', 'N/A')}",
                    f"Display URL: {page.get('displayUrl', 'N/A')}",
                    f"Snippet: {page.get('snippet', 'N/A')}",
                    f"Language: {page.get('language', 'N/A')}",
                    "---"
                ]
            )
        )
    content = "\n".join(result_list)
    
    return content


class BingNewsSearchToolSchema(BaseModel):
    query: Annotated[str, Field(
        ..., 
        description="The search query for the Bing News Search Tool."
    )]
    count: Annotated[Optional[int], Field(
        50, 
        description="The number of search results to return. Default is 50."
    )]
    freshness: Annotated[Optional[str], Field(
        None, 
        description=("Freshness of the content. Valid case-insensitive values include:\n"
                     "'Day' — Return news articles discovered by Bing within the last 24 hours.\n"
                     "'Week' — Return news articles discovered by Bing within the last 7 days.\n"
                     "'Month' — Return news articles discovered by Bing within the last 30 days.")
    )]
    offset: Annotated[Optional[int], Field(
        0, 
        description="The zero-based offset that indicates the number of search results to skip before returning results. Default is 0."
    )]
    mkt: Annotated[Optional[str], Field(
        None, 
        description=("The market where the results come from in <language>-<country/region> format. Example: en-US. "
                     "Possible values include:\n"
                     "- Argentina: Spanish (es-AR)\n"
                     "- Australia: English (en-AU)\n"
                     "- Austria: German (de-AT)\n"
                     "- Belgium: Dutch (nl-BE)\n"
                     "- Belgium: French (fr-BE)\n"
                     "- Brazil: Portuguese (pt-BR)\n"
                     "- Canada: English (en-CA)\n"
                     "- Canada: French (fr-CA)\n"
                     "- Chile: Spanish (es-CL)\n"
                     "- Denmark: Danish (da-DK)\n"
                     "- Finland: Finnish (fi-FI)\n"
                     "- France: French (fr-FR)\n"
                     "- Germany: German (de-DE)\n"
                     "- Hong Kong SAR: Traditional Chinese (zh-HK)\n"
                     "- India: English (en-IN)\n"
                     "- Indonesia: English (en-ID)\n"
                     "- Italy: Italian (it-IT)\n"
                     "- Japan: Japanese (ja-JP)\n"
                     "- Korea: Korean (ko-KR)\n"
                     "- Malaysia: English (en-MY)\n"
                     "- Mexico: Spanish (es-MX)\n"
                     "- Netherlands: Dutch (nl-NL)\n"
                     "- New Zealand: English (en-NZ)\n"
                     "- Norway: Norwegian (no-NO)\n"
                     "- People's Republic of China: Chinese (zh-CN)\n"
                     "- Poland: Polish (pl-PL)\n"
                     "- Republic of the Philippines: English (en-PH)")
    )]


class BingNewsSearchTool(BaseTool):
    name: str = "Bing News Search Tool"
    description: str = "A tool for performing news searches."
    args_schema: Type[BaseModel] = BingNewsSearchToolSchema

    def _run(self, query: str, **kwargs) -> str:
        """
        Executes a news search using the Bing News Search API and returns the results.

        Args:
            query (str): The search query.

            **kwargs: Additional arguments including:
                      count (int): The number of search results to return. Default is 50.
                      freshness (str): Freshness of the content. Valid case-insensitive values include:
                        'Day' — Return news articles discovered by Bing within the last 24 hours.
                        'Week' — Return news articles discovered by Bing within the last 7 days.
                        'Month' — Return news articles discovered by Bing within the last 30 days.
                      offset (int): The zero-based offset that indicates the number of search results to skip before returning results. The default is 0.
                      mkt (str): The market where the results come from in <language>-<country/region> format. For example, en-US.
                        Possible values include:
                        - Argentina: Spanish (es-AR)
                        - Australia: English (en-AU)
                        - Austria: German (de-AT)
                        - Belgium: Dutch (nl-BE)
                        - Belgium: French (fr-BE)
                        - Brazil: Portuguese (pt-BR)
                        - Canada: English (en-CA)
                        - Canada: French (fr-CA)
                        - Chile: Spanish (es-CL)
                        - Denmark: Danish (da-DK)
                        - Finland: Finnish (fi-FI)
                        - France: French (fr-FR)
                        - Germany: German (de-DE)
                        - Hong Kong SAR: Traditional Chinese (zh-HK)
                        - India: English (en-IN)
                        - Indonesia: English (en-ID)
                        - Italy: Italian (it-IT)
                        - Japan: Japanese (ja-JP)
                        - Korea: Korean (ko-KR)
                        - Malaysia: English (en-MY)
                        - Mexico: Spanish (es-MX)
                        - Netherlands: Dutch (nl-NL)
                        - New Zealand: English (en-NZ)
                        - Norway: Norwegian (no-NO)
                        - People's Republic of China: Chinese (zh-CN)
                        - Poland: Polish (pl-PL)
                        - Republic of the Philippines: English (en-PH)
                        - Russia: Russian (ru-RU)
                        - South Africa: English (en-ZA)
                        - Spain: Spanish (es-ES)
                        - Sweden: Swedish (sv-SE)
                        - Switzerland: French (fr-CH)
                        - Switzerland: German (de-CH)
                        - Taiwan: Traditional Chinese (zh-TW)
                        - Türkiye: Turkish (tr-TR)
                        - United Kingdom: English (en-GB)
                        - United States: English (en-US)
                        - United States: Spanish (es-US)
                      safeSearch (str): Level of safe search. Values include 'Off', 'Moderate', and 'Strict'. Default is 'Moderate'.
                      category (str): The category of news articles to return, e.g., 'Sports', 'Entertainment'.
                      cc (str): A 2-character country code of the country where the results come from. For example:
                        - Argentina: AR
                        - Australia: AU
                        - Austria: AT
                        - Belgium: BE
                        - Brazil: BR
                        - Canada: CA
                        - Chile: CL
                        - Denmark: DK
                        - Finland: FI
                        - France: FR
                        - Germany: DE
                        - Hong Kong SAR: HK
                        - India: IN
                        - Indonesia: ID
                        - Italy: IT
                        - Japan: JP
                        - Korea: KR
                        - Malaysia: MY
                        - Mexico: MX
                        - Netherlands: NL
                        - New Zealand: NZ
                        - Norway: NO
                        - People's Republic of China: CN
                        - Poland: PL
                        - Portugal: PT
                        - Republic of the Philippines: PH
                        - Russia: RU
                        - Saudi Arabia: SA
                        - South Africa: ZA
                        - Spain: ES
                        - Sweden: SE
                        - Switzerland: CH
                        - Taiwan: TW
                        - Türkiye: TR
                        - United Kingdom: GB
                        - United States: US
                      originalImg (bool): To determine whether the Image object includes the contentUrl field or only the thumbnail field.
                      setLang (str): The language to use for user interface strings in <language>-<country/region> format.
                      since (int): The UNIX epoch time (Unix timestamp) to filter the trending topics.
                      sortBy (str): The order to return news topics in values: 'Date' or 'Relevance'.
                      textDecorations (bool): Determines if display strings in the results should contain decoration markers. Default is False.
                      textFormat (str): The type of markers to use for text decorations, values: 'Raw' or 'HTML'.
                      
        Returns:
            str: A list of search results.
        """
        count = kwargs.get("count", 50)
        freshness = kwargs.get("freshness", "Month")
        offset = kwargs.get("offset", 0)
        mkt = kwargs.get("mkt")
        safeSearch = kwargs.get("safeSearch", "Moderate")
        category = kwargs.get("category")
        cc = kwargs.get("cc")
        originalImg = kwargs.get("originalImg")
        setLang = kwargs.get("setLang")
        since = kwargs.get("since")
        sortBy = kwargs.get("sortBy")
        textDecorations = kwargs.get("textDecorations")
        textFormat = kwargs.get("textFormat")

        # Retrieve API key and endpoint from environment variables
        api_key = os.getenv("AZURE_BING_API_KEY")
        endpoint = os.getenv("AZURE_BING_SEARCH_ENDPOINT")

        # Check if the API key is set
        if not api_key:
            raise ValueError("AZURE_BING_API_KEY must be set as an environment variable.")

        # Set up request headers and parameters
        headers = {"Ocp-Apim-Subscription-Key": api_key}
        params = {
            "q": query,
            "count": count,
            "freshness": freshness,
            "offset": offset,
            "mkt": mkt,
            "safeSearch": safeSearch,
            "category": category,
            "cc": cc,
            "originalImg": originalImg,
            "setLang": setLang,
            "since": since,
            "sortBy": sortBy,
            "textDecorations": textDecorations,
            "textFormat": textFormat
        }

        # Remove any keys from params if their value is None
        params = {k: v for k, v in params.items() if v is not None}

        # Ensure the endpoint URL is correctly formatted for news search
        if not endpoint.endswith("/v7.0/news/search"):
            endpoint = f"{endpoint.rstrip('/')}/v7.0/news/search"

        # Make the request to the Bing News Search API
        response = requests.get(endpoint, headers=headers, params=params)
        response.raise_for_status()
    
        # Parse the response and extract news articles
        result_list = []
        news_articles = response.json().get("value", [])

        # Check if the response is empty and return an adequate message if it is
        if not news_articles:
            return "No news articles found for the given query."

        # Extract relevant information from each news article
        for article in news_articles:
            result_list.append(
                "\n".join(
                    [
                        f"Name: {article.get('name')}",
                        f"URL: {article.get('url')}",
                        f"Description: {article.get('description')}",
                        #"About: " + ", ".join(
                        #    [f"ReadLink: {about.get('readLink')}, Name: {about.get('name')}"
                        #     for about in article.get('about', [])]
                        #),
                        "\n".join(
                            [
                                f"Provider Name: {provider.get('name')}"
                                #f"\nProvider Type: {provider.get('_type')}"
                                for provider in article.get('provider', [])
                            ]
                        ),
                        f"DatePublished: {article.get('datePublished')}",
                        "---"
                    ]
                )
            )
        content = "\n".join(result_list)
        
        return content   
