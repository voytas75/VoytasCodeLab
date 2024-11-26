import os
import sys    
from datetime import datetime
from selenium import webdriver
from crewai_tools import (
    Tool,
    FileWriterTool,
    ScrapeWebsiteTool,
    RagTool,
    WebsiteSearchTool,
    EXASearchTool,
    SeleniumScrapingTool,
    SerperDevTool,
    FileReadTool,
    DirectoryReadTool,
    TXTSearchTool,
    PDFSearchTool,
    BrowserbaseLoadTool,
    CodeDocsSearchTool,
    CodeInterpreterTool,
    CSVSearchTool,
    DallETool,
    DirectorySearchTool,
    DOCXSearchTool,
    GithubSearchTool,
    JSONSearchTool,
    MDXSearchTool,
    YoutubeChannelSearchTool,
    YoutubeVideoSearchTool,
)
from .bing_search_v1 import BingWebSearchTool, BingNewsSearchTool
from .Mediastack_tool import MediastackNewsTool
from .newsapi_tool import NewsAPITopTool, NewsAPIEverythingTool
from .Newsdata_tool import LatestNewsTool
from .TavilyAI_tool import TavilySearchGeneralTool, TavilySearchNewsTool, TavilyContextTool, TavilyQnATool
from .custom_pdf_tool import CustomPDFReadTool
from .AOAIChroma_tool import AzureOpenAIChromaTool 
from .serpapi_Google_tools import OrganicSearchTool, KnowledgeGraphTool 
from dotenv import load_dotenv
from tavily import TavilyClient
from crewai import LLM




def callback_function(output):
    # Do something after the task is completed
    print(f"\033[94m[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Task '{output.name}' completed\033[0m")

def step_callback_function(step):
    # List all attributes of step:
    # thought
    # output
    # text
    # tool (not present in every case)
    # tool_input (only in some tasks)
    # result (present when tools are used)
    
    """step_attributes = vars(step)
    
    for attr, value in step_attributes.items():
        #print(f"{attr}: {value}")
        print(f"    attr: {attr}")"""    

    if step:
        if step.thought:
            step.thought = step.thought.replace('\n', ' ')
            thought_text = step.thought[:300] + "..." if len(step.thought) > 300 else step.thought
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]    Thought: {thought_text}")
        #if step.tool:
        #    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]    Tool: {step.tool}")
        #    if step.tool_input:
        #        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]    Tool Input: {step.tool_input}")
        


def initialize_tools():
   # selenium
   options = webdriver.ChromeOptions()
   options.add_experimental_option('excludeSwitches', ['enable-logging'])
   options.add_argument("--incognito")
   options.add_argument("--log-level=3")
   options.add_argument("--headless")
   options.add_argument("--disable-logging")
   options.add_argument("--disable-gpu-vsync") # Disables GPU vsync, which can help with faster rendering.
   options.add_argument("--disable-extensions") # Disables all extensions, which can speed up the browser.
   options.add_argument("--disable-background-networking") # Disables background networking, which can reduce unnecessary network activity.
   options.add_argument("--disable-translate") # Disables the translation feature, which can speed up page loading.
   # https://peter.sh/experiments/chromium-command-line-switches/
   
   driver = webdriver.Chrome(options=options)
   
   config=dict(
        llm=dict(
            provider="azure_openai", # or google, openai, anthropic, llama2, ...
            config=dict(
                model=os.getenv('AZURE_CHAT_DEPLOYMENT_MODEL'),
                deployment_name=os.getenv('AZURE_CHAT_DEPLOYMENT'),
                temperature=0.2,
                top_p=0.7,
                # stream=true,
            ),
        ),
        embedder=dict(
            provider="azure_openai", # or openai, ollama, ...
            config=dict(
                model=os.getenv("AZURE_OPENAI_EMBEDDED_MODEL"),
                deployment_name=os.getenv("AZURE_OPENAI_EMBEDDED_DEPLOYMENT"),
                # aby dzialalo musi byc wykasowana zmienna OPENAI_API_BASE: https://github.com/langchain-ai/langchain/discussions/17790#discussioncomment-8690960
                # baza jest w c:\Users\voytas\.embedchain\
            ),
        ),
   )
   return {
        'bing': BingWebSearchTool(),
        'bingnews': BingNewsSearchTool(),
        'scrape': ScrapeWebsiteTool(), # https://docs.crewai.com/tools/scrapewebsitetool
        'rag': RagTool(config=config),
        'website_search': WebsiteSearchTool(config=config),        
        'file_writer': FileWriterTool(),
        'file_read': FileReadTool(),
        'directory': DirectoryReadTool(),
        'directory_search': DirectorySearchTool(config=config),
        'text_search': TXTSearchTool(config=config), # https://docs.crewai.com/tools/txtsearchtool
        'media_stack': MediastackNewsTool(),
        'newsapi_top': NewsAPITopTool(),
        'newsapi_everything': NewsAPIEverythingTool(),
        'newsdata': LatestNewsTool(),
        'exa': EXASearchTool(),
        #'selenium': SeleniumScrapingTool(driver=driver),
        'selenium': SeleniumScrapingTool(), # https://docs.crewai.com/tools/seleniumscrapingtool
        'serperdev': SerperDevTool(), # https://docs.crewai.com/tools/serperdevtool
        'tavily_general':TavilySearchGeneralTool(),
        'tavily_news': TavilySearchNewsTool(),
        'tavily_context': TavilyContextTool(),
        'tavily_qna': TavilyQnATool(),
        'pdf_read': CustomPDFReadTool(),
        'pdf_search': PDFSearchTool(config=config), # https://docs.crewai.com/tools/pdfsearchtool
        #'browser': BrowserbaseLoadTool(),
        'code_docs_search': CodeDocsSearchTool(config=config),
        'code_interpreter': CodeInterpreterTool(),
        'csv_search': CSVSearchTool(config=config),
        'dalle': DallETool(),
        'docx_search': DOCXSearchTool(config=config),
        'github_search': GithubSearchTool(
            config=config,
            gh_token=os.getenv('GH_TOKEN'),
            content_types=['code','issue']
        ), # https://docs.crewai.com/tools/githubsearchtool
        'json_search': JSONSearchTool(config=config), # https://docs.crewai.com/tools/jsonsearchtool
        'mdx_search': MDXSearchTool(config=config), # https://docs.crewai.com/tools/mdxsearchtool
        'ytch_search': YoutubeChannelSearchTool(config=config),
        'ytv_search': YoutubeVideoSearchTool(config=config),
        'nlp_search': AzureOpenAIChromaTool(),
        'serpapi_google': OrganicSearchTool(),
        'serpapi_google_kg': KnowledgeGraphTool(), # google knowledge graph
    }
   
def create_llm_config(temperature, top_p, frequency_penalty, presence_penalty):
    return {
        "model": f"azure/{os.getenv('AZURE_CHAT_DEPLOYMENT')}",
        "base_url": os.getenv("AZURE_API_BASE"),
        "api_key": os.getenv("AZURE_API_KEY"),
        "api_version": os.getenv("AZURE_API_VERSION"),
        "temperature": temperature,
        "top_p": top_p,
        "frequency_penalty": frequency_penalty,
        "presence_penalty": presence_penalty,
        # "seed": 42,  # Optional: Set a seed for reproducibility
    }

load_dotenv()

#embedder
embedder_config = {
    "provider": "azure",
    "config": {
        "api_key": os.getenv("AZURE_OPENAI_API_KEY"),
        "api_base": os.getenv("AZURE_OPENAI_ENDPOINT"),
        "api_type": "azure",
        "api_version": os.getenv("AZURE_API_VERSION"),
        "model_name": os.getenv("AZURE_OPENAI_EMBEDDED_MODEL"),
        "deployment_id": os.getenv("AZURE_OPENAI_EMBEDDED_DEPLOYMENT"),
    }
}

#print("In module products sys.path[0], __package__ ==", sys.path[0], __package__)

# Configure Azure OpenAI access
azure_api_key = os.getenv("AZURE_API_KEY") or input("Enter your Azure OpenAI api key: ").strip()
azure_api_base = azure_openai_endpoint = os.getenv("AZURE_API_BASE") or input("Enter your Azure OpenAI Endpoint: ").strip()
azure_api_version = azure_openai_version = os.getenv("AZURE_API_VERSION") or input("Enter your Azure OpenAI API Version: ").strip()
azure_chat_deployment = azure_openai_deployment = os.getenv("AZURE_CHAT_DEPLOYMENT") or input("Enter your PSAOAI API Azure OpenAI Deployment: ").strip()
azure_embedding_deployment = os.getenv("AZURE_OPENAI_EMBEDDED_DEPLOYMENT") or input("Enter your Azure OpenAI Embedded Deployment: ").strip()
# remember to configure envs LiteLLM https://docs.litellm.ai/docs/providers/azure


current_date=datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
current_readable_date = datetime.now().strftime('%B %d, %Y')
log_file = f"LOG_crew_{current_date}.log"
#raport_base_folder = input("Enter the base folder for the report: ").strip()

if os.path.exists("/path/to/A/"):
    raport_base_folder = "/path/to/A/"
elif os.path.exists("/path/to/B/"):
    raport_base_folder = "/path/to/B"
else:
    raport_base_folder = input("Enter the base folder for the report: ").strip()

author = "<your_name>, CrewAI"


llm_balanced = LLM(**create_llm_config(0.2, 0.7, 0.1, 0.1))
llm_deterministic = LLM(**create_llm_config(0.0, 0.1, 0.0, 0.0))
llm_creative = LLM(**create_llm_config(0.9, 0.9, 0.5, 0.5))
llm_exploratory = LLM(**create_llm_config(0.7, 0.8, 0.3, 0.3))
llm_focused = LLM(**create_llm_config(0.3, 0.5, 0.2, 0.2))
llm_conversational = LLM(**create_llm_config(0.6, 0.7, 0.4, 0.4))
