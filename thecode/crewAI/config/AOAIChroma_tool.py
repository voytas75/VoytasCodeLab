#!/usr/bin/env python
"""
AOAIChroma_tool.py: This script is designed to integrate Azure OpenAI and ChromaDB for generating responses with memory. 
It allows users to specify a prompt and user ID for memory retrieval and storage, and provides options for the number of memory records to retrieve. 
The script utilizes configurations and tools from the CrewAI framework to perform the operations and generate responses. 
This tool is for the CrewAI framework.
author: https://github.com/voytas75
repo: https://github.com/voytas75/VoytasCodeLab
"""

__author__ = 'https://github.com/voytas75'
__name__ = 'Azure OpenAI and ChromaDB tool'


import os
import chromadb
import litellm
import json

from litellm import AzureOpenAI, completion
from chromadb import PersistentClient, Settings
from chromadb.utils.embedding_functions import OpenAIEmbeddingFunction
from crewai_tools import BaseTool
from pydantic import BaseModel, Field
from typing import Annotated, Optional, Type
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()


class AzureOpenAIChromaToolSchema(BaseModel):
    prompt: Annotated[str, Field(description="The prompt for the Azure OpenAI model.")]
    user_id: Annotated[str, Field(description="The user ID for memory retrieval and storage.")]
    max_memory_records: Annotated[Optional[int], Field(description="The maximum number of memory records to retrieve. Default is 5.", ge=1)] = 5

    class Config:
        arbitrary_types_allowed = True

class AzureOpenAIChromaTool(BaseTool):
    name: str = "Azure OpenAI Chroma Tool"
    description: str = "A tool for interacting with Azure OpenAI and ChromaDB to generate responses with memory."
    args_schema: Type[BaseModel] = AzureOpenAIChromaToolSchema

    def _run(self, prompt: str, user_id: str, max_memory_records: int = 5) -> str:
        print("Setting up Azure OpenAI client...")
        # Azure OpenAI setup
        azure_client_instance = AzureOpenAI(
            api_key=os.getenv("AZURE_API_KEY"),
            azure_endpoint=os.getenv("AZURE_API_BASE"),
            api_version=os.getenv("AZURE_API_VERSION"),
            azure_deployment=os.getenv("AZURE_CHAT_DEPLOYMENT")
        )
        
        print("Setting up ChromaDB client...")
        # ChromaDB setup
        client = chromadb.PersistentClient(path="c:/chroma/chroma_memory")
        embedding_function = OpenAIEmbeddingFunction(
            api_type="azure",
            api_key=os.getenv("AZURE_API_KEY"), 
            model_name=os.getenv("AZURE_OPENAI_EMBEDDED_MODEL"),
            deployment_id=os.getenv("AZURE_OPENAI_EMBEDDED_DEPLOYMENT"),
            api_base=os.getenv("AZURE_API_BASE"),
        )
        
        collection = client.get_or_create_collection(
            name='nlp_memory',
            embedding_function=embedding_function
        )

        print("Retrieving user memory...")
        # Retrieve user memory
        memory = collection.query(
            query_texts=[prompt],
            #query_texts=[user_id],
            n_results=max_memory_records,
            include=["documents", "distances", "metadatas"]
        ).get("documents", [])

        #print("\033[93mMemory retrieved:\033[0m", memory)
        
        print("Extracting data from the memory...")
        extracted_memory = []
        for memory_entry in memory:
            #print(f"Processing memory entry: {memory_entry}")
            for item in memory_entry:
                try:
                    #parsed_item = json.loads(item)
                    #print(f"Parsed item: {parsed_item}")
                    extracted_memory.append(item)
                except json.JSONDecodeError as e:
                    print(f"Error parsing memory entry: {e}")
        print("Extraction complete.")

        memory = extracted_memory
        
        if memory:
            print("Memory found.")
            #print("Memory after extraction:")
            #for idx, mem in enumerate(memory, start=1):
            #    print(f"Memory {idx}: {mem}")
            print(f"Count of memory list: {len(memory)}")
        else:            
            print("No memory found.")
        
        # Combine memory context with the prompt
        combined_prompt = f"{prompt}\n\nCONTEXT FROM PREVIOUS INFORMATION:\n" + "\n".join(memory)
        
        print("Generating completion with Azure OpenAI...")
        
        system_content = """
You are a helpful assistant. Your role is to give only key insights.
DO NOT make up answer and if you are not sure responde with "IDK".
Response as JSON.
"""
        
        messages = [
                {"role": "system", "content": system_content},
                {"role": "user", "content": combined_prompt}
            ]
        
        #print(messages)
        
        # Generate completion with Azure OpenAI
        response = litellm.completion(
            model = f"azure/{os.getenv("AZURE_CHAT_DEPLOYMENT")}",
            messages = messages,
        )        
        
        chat_output = response.choices[0].message.content
        
        print("Storing new memory...")
        # Store new memory
        memory_entry = {
            "user_id": user_id,
            "prompt": prompt,
            #"date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            #"response": chat_output
        }
        #collection.add(
        collection.upsert(
            documents=str(chat_output),
            metadatas=[memory_entry],
            ids=[f"{user_id}_{hash(prompt)}"]
        )
        
        print("Process completed.")
        return chat_output
