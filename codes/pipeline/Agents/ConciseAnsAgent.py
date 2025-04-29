import os
import getpass
from dotenv import load_dotenv
import google.generativeai as genai
from openai import OpenAI
from operator import itemgetter
from operator import itemgetter
from typing import Dict, List, Union
from datetime import datetime
import json

from langchain_core.prompts import PromptTemplate
from langchain import hub
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.messages import AIMessage
from langchain_core.runnables import (
    Runnable,
    RunnableLambda,
    RunnableMap,
    RunnablePassthrough,
)
from langchain_openai import ChatOpenAI

#TO CHANGE IF POSSIBLE
from LLMs import GPT4o_mini_LATS

load_dotenv('../../.env')

def conciseAns_vanilla(query, tools_list):
    print("RUNNING conciseAns_vanilla")
    finalQuery = f'''
        Note: The Current Date and Time is {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}. All your searches and responses
        must be with respect to this time frame. Whenever an agent is called, use this date time as the current date time
        if required.

        Provide a concise, and well researched answer for the following query.:
        {query}

        Provide Numbers, Financials, Case Laws, Facts in order to back the answer.
        
        Give a direct answer to the question, without showing your thought process,
        extra information, and don't provide detailed analysis. Only answer what is asked
        with the NECESSARY information backing it.
    '''
    prompt = hub.pull("hwchase17/openai-tools-agent")
    agent = create_tool_calling_agent(GPT4o_mini_LATS, tools_list, prompt)
    agent_executor = AgentExecutor(agent=agent, tools=tools_list, verbose=True)
    response = agent_executor.invoke(
        {
            "input": {finalQuery}
        }
    )
    with open("conciseResponse.md", "w") as f:
        f.write(response['output'])
    print("COMPLETED conciseAns_vanilla")
    print(response)
    print(type(response))
    return json.dumps(response['output'])


def conciseAns_rag(query,rag_context, text, api_key, LLM):
    # return response #TODO: Implement this function
    return "Not Implemented Yet"
