#!/usr/bin/env python
"""
crewai-PROD-TechDiscussionAssistant.py: This script is designed to run CrewAI for technical discussions and assistance. 
It allows users to specify a topic for discussion, enables various modes such as planning and manager modes, 
and provides options for verbose output and result count. The script utilizes configurations and tools 
from the CrewAI framework to facilitate discussions and generate reports.
author: https://github.com/voytas75
repo: https://github.com/voytas75/VoytasCodeLab
example report: https://github.com/voytas75/ReportHub/blob/master/reports/WhatsNewWindowsServer2025.md
"""

__author__ = 'https://github.com/voytas75'
__name__ = 'Tech Discussion Assistent Crew'

import os
import time
import sys
import argparse
#import agentops

from crewai import Agent, Task, Crew, Process
from chromadb.utils.embedding_functions import OpenAIEmbeddingFunction

from config.config import (
    initialize_tools,
    current_date,
    current_readable_date,
    log_file,
    task_callback_function,
    step_callback_function,
    raport_base_folder,
    llm_balanced,
    llm_focused,
    llm_conversational,
    llm_creative,
    llm_deterministic,
    llm_exploratory,
    author,
    print_time_taken,
    embedder_config,
)



#region Configuration

parser = argparse.ArgumentParser(description="Run CrewAI for Technical Discussions.")
parser.add_argument("--topic", type=str, help="Specify the topic for the technical discussion")
parser.add_argument("--planning", action="store_true", help="Enable crew planning mode")
parser.add_argument("--manager", action="store_true", help="Enable crew manager (hierarchical)")
parser.add_argument("--verbose", action="store_true", help="Enable crew verbose output")
parser.add_argument("--result_count", type=int, default=15, help="Specify the number of web results to retrieve")
parser.add_argument("--nocache", action="store_false", help="Disable caching for the crew")
parser.add_argument("--nomemory", action="store_false", help="Disable memory for the crew")
args = parser.parse_args()

topic = args.topic if args.topic else ""
if not topic:
    while not topic:
        topic = input("Please provide a topic for the technical discussion: ").strip()

#agentops.init() # Agent Monitoring with AgentOps

tools = initialize_tools()


# remove because i do not use openai but ollama/lmstudio where this env is used but it makes crewai embed stop working.
#if "OPENAI_API_BASE" in os.environ:
#    os.environ.pop("OPENAI_API_BASE", None)

llm=llm_deterministic

# Setup file paths
readable_date = current_readable_date
script_name = os.path.splitext(os.path.basename(__file__))[0]
output_folder_path = os.path.join(raport_base_folder, f"{script_name}_{current_date}")
os.makedirs(output_folder_path, exist_ok=True)  # Create the output folder if it doesn't exist

#endregion


#region WELCOME

# Define the purpose of the script
script_purpose = """
Here's a friendly and professional welcome script message for your CrewAI:  

**Welcome to Tech Discussion Assistant!**  
Hi there! 👋 I'm here to help you explore and discuss topics related to any technology, like SCCM, Azure, or anything else you're curious about.  

🔍 **How it works:**  
1. Ask me a question about a specific technology or process.  
2. I'll search the internet, analyze the results, and recommend the most relevant documentation or resources.  
3. I'll provide summaries and links to help you quickly find what you need.  

📘 Ready to dive in? Just type your question, and let's get started!  
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

search_facilitator = Agent(
    role="Search Facilitator",
    goal="Conduct a web search to gather information about the user's query.",
    backstory=(
        "A proficient search expert skilled in using various search engines and APIs to find relevant articles, blogs, and documentation websites. "
        "This agent ensures the retrieval of high-quality and credible information."
    ),
    allow_delegation=False,
    llm=llm,
    verbose=False,
)

relevance_analyzer = Agent(
    role="Relevance Analyzer",
    goal="Analyze the content of search results for alignment with the user's question.",
    backstory=(
        "An analytical expert with a keen eye for detail, specializing in evaluating and ranking search results based on relevance and credibility. "
        "This agent ensures that the most pertinent information is highlighted for the user."
    ),
    llm=llm,
    verbose=False,
)

document_recommender = Agent(
    role="Document Recommender",
    goal="Suggest high-quality documentation or resources for further reading.",
    backstory=(
        "A knowledgeable resource curator with extensive experience in identifying and recommending official and credible documentation. "
        "This agent provides concise summaries and highlights the best resources for the user's needs."
    ),
    llm=llm,
    verbose=False,
)

discussion_manager = Agent(
    role="Discussion Manager",
    goal="Facilitate conversation by answering follow-up questions using retrieved data.",
    backstory=(
        "An engaging conversationalist with a strong background in customer support and information dissemination. "
        "This agent excels at providing clear and concise answers, guiding users through complex topics with ease."
    ),
    llm=llm,
    verbose=False,
)

#endregion

#region TASKS

conduct_web_search_task = Task(
    name="Web Search",
    description="""Perform a web search for the user-provided question '{question}' using search engines. Gather the top {result_count} results, including titles and descriptions.""",
    expected_output="""A markdown-formatted report with sections: 
1. Title: [Title]
2. URL: [url]
3. Description: [description]
4. Publish Date: [publish_date]
""",
    agent=search_facilitator,
    tools=[
        tools['exa'],
        tools['serpapi_google'],
        tools['bing'],
    ],
    output_file=os.path.join(output_folder_path, f"web_search_task_{script_name}_{current_date}.txt"),
)

analyze_relevance_task = Task(
    name="Relevance analyzer",
    description="""Analyze and save the search results for relevance to the user-provided question '{question}'. Score each result based on keyword matches and semantic similarity. Ensure that the website content exists, and the site is valid (no 404 errors, non-existent sites, or behind a paywall).
Save every url analyze result as separate .TXT file. The file names MUST start with 'webanalyze_' and be stored in the output directory: {output_dir}.   
""",
    expected_output="""A markdown-formatted report with sections: 
1. Title: [Title]
2. URL: [url]
3. Description: [description]
4. Publish Date: [publish_date]
5. Content Confidence Score: [low/medium/high]
6. Relevance Score: [score]
""",
    agent=relevance_analyzer,
    context=[conduct_web_search_task],
    tools=[
        tools['selenium'],
        tools['website_search'],
        tools['scrape'],
        tools['file_writer'],
        tools['file_read'],
    ],
)

recommend_documents_task = Task(
    name="Document recommendations",
    description="""Identify and recommend high-quality documentation or resources from the ranked search results. Provide a short summary for each recommended link. Read every TXT file starts with name 'webanalyze_'
The report MUST be saved as a user-friendly .TXT document with a name dynamically generated to reflect the question and date. The document MUST be stored in the output directory: {output_dir}.    
""",
    expected_output="""A markdown-formatted report with sections: 
1. Title: [Title]
2. URL: [url]
3. Publish Date: [publish_date]
4. Summary: [summary]
""",
    agent=document_recommender,
    context=[analyze_relevance_task],
    tools=[
        tools['file_writer'],
        tools['file_read'],
        tools['directory'],
    ],    
)

engage_in_discussion_task = Task(
    name="Discussion",
    description="""Answer the user-provided question '{question}' using the recommended links and provide suggestions for further exploration.""",
    expected_output="""Generate a final report in  based on the provided URLs. The conversational style report MUST include the following sections:
1. Title: [Title]
2. Author: {author}
3. Date: {date}
4. Response: Provide a detailed answer to the user-provided question '{question}' using the recommended links.
5. Recommended Links: List the relevant URLs with a brief description for each. Ensure that the URLs are accurate and do not use placeholders like example.com.
""",
    agent=discussion_manager,
    context=[recommend_documents_task],
    output_file=os.path.join(output_folder_path, f"Report.md"),
)

#endregion

#region Crew
# Update the crew with the new agents and tasks
crew = Crew(
    agents=[
        search_facilitator,
        relevance_analyzer,
        document_recommender,
        discussion_manager,
    ],
    tasks=[
        conduct_web_search_task,
        analyze_relevance_task,
        recommend_documents_task,
        engage_in_discussion_task,
    ],
    full_output=False,
    process = Process.hierarchical if args.manager else Process.sequential, 
    manager_agent = manager,
    cache=args.nocache,
    memory=args.nomemory,
    embedder=embedder_config if args.nomemory else None,
    planning=args.planning, planning_llm=llm_creative,
    step_callback=step_callback_function,
    task_callback=task_callback_function,
    share_crew=False,
    output_log_file=os.path.join(output_folder_path, log_file),
    verbose=args.verbose,
)

# Execute the crew tasks
result = crew.kickoff({
    'question': topic,
    'date': readable_date,
    'author': author,
    'result_count': args.result_count,
    'output_dir': output_folder_path,
    })

#endregion


#region Output

# Output the result
print("\n" + "-" * 50 + "\n")
"""print(result)
print("\n" + "-" * 50 + "\n")
"""
# Print the usage metrics of the crew
print(crew.usage_metrics)
print("\n" + "-" * 50 + "\n")
# Print the time taken to execute the task
print_time_taken(time.time() - start_time)
print("\n" + "-" * 50 + "\n\n")
print("Goodbye!\n\n")

#endregion