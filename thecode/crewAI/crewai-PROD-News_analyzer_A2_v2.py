#!/usr/bin/env python
"""
crewai-PROD-News_analyzer_A2_v2.py: This script is designed to run CrewAI for news search and analysis. 
It allows users to specify a topic for analysis, enables various modes such as planning and manager modes, 
and provides options for verbose output and result count. The script utilizes configurations and tools 
from the CrewAI framework to perform the analysis and generate reports.
author: https://github.com/voytas75
repo: https://github.com/voytas75/VoytasCodeLab
"""

__author__ = 'https://github.com/voytas75'
__name__ = 'News Analyzer Crew'


import os
import time
import sys
#import agentops
import argparse

from crewai import Agent, Task, Crew, Process
from chromadb.utils.embedding_functions import OpenAIEmbeddingFunction

from config.config import (
    initialize_tools,
    current_date,
    current_readable_date,
    log_file,
    callback_function,
    step_callback_function,
    raport_base_folder,
    llm_balanced,
    llm_focused,
    llm_conversational,
    llm_creative,
    llm_deterministic,
    llm_exploratory,
    author
)


# region FUNCTIONS

def print_time_taken(time_taken):
    """Prints the time taken to execute the crew."""
    if time_taken < 60:
        print("Time taken to execute crew: less than 1 minute")
    else:
        print(f"Time taken to execute crew: {time_taken / 60:.2f} minutes")

# endregion


#region Configuration

parser = argparse.ArgumentParser(description="Run CrewAI for News Search.")
parser.add_argument("--topic", type=str, help="Specify the topic to analyze in News")
parser.add_argument("--planning", action="store_true", help="Enable crew planning mode")
parser.add_argument("--manager", action="store_true", help="Enable crew manager (hierarchical)")
parser.add_argument("--verbose", action="store_true", help="Enable crew verbose output")
parser.add_argument("--result_count", type=int, default=10, help="Specify the number of web results per provider to retrieve")
parser.add_argument("--nocache", action="store_false", help="Disable caching for the crew")
parser.add_argument("--nomemory", action="store_false", help="Disable memory for the crew")
args = parser.parse_args()

topic = args.topic if args.topic else ""
if not topic:
    while not topic:
        topic = input("Please provide a topic to analyze in News: ").strip()


#agentops.init() # Agent Monitoring with AgentOps

tools = initialize_tools()


# remove because i do not use openai but ollama/lmstudio where this env is used but it makes crewai embed stop working.
if "OPENAI_API_BASE" in os.environ:
    os.environ.pop("OPENAI_API_BASE", None)

llm=llm_focused
# Setup file paths
readable_date = current_readable_date

script_name = os.path.splitext(os.path.basename(__file__))[0]
output_folder_path = os.path.join(raport_base_folder, f"{script_name}_{current_date}")
os.makedirs(output_folder_path, exist_ok=True)  # Create the output folder if it doesn't exist

#endregion


#region WELCOME

# Define the purpose of the script
script_purpose = """
Welcome to your CrewAI Team! 🚀  

This crew is designed to streamline your work with specialized agents for data gathering, analysis, content creation, and reporting. Each agent is equipped with tools and expertise to ensure efficiency, accuracy, and actionable results across diverse tasks.  

Whether it's identifying trends, crafting reports, verifying data, or building timelines, your team is here to help you achieve your goals effortlessly. Let's get started! 🌟  

"""
print(script_purpose)


print(f"\033[92mTopic: {topic}\033[0m\n\n")


start_time = time.time()

#endregion


#region AGENTS

# Define the manager agent
manager = Agent(
    role="Project Manager",
    goal="Efficiently manage the crew and ensure high-quality task completion",
    backstory="You're an experienced project manager, skilled in overseeing complex projects and guiding teams to success. Your role is to coordinate the efforts of the crew members, ensuring that each task is completed.",
    llm=llm_exploratory,
)

general_purpose_agent = Agent(
    role="General Purpose Analyst",
    goal="Undertake and successfully complete any task assigned, utilizing extensive data gathering, analysis, and synthesis methodologies.",
    backstory=(
        "A highly skilled generalist proficient in multiple domains, including advanced web research, precise data scraping, "
        "thorough information synthesis, and detailed content creation. This agent ensures rigor and quality in all analyses, "
        "producing actionable insights with a commitment to accuracy and professionalism."
    ),
    llm=llm,
    verbose=False,
)

web_search_agent = Agent(
    role="Web Search Agent",
    goal="Perform web searches across multiple news platforms.",
    backstory=(
        "A versatile agent proficient in conducting web searches across various news platforms, ensuring comprehensive data collection. "
        "Skilled in data aggregation and synthesis to provide a unified view of the gathered information."
    ),
    llm=llm,
    verbose=False, 
)

content_scraping_agent = Agent(
    role="Content Scraping Agent",
    goal="Scrape content from identified web sources.",
    backstory=(
        "An expert in web scraping, capable of extracting relevant content from various online sources. "
        "Ensures that the scraped data is accurate, well-organized, and ready for further analysis."
    ),
    llm=llm,
    verbose=False, 
)

trend_analysis_agent = Agent(
    role="Trend Analysis Agent",
    goal="Critically assess the organized data, drawing comparisons and identifying trends among the different articles and perspectives. Highlight significant patterns, differences, and insights that contribute to a deeper understanding of the topic, providing valuable commentary for the final report.",
    backstory=(
        "As a former data analyst in a prestigious research firm, you spent years interpreting data and uncovering trends in various industries. Your analytical "
        "mindset allows you to see beyond the surface, identifying subtle patterns and correlations that others might overlook. With a passion for storytelling "
        "through data, you transitioned into a role that combines your analytical skills with your love for journalism. Now, as a Trend Analysis Agent, "
        "you utilize your expertise to provide insightful comparisons and highlight emerging trends, ensuring that each report is not only informative but also impactful."
    ),
    llm=llm,
    verbose=False,
)

twitter_posts_writer = Agent(
    role="Social Media Content Strategist",
    goal="Craft engaging and informative Twitter/X posts related to {topic}.",
    backstory=(
        "An expert social media strategist with a strong background in creating impactful social media content. "
        "Possesses the ability to distill complex information into concise and captivating posts, driving engagement and effectively communicating key insights."
    ),
    max_iter=3,
    llm=llm,
    verbose=False,
)

data_verification_agent = Agent(
    role="Data Verification Specialist",
    goal="Verify the accuracy and authenticity of gathered data related to {topic}.",
    backstory=(
        "A meticulous and detail-oriented specialist, dedicated to ensuring the integrity and reliability of data. "
        "Possesses extensive experience in cross-referencing sources, validating information, and identifying any discrepancies. "
        "Committed to maintaining the highest standards of data accuracy in all analyses."
    ),
    llm=llm,
    verbose=False,
)

report_writer = Agent(
    role="Technical Report Specialist",
    goal="Write a detailed and professional report on '{topic}'.",
    backstory=(
        "A dedicated technical writer with extensive experience in integrating and organizing complex data from multiple sources into coherent, "
        "insightful reports. This specialist ensures the production of high-quality, well-structured reports that meet stringent standards of clarity and depth."
    ),
    llm=llm,
    verbose=False, 
)

news_timeline_builder = Agent(
    role="News Timeline Builder",
    goal="Focus on gathering events related to a given topic and constructing a chronological timeline.",
    backstory=(
        "This agent specializes in organizing information temporally, ensuring clarity and relevance in presenting how events unfold. "
        "With a background in historical research and data journalism, the News Timeline Builder excels at piecing together events from various sources "
        "to create a coherent and informative timeline. This agent's meticulous approach ensures that each event is accurately placed in context, "
        "providing a clear narrative of the topic's development over time."
    ),
    llm=llm,
    verbose=False,
)

#endregion


#region TASKS

analyze_user_topic_task = Task(
    name="Analyze User Topic Task",
    description="""Analyze the user-provided topic '{topic}'. Understand what the user is asking for, and suggest relevant web search queries. Provide query phrases ranging from short to advanced ones. 
""",
    expected_output="""A markdown-formatted report with sections: 
1. original topic: {topic}
2. **Basic Search Queries**:
    - [queries]
3. **Intermediate Search Queries**:
    - [queries]
4. **Advanced Search Queries**:
    - [queries]    
""",
    agent=general_purpose_agent,
    tools=[
    ],
    output_file=os.path.join(output_folder_path, f"analyze_user_topic_task_{script_name}_{current_date}.txt"),
)


web_search_bingnews_task = Task(
    name="Bing News Web Search Task",
    description="""Perform a web search. Perform a comprehensive bing news web search on the given topic '{topic}' using the provided search queries or create query text to get results. 
""",
    expected_output="""A markdown-formatted report with the following structure:

# Structure

1. **Query**: [State the original query used in the search.]
2. **Number of Results**: [State the total number of results found.]
3. **Results**: List the top {result_count} results with the following details:
    - **Title/Name**: [State the title of the web page.]
    - **Address/URL**: [Provide the URL of the web page from which the content was scraped.]
    - **Source**: [State the source of the news article. This could be the name of the news outlet, the author's name, or any other relevant information that indicates the origin of the article.]
    - **Content**: [Provide the main content retrieved from the web page. The content MUST be relevant and succinct, focusing on the topic at hand.]
    - **Publication Date**: [Include the publication date of the article.]
    - **Other**: [Additional information about the scraped content.]

# Analysis

- Ensure the content is relevant to the topic and provides a comprehensive overview.
- Verify the credibility of the sources and the accuracy of the information.
- Summarize the key points and insights from the content.

""",
    agent=web_search_agent,
    context=[analyze_user_topic_task],
    tools=[
        tools['bingnews'],
    ],
    output_file=os.path.join(output_folder_path, f"web_search_bingnews_task_{script_name}_{current_date}.txt"),
)

web_search_mediastack_task = Task(
    name="Mediastack News Web Search Task",
    description="""Perform a web search. Perform a comprehensive Mediastack news web search on the given topic '{topic}' using the provided search queries or create query text to get results. If there are no results, must search web again by changing your query.
""",
    expected_output="""A markdown-formatted report with the following structure:

# Structure

1. **Query**: [State the original query used in the search.]
2. **Number of Results**: [State the total number of results found.]
3. **Results**: List the top {result_count} results with the following details:
    - **Title/Name**: [State the title of the web page.]
    - **Address/URL**: [Provide the URL of the web page from which the content was scraped.]
    - **Source**: [State the source of the news article. This could be the name of the news outlet, the author's name, or any other relevant information that indicates the origin of the article.]
    - **Content**: [Provide the main content retrieved from the web page. The content MUST be relevant and succinct, focusing on the topic at hand.]
    - **Publication Date**: [Include the publication date of the article.]
    - **Other**: [Additional information about the scraped content.]

# Analysis

- Ensure the content is relevant to the topic and provides a comprehensive overview.
- Verify the credibility of the sources and the accuracy of the information.
- Summarize the key points and insights from the content.

""",
    agent=web_search_agent,
    context=[analyze_user_topic_task],
    tools=[
        tools['media_stack'],
    ],
    output_file=os.path.join(output_folder_path, f"web_search_mediastack_task_{script_name}_{current_date}.txt"),
)

web_search_newsapi_task = Task(
    name="Newsapi News Web Search Task",
    description="""Perform a web search. Perform a comprehensive Newsapi news web search on the given topic '{topic}' using the provided search queries or create query text to get results. If there are no results, must search web again by changing your query.
""",
    expected_output="""A markdown-formatted report with the following structure:

# Structure

1. **Query**: [State the original query used in the search.]
2. **Number of Results**: [State the total number of results found.]
3. **Results**: List the top {result_count} results with the following details:
    - **Title/Name**: [State the title of the web page.]
    - **Address/URL**: [Provide the URL of the web page from which the content was scraped.]
    - **Source**: [State the source of the news article. This could be the name of the news outlet, the author's name, or any other relevant information that indicates the origin of the article.]
    - **Content**: [Provide the main content retrieved from the web page. The content MUST be relevant and succinct, focusing on the topic at hand.]
    - **Publication Date**: [Include the publication date of the article.]
    - **Other**: [Additional information about the scraped content.]

# Analysis

- Ensure the content is relevant to the topic and provides a comprehensive overview.
- Verify the credibility of the sources and the accuracy of the information.
- Summarize the key points and insights from the content.

""",
    agent=web_search_agent,
    context=[analyze_user_topic_task],
    tools=[
        tools['newsapi_everything'],
    ],
    output_file=os.path.join(output_folder_path, f"web_search_newsapi_task_{script_name}_{current_date}.txt"),
)

web_search_newsdata_task = Task(
    name="Newsdata News Web Search Task",
    description="""Perform a web search. Perform a comprehensive Newsdata news web search on the given topic '{topic}' using the provided search queries or create query text to get results. If there are no results, must search web again by changing your query.
""",
    expected_output="""A markdown-formatted report with the following structure:

# Structure

1. **Query**: [State the original query used in the search.]
2. **Number of Results**: [State the total number of results found.]
3. **Results**: List the top {result_count} results with the following details:
    - **Title/Name**: [State the title of the web page.]
    - **Address/URL**: [Provide the URL of the web page from which the content was scraped.]
    - **Source**: [State the source of the news article. This could be the name of the news outlet, the author's name, or any other relevant information that indicates the origin of the article.]
    - **Content**: [Provide the main content retrieved from the web page. The content MUST be relevant and succinct, focusing on the topic at hand.]
    - **Publication Date**: [Include the publication date of the article.]
    - **Other**: [Additional information about the scraped content.]

# Analysis

- Ensure the content is relevant to the topic and provides a comprehensive overview.
- Verify the credibility of the sources and the accuracy of the information.
- Summarize the key points and insights from the content.

""",
    agent=web_search_agent,
    context=[analyze_user_topic_task],
    tools=[
        tools['newsdata'],
    ],
    output_file=os.path.join(output_folder_path, f"web_search_newsdata_task_{script_name}_{current_date}.txt"),
)

web_search_exa_task = Task(
    name="EXA News Web Search Task",
    description="""Perform a web search. Perform a comprehensive EXA news web search on the given topic '{topic}' using the provided search queries or create query text to get results. If there are no results, must search web again by changing your query.
""",
    expected_output="""A markdown-formatted report with the following structure:

# Structure

1. **Query**: [State the original query used in the search.]
2. **Number of Results**: [State the total number of results found.]
3. **Results**: List the top {result_count} results with the following details:
    - **Title/Name**: [State the title of the web page.]
    - **Address/URL**: [Provide the URL of the web page from which the content was scraped.]
    - **Source**: [State the source of the news article. This could be the name of the news outlet, the author's name, or any other relevant information that indicates the origin of the article.]
    - **Content**: [Provide the main content retrieved from the web page. The content MUST be relevant and succinct, focusing on the topic at hand.]
    - **Publication Date**: [Include the publication date of the article.]
    - **Other**: [Additional information about the scraped content.]

# Analysis

- Ensure the content is relevant to the topic and provides a comprehensive overview.
- Verify the credibility of the sources and the accuracy of the information.
- Summarize the key points and insights from the content.

""",
    agent=web_search_agent,
    context=[analyze_user_topic_task],
    tools=[
        tools['exa'],
    ],
    output_file=os.path.join(output_folder_path, f"web_search_exa_task_{script_name}_{current_date}.txt"),
)

web_search_tavily_news_task = Task(
    name="Tavily News Web Search Task",
    description="""Perform a web search. Perform a comprehensive Tavily news web search on the given topic '{topic}' using the provided search queries or create query text to get results. If there are no results, must search web again by changing your query.
""",
    expected_output="""A markdown-formatted report with the following structure:

# Structure

1. **Query**: [State the original query used in the search.]
2. **Number of Results**: [State the total number of results found.]
3. **Results**: List the top {result_count} results with the following details:
    - **Title/Name**: [State the title of the web page.]
    - **Address/URL**: [Provide the URL of the web page from which the content was scraped.]
    - **Source**: [State the source of the news article. This could be the name of the news outlet, the author's name, or any other relevant information that indicates the origin of the article.]
    - **Content**: [Provide the main content retrieved from the web page. The content MUST be relevant and succinct, focusing on the topic at hand.]
    - **Publication Date**: [Include the publication date of the article.]
    - **Other**: [Additional information about the scraped content.]

# Analysis

- Ensure the content is relevant to the topic and provides a comprehensive overview.
- Verify the credibility of the sources and the accuracy of the information.
- Summarize the key points and insights from the content.

""",
    agent=web_search_agent,
    context=[analyze_user_topic_task],
    tools=[
        tools['tavily_news'],
    ],
    output_file=os.path.join(output_folder_path, f"web_search_tavily_news_task_{script_name}_{current_date}.txt"),
)

aggregate_news_data_task = Task(
    name="Aggregate News Data Task",
    description="""Aggregate. Ensure that all relevant information is included, and each entry is properly formatted and categorized.
""",
    expected_output="""A comprehensive markdown-formatted report with the following structure:

# Aggregated News Data Report

## Overview
Provide a brief overview of the aggregated news data, including the total number of sources and any notable observations.

## Detailed Entries
For each news item, include the following details:

1. **Title/Name**: [The title of the web page or news article]
2. **URL**: [The URL of the source]
3. **Source**: [The name of the news outlet, author's name, or any other relevant information indicating the origin]
4. **Publication Date**: [The publication date of the news article or web page]
5. **Content**: [A summary of the main content retrieved from the source. Ensure the summary is concise and relevant to the topic]
6. **Metadata**: [Additional data such as author's name, language, country, and any other relevant information]

## Summary and Insights
- Summarize the key points and insights from the aggregated data.
- Highlight any trends, common themes, or significant findings.
- Provide an analysis of the credibility and relevance of the sources.

## Conclusion
- Offer a final summary of the aggregated news data.
- Include any recommendations or next steps based on the findings.

""",
    context=[
        web_search_bingnews_task, 
        web_search_mediastack_task, 
        web_search_exa_task, 
        web_search_newsdata_task, 
        web_search_tavily_news_task, 
        web_search_newsapi_task,
    ],
    agent=general_purpose_agent,
    output_file=os.path.join(output_folder_path, f"aggregate_news_data_task_{script_name}_{current_date}.txt"),
)

web_scraping_task = Task(
    name="Web Data Scraping Task",
    description="""Scrape URL's content. Perform read website content. You MUST read all URLs website content and create a report. Ensure that the website content exists, and the site is valid (there is no 404 errors, there is no non-existent sites, there is no paywall). 
""",
    expected_output="""A markdown-formatted report with the following structure:

# Web Data Scraping Report

1. **Number of URLs**: Provide the total number of URLs scraped.
2. **Results**: List the top 20 scraped URLs with detailed information:
    - **URL**: Include the URL of the web page from which the data was scraped for easy reference and verification.
    - **Title/Name**: State the title of the web page to understand the context of the scraped content.
    - **Metadata**: If available, include the date of publication, the author's name, or any other relevant metadata that provides context to the content.
    - **Content**: Provide detailed content retrieved from the website.
    - **Other Information**: Include additional information about the news website or page, such as language, country, etc. If available, include any additional details that might be useful for further analysis or interpretation of the data, such as the language of the content, the country of origin, or any other relevant details that could impact the analysis or interpretation of the data.
""",
    context=[aggregate_news_data_task],
    agent=content_scraping_agent,
    tools=[
        tools['scrape'],
        tools['selenium'],
    ],
    output_file=os.path.join(output_folder_path, f"web_scraping_task_{script_name}_{current_date}.txt"),
)

social_media_posts_task = Task(
    name="Social Media Posts Creation Task",
    description="""Create five engaging, catchy, creative and concise posts for Platform X (formerly Twitter)
""",
    expected_output="""A plain-text report with the following structure:

# Posts List

1. **Post**: Create an engaging, catchy, and concise post for Platform X (formerly Twitter). Ensure the post includes 3 to 5 hashtags, emojis, and a URL if available. Add the URL as is, without using the [text](url) format.
2. **Reasoning**: Provide a detailed explanation of why this post is the best choice, highlighting its potential impact and relevance.
3. **Rating**: Assign an indicator value assessing the potential reception of the post, ranging from 0.000 to 1.000.

# Guide

1. Ensure each post uses 3 to 5 hashtags, emojis, and includes a URL if available.
2. Add the URL as is. DO NOT use the [text](url) format.
""",
    agent=twitter_posts_writer,
    context=[web_scraping_task],
    async_execution=True,
    output_file=os.path.join(output_folder_path, f"output_twitter_posts_task_{script_name}_{current_date}.txt"),
)

verification_data_task = Task(
    name="Verification Data Task",
    description="""Verify the accuracy and authenticity of gathered news data related to the topic '{topic}'.  Ensure that the news data is accurate, credible, and relevant to the topic. This includes cross-referencing sources, checking for biases, and confirming the validity of the information. Ensure that urls are valid. 
""",
    expected_output="""A markdown-formatted report with the following sections:

# Web Data Verification Report

1. **Introduction**: Provide a brief overview of the news topic and explain the purpose of the data verification process.
2. **Clarifying Questions**: List any clarifying questions asked to validate the news data, along with the responses received, if applicable.
3. **Source Verification**: Describe the process of cross-referencing sources and present the findings.
4. **URL Verification**: Detail the results of the URL verification process, including any issues or discrepancies found, such as invalid URLs or 404 errors.
5. **Bias Check**: Identify any potential biases in the news data and explain how they were addressed.
6. **Relevance Check**: Explain how the relevance of the data to the topic was confirmed.
7. **Statistical Validation**: Present the results of any statistical validation methods applied to the data.
8. **External Validation**: Summarize the findings from external validation services or additional agents used in the verification process.
9. **Conclusion**: Summarize the overall results of the verification process and confirm the authenticity and credibility of the data.
""",
    context=[web_scraping_task],
    agent=data_verification_agent,
    output_file=os.path.join(output_folder_path, f"verification_data_task_{script_name}_{current_date}.txt"),
)

task_analyze_trends_and_compare = Task(
    name="Trends Analysis and Comparison Task",
    description="""Analyze the information to identify trends, commonalities, and differences across the News articles by topic '{topic}'.
""",
    expected_output="""A markdown-formatted report with the following structure:

# Key Trends
Identify and elaborate on common patterns, themes, or insights emerging from multiple articles. Ensure that each trend is substantiated with relevant data points and examples for enhanced credibility.

# Differing Perspectives
Conduct a thorough examination of areas of disagreement or contrasting viewpoints presented by various reputable sources. Highlight the implications of these differing opinions and the context in which they arise.

# Unique Insights
Identify and expound on standout information or unique insights that offer a deeper or more nuanced understanding of the topic. Ensure these insights are clearly distinguished and contextually well-explained.

# Detailed Analysis
Provide a formal, objective analysis throughout, utilizing bullet points for clarity and a structured format. Include rigorous citations and references where applicable to maintain the credibility and traceability of information.

# Professional Relevance
Construct the summary with a specific focus on the needs of data analysts and decision-makers, emphasizing clarity, coherence, and actionable insights. Ensure the analysis offers practical value and facilitates informed decision-making.
""",
    agent=trend_analysis_agent,
    context=[web_scraping_task, 
             verification_data_task],
    output_file=os.path.join(output_folder_path, f"trend_analysis_task_{script_name}_{current_date}.txt"),
)

analyze_to_report_findings_task = Task(
    name="Analyze Data to Report Findings Task",
    description="""Analyze the collected data. The focus MUST be on summarizing key insights, trends, and unique observations relevant to the topic '{topic}' and compiling these into a coherent report. 
""",
    expected_output="""Generate a markdown-formatted report with the following structure:
1. **Introduction**: Provide a brief overview of the collected data and explain the purpose of the analysis.
2. **Key Trends**: Identify and describe the main trends observed in the data.
3. **Unique Insights**: Elaborate on any unique insights and findings derived from the data.
4. **Comparison**: Conduct a comparative analysis of differing perspectives and data points.
5. **Conclusion**: Summarize the findings and provide final thoughts on the analysis.
""",
    agent=report_writer,
    context=[web_scraping_task, 
             verification_data_task],
    output_file=os.path.join(output_folder_path, f"analyze_to_report_findings_task_{script_name}_{current_date}.txt"),
)

analyze_to_report_recommendations_task = Task(
    name="Analyze Data to Report Recommendations Task",
    description="""
Analyze the collected data. The focus MUST be on summarizing key insights, trends, and unique observations relevant to the topic '{topic}' and compiling these into a coherent report.
""",
    expected_output="""Generate a markdown-formatted report with the following sections:
1. **Introduction**: Provide a brief overview of the collected data and explain the purpose of the analysis.
2. **Key Trends**: Identify and describe the main trends observed in the data, substantiating each trend with relevant data points and examples.
3. **Unique Insights**: Elaborate on any unique insights and findings derived from the data, ensuring these insights are clearly distinguished and contextually well-explained.
4. **Comparison**: Conduct a comparative analysis of differing perspectives and data points, highlighting the implications and context of these differences.
5. **Recommendations**: Offer actionable recommendations based on the conclusions drawn from the analysis, emphasizing practical value and informed decision-making.
6. **Conclusion**: Summarize the findings and provide final thoughts on the analysis, ensuring clarity and coherence.
""",
    agent=report_writer,
    context=[web_scraping_task, 
             verification_data_task, 
             analyze_to_report_findings_task],
    output_file=os.path.join(output_folder_path, f"analyze_to_report_recommendations_task_{script_name}_{current_date}.txt"),
)

build_timeline_task = Task(
    name="Build Timeline of Events Task",
    description="""Build timeline. Extract and organize key events related to the topic '{topic}' from the collected news data. The events should be presented in a chronological timeline, ensuring each event includes a detailed description, source, and timestamp. Optionally, categorize the events with relevant tags.
""",
    expected_output="""Generate a markdown-formatted report with the following structure:
1. **List of Events**: Provide a detailed list of events in either JSON, markdown, or table format. Each event should include:
    - **Event Description**: A brief summary or headline of the event.
    - **Source**: The source from which the event information was obtained.
    - **Timestamp**: The date or time when the event occurred.
    - **Tags**: Optional tags or categorization (e.g., type of event).
2. **Visual Representation**: Optionally include a visual representation of the events, such as a Gantt chart or timeline graphic, to enhance the understanding of the chronological sequence.

# Example Format
- **Event Description**: A brief summary or headline of the event.
- **Source**: The source from which the event information was obtained.
- **Timestamp**: The date or time when the event occurred.
- **Tags**: Optional tags or categorization (e.g., type of event).
""",
    agent=news_timeline_builder,
    context=[
        web_search_bingnews_task, 
        web_search_tavily_news_task,
        #web_search_mediastack_task, 
        web_search_newsapi_task, 
        web_search_newsdata_task, 
        web_search_exa_task,         
    ],
    output_file=os.path.join(output_folder_path, f"build_timeline_task_{script_name}_{current_date}.txt"),
)

final_comprehensive_report_task = Task(
    name="Final Comprehensive News Report",
    description="""Create a comprehensive and professional final news report on the topic '{topic}'. Ensure the report is thoroughly verified by analyzing the content five times and asking clarifying questions to validate accuracy. MUST include hyperlinks in relevant sections to guide reader to the news or articles.
""",
    expected_output="""Generate a comprehensive markdown-formatted report with the following structure:

1. **Title**: Provide a concise and descriptive title for the report.
    - Include the date of creation: {date}
    - Author: {author}

2. **Table of Contents**: Create links to each section of the report for easy navigation.

3. **Introduction**: Write an overview of the topic being analyzed.

4. **Trends**: Identify and describe trends, commonalities, and differences across the news articles.

5. **Findings**: Present detailed content for each finding, including titles and relevant data.

6. **Recommendations**: Offer actionable recommendations based on the conclusions drawn from the analysis.

7. **News and Articles**: List the title, URL, and description of each article used in the report. Ensure the data is accurate and relevant to existing news websites.

8. **Timeline**: Construct a chronological timeline of key events related to the topic. Include descriptions, sources, and timestamps to provide a clear and structured overview of the sequence of events.

9. **Questions**: Formulate questions to help users delve deeper into the topic.
    - Simple questions: Up to 5 short and clarifying questions to gain deeper insight into the topics, news, articles, and findings.
    - Advanced questions: Up to 5 complex and detailed questions to gain deeper insight into the topics, news, articles, and findings.

10. **Executive Summary and Conclusions**: Summarize the report with a brief executive summary and conclusions based on all findings.

11. **X Posts (formerly Twitter)**: Create 5 engaging, catchy, creative, and concise posts based on the report findings and recommendations. Each post should use 3 to 5 hashtags, emojis, and URLs if available. Analyze suggested tweets and recommend only one, providing a reason for your choice:
    - Recommended Post: [Your recommended X's post here]
    - Posts: [List of all suggested X's posts here]

# Markdown Syntax Guidelines

## Headings
Use `#` for headings. The number of `#` symbols indicates the heading level, e.g.:
# Heading 1
## Heading 2
### Heading 3

## Emphasis
Examples:
- **Bold**: `**bold text**` or `__bold text__`
- *Italic*: `*italic text*` or `_italic text_`
- ~~Strikethrough~~: `~~strikethrough~~`

## Lists
- **Unordered list**: Use `-`, `*`, or `+`, e.g.:
    - Item 1
    - Item 2
- **Ordered list**: Use numbers, e.g.:
1. First item
2. Second item

## Links
Examples:
[Link text](https://example.com)

## Images
Examples:
![Alt text](https://example.com/image.jpg)

## Code
Examples:
- **Inline code**: Use backticks: `` `code` ``
- **Code block**: Use triple backticks:

```<code language name, eg. `python`, `text`, `powershell`>
Code block
```

## Blockquotes
Eexamples:
> This is a blockquote.

## Horizontal Rule
Example:
---

NOTE: Do not use the Markdown block "```" at the beginning and end of a report!
""",
    agent=report_writer,
    context=[
        verification_data_task, 
        web_scraping_task, 
        social_media_posts_task, 
        analyze_to_report_findings_task, 
        analyze_to_report_recommendations_task, 
        task_analyze_trends_and_compare,
        build_timeline_task
    ],
    output_file=os.path.join(output_folder_path, f"Report.md"),
)

# Define a task for the general_purpose_agent to create an auto-generated .MD file name based on context and save a summary of data in the file
generate_summary_report_task = Task(
    name="Generate Summary Report",
    description="""Generate a concise and informative summary of the data.
""",
    expected_output="A well-structured markdown-formatted summary report.",
    context=[final_comprehensive_report_task],
    agent=general_purpose_agent,
    output_file=os.path.join(output_folder_path, f"Summary_Report.md"),
)

#endregion

#region Crew
# Update the crew with the new agents and tasks
crew = Crew(
    agents=[
        general_purpose_agent,
        web_search_agent,
        content_scraping_agent,
        twitter_posts_writer,
        trend_analysis_agent,
        data_verification_agent,
        news_timeline_builder,
        report_writer,
    ],
    tasks=[
        analyze_user_topic_task,
        web_search_bingnews_task,
        #web_search_mediastack_task, 
        web_search_exa_task, 
        web_search_newsdata_task, 
        web_search_tavily_news_task, 
        web_search_newsapi_task,        
        aggregate_news_data_task,
        web_scraping_task,
        social_media_posts_task,
        verification_data_task,
        task_analyze_trends_and_compare,
        analyze_to_report_findings_task,
        analyze_to_report_recommendations_task,
        build_timeline_task,
        final_comprehensive_report_task,
        generate_summary_report_task,
    ],
    full_output=False,
    process = Process.hierarchical if args.manager else Process.sequential, 
    manager_agent = manager,
    cache=args.nocache,
    memory=args.nomemory,
    embedder=OpenAIEmbeddingFunction(
        api_key=os.getenv("AZURE_API_KEY"),
        api_base=os.getenv("AZURE_API_BASE"),
        api_type="azure",
        api_version=os.getenv("AZURE_API_VERSION"),
        model_name=os.getenv("AZURE_OPENAI_EMBEDDED_MODEL"),
        deployment_id=os.getenv("AZURE_OPENAI_EMBEDDED_DEPLOYMENT"),
    ),    
    planning=args.planning, planning_llm=llm_creative,
    #step_callback=step_callback_function,
    #task_callback=callback_function,
    share_crew=False,
    output_log_file=os.path.join(output_folder_path, log_file),
    verbose=args.verbose,
)

# Execute the crew tasks
result = crew.kickoff({
    'topic': topic,
    'date': readable_date,
    'author': author,
    'result_count': args.result_count,
    'output_dir': output_folder_path,
    })

#endregion


#region Output

# Output the result
print("\n" + "-" * 50 + "\n")
# Print the usage metrics of the crew
print(crew.usage_metrics)
print("\n" + "-" * 50 + "\n")
# Print the time taken to execute the task
print_time_taken(time.time() - start_time)
print("\n" + "-" * 50 + "\n\n")
print("Goodbye!\n\n")

#endregion
