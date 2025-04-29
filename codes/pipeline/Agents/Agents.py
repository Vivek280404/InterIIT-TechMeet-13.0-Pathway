""" 
This file contains the Agent class which is used to create an agent object for each task in the LATS pipeline.
functions:
    - __init__ : initializes the agent object with the task number, name, role, constraints, task, dependencies, tools_list, state
    - genContext_andRunLATS : generates the context for the agent based on the dependencies and runs the LATS pipeline for the agent
    - Agent : class to create an agent object for each task in the LATS pipeline
"""
import google.generativeai as genai
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain import hub
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain_community.callbacks import get_openai_callback
from Agents.LATS.NewTools import *
from langchain.tools import BaseTool, tool
from datetime import datetime
from langchain.globals import set_verbose
set_verbose(True)

import logging
logging.basicConfig(level=logging.INFO)

import sys

from langchain.callbacks.tracers import ConsoleCallbackHandler

from Agents.LATS.Solve_subquery import SolveSubQuery

class Agent:
    def __init__(self, number, name, role, constraints, task, dependencies, tools_list, state):
        self.taskNumber = number
        self.name = name
        self.role = role
        self.constraints = constraints
        self.dependencies = dependencies
        self.context = ''
        self.task = task
        self.state = state

        tl_lis = []

        if len(tools_list)<1:
            tools_list.append('web_search')

        for function_name in tools_list:
            if '(' in function_name:
                function_name = function_name.split('(')[0]
                tl_lis.append(globals()[function_name])
            else:
                tl_lis.append(globals()[function_name])
        self.tools_list = tl_lis[:]
        
        if self.state == 'RAG':
            self.tools_list.append(retrieve_documents)

        self.PREFIX_TEMPLATE = f"""You are a {self.name}, with the following role : {self.role}."""
        self.CONSTRAINT_TEMPLATE = f"the constraint is {self.constraints}. "

        self.func_docs = ''''''

        for func in self.tools_list:
            self.func_docs+=f'''{func.name}: {func.description}\n'''

        
    def genContext_andRunLATS(self, response_dict):
        for task in self.dependencies:
            if task in response_dict:
                self.context += response_dict[task]
            else:
                print(f"{task} not executed yet, it should have been executed before {self.taskNumber}")

        ROLE_TEMPLATE = f"""

            Note: The Current Date and Time is {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}. All your searches and responses
            must be with respect to this time frame.

            IMPORTANT: DO NOT REMOVE ANY SOURCE LINKS. FORMAT THEM ACCORDING TO MARKDOWN. 
            Cite all the sources, website links, and data sources

            Make your response on the basis of the history: 
            {self.context} 

            and the specific subtask for you {self.task}

            Based on your role, research and give us a comprehensive response analyzing various metrics. Try to stick to your role. 
            Try to substantiate your answers with as much numbers, comparatives, facts, case laws and history as possible wherever required.
            Provide Numbers and Explicitly researched facts in your response in order to back your claims. You may also provide tables of 
            relevant information. 
            Research, analyze and report from a multi-dimensional aspect, for instance interdependency
            between multiple domains like finance, microeconomics, macroeconomics, public policy, politics, law, environment etc,
            Large Scale considerations v/s Small Scale considerations, Long Term Considerations v/s Short Term Considerations etc.
            You have access to the following tools:

            {self.func_docs}

            Use the following format for reasoning:
            - Thought: Describe what you're thinking.
            - Action: Choose a tool from the pool of tools.
            - Action Input: Provide the input for the tool. Ensure that the input provided matches with the parameters of the tool, and the datatypes are same.
            - Observation: Record the tool's result. In this observation, give a detailed explanation and reasoning of your response, backed by facts and numbers wherever required.
            Ensure that the Observation, that is the Final response is not short and concise, but detailed report with all the facts and figures well substantiated. 
            Try to substantiate your answers with as much numbers, comparatives, facts, case laws and history as possible wherever required.
            MAKE YOUR OUTPUTS EXTREMELY DETAILED AND WELL REASONED AND DO NOT OMIT ANY IMPORTANT FACTS WHICH ARE RESEARCHED BY THE TOOLS.

            IMPORTANT: Cite all the sources, website links, and data sources at the location where information is mentioned. 
            All links must be functional and correspond to the data. Cite the links at the location of the data, and at the end
            of the report generated. This is EXTREMELY IMPORTANT. THESE LINKS SHOULD BE CLICKABLE.
        """
        PROMPT_TEMPLATE = self.PREFIX_TEMPLATE + self.CONSTRAINT_TEMPLATE + ROLE_TEMPLATE
        
        response = SolveSubQuery(PROMPT_TEMPLATE, self.tools_list)

        return response


        

        







