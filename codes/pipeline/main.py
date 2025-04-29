"""
This script sets up a WebSocket server to handle various types of queries and tasks using different agents and APIs.
Functions:
    mainBackend(query, websocket, rag):
        Handles the main backend processing of queries, including classification, planning, and execution of tasks using various agents.
    handle_connection(websocket):
        Manages incoming WebSocket connections and routes messages to the appropriate handlers.
    main():
        Starts the WebSocket server and keeps it running indefinitely.
"""
import os
from dotenv import load_dotenv
load_dotenv('../.env')

import time
import json
import google.generativeai as genai
import re

# Import custom agents for different tasks
from Agents.Agents import Agent
from Agents.Smack import Smack
from Agents.ClassifierAgent import classifierAgent, classifierAgent_RAG
from Agents.PlannerAgent import plannerAgent, plannerAgent_rag
from Agents.ChartGenAgent import generate_chart
from Agents.DrafterAgent import drafterAgent_vanilla, drafterAgent_rag
from Agents.ConciseAnsAgent import conciseAns_vanilla, conciseAns_rag
from Agents.RAG_Agent import ragAgent
from Agents.LATS.Solve_subquery import SolveSubQuery
from Agents.conciseLatsAgent import conciseAns_vanilla_LATS
from langchain_community.callbacks import get_openai_callback
from langchain_openai import ChatOpenAI

from Agents.LATS.NewTools import *
import json
import threading
import asyncio
import websockets

from langchain.globals import set_verbose

import concurrent.futures
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, List, Any
from collections import defaultdict

from makeGraphJSON import makeGraphJSON

from TopicalGuardrails import applyTopicalGuardails
from GenerateQuestions import genQuestionComplex, genQuestionSimple

set_verbose(True)
now = time.time()


async def mainBackend(query, websocket, rag):
    """
    Main backend function to process queries and interact with a websocket.
    This function handles different types of queries (simple or complex) and 
    processes them using various agents and pipelines. The function 
    also generates and sends responses back through the websocket.
    Args:
        query (str): The input query to be processed.
        websocket (WebSocket): The websocket connection to send responses.
        rag (bool): Flag to indicate if RAG mode is enabled.
    Returns:
        None
    """

    print("Running mainBackend, ", query)
    GOOGLE_API_KEY = os.getenv('GEMINI_API_KEY_30')
    OPENAI_API_KEY = os.getenv('OPEN_AI_API_KEY_30')
    os.makedirs('./output', exist_ok=True)
    LLM = 'OPENAI'
    key_dict = {
        'OPENAI': OPENAI_API_KEY,
        'GEMINI': GOOGLE_API_KEY
    }
    api_key = key_dict[LLM]

    IS_RAG = rag

    if IS_RAG == True:
        print("RAG is ON")
    else:
        print("RAG is OFF")

    with open("ProcessLogs.md", "w") as f:
        f.write("")
    with open("tickers.txt", "a") as f_ticker:
        f_ticker.write('')

    # Apply guardrails to the query
    guard_rails, reasonings = applyTopicalGuardails(query)
    
    resp = ''
    additionalQuestions = None
    addn_questions = []
    
    if guard_rails:
        if not IS_RAG:
            query_type = classifierAgent(query).lower()
            print("RUNNING without Internal Docs Context")
            if query_type == "complex":
                print("RUNNING COMPLEX TASK PIPELINE")
                
                plan = plannerAgent(query)
                #This is the dictionary for UI Graph Construction
                dic_for_UI_graph = makeGraphJSON(plan['sub_tasks'])
                print(dic_for_UI_graph)
                await asyncio.sleep(1)
                await websocket.send(json.dumps({"type": "graph", "response": json.dumps(dic_for_UI_graph)}))
                with open('Graph.json', 'w') as fp:
                    json.dump(dic_for_UI_graph, fp)
                
                out_str = ''''''
                agentsList = []
                
                for sub_task in plan['sub_tasks']:
                    addn_questions.append(plan['sub_tasks'][sub_task]['content'])
                    agent_name = plan['sub_tasks'][sub_task]['agent']
                    agent_role = plan['sub_tasks'][sub_task]['agent_role_description']
                    local_constraints = plan['sub_tasks'][sub_task]['local_constraints']
                    task = plan['sub_tasks'][sub_task]['content']
                    dependencies = plan['sub_tasks'][sub_task]['require_data']
                    tools_list = plan['sub_tasks'][sub_task]['tools']
                    agent_state = 'vanilla'
                    print(f'processing {agent_name}')
                    agent = Agent(sub_task, agent_name, agent_role, local_constraints, task,dependencies, tools_list, agent_state)
                    agentsList.append(agent)
                
                # Execute the task results using the Smack agent
                smack = Smack(agentsList)
                taskResultsDict = smack.executeSmack()
                for task in taskResultsDict:
                    out_str += f'{taskResultsDict[task]} \n'
                resp = drafterAgent_vanilla(query, out_str)
                resp = re.sub(r'\\\[(.*?)\\\]', lambda m: f'$${m.group(1)}$$', resp, flags=re.DOTALL)
                resp = generate_chart(resp)
                '''additionalQuestions = []
                for que in addn_questions:
                    finQue = await genQuestionComplex(query, addn_questions)
                    additionalQuestions.append(finQue)'''
                additionalQuestions = await genQuestionSimple(addn_questions)


            elif query_type == "simple":
                print("RUNNING SIMPLE TASK PIPELINE")   
                async def executeSimplePipeline(query):
                    tools_list = [get_stock_data, web_search_simple, get_basic_financials, get_company_info, get_stock_dividends, get_income_stmt, get_balance_sheet, get_cash_flow, get_analyst_recommendations]
                    resp = conciseAns_vanilla(query, tools_list)   
                    resp = re.sub(r'\\\[(.*?)\\\]', lambda m: f'$${m.group(1)}$$', resp, flags=re.DOTALL)
                    return str(resp)

                async def run_parallel(query):
                    resp, additionalQuestions = await asyncio.gather(
                        executeSimplePipeline(query),
                        genQuestionSimple(query)
                    )
                    return (str(resp), additionalQuestions)
                # resp = await executeSimplePipeline(query)
                resp, additionalQuestions = await run_parallel(query)

        elif IS_RAG:
            print("Running Internal Docs RAG")
            rag_context = ragAgent(query, state = "concise")
            print("========================")
            query_type = classifierAgent_RAG(query, rag_context).lower()
            
            if query_type == "complex":
                agent_state = 'RAG'
                print("RUNNING COMPLEX TASK PIPELINE")

                rag_context = ragAgent(query, state = 'report')
                plan = plannerAgent_rag(query, rag_context)
                
                dic_for_UI_graph = makeGraphJSON(plan['sub_tasks'])
                for node in dic_for_UI_graph['nodes']:
                    node['metadata']['tools'].append('retrieve_documents')

                print(dic_for_UI_graph)
                await asyncio.sleep(1)
                await websocket.send(json.dumps({"type": "graph", "response": json.dumps(dic_for_UI_graph)}))
                with open('Graph.json', 'w') as fp:
                    json.dump(dic_for_UI_graph, fp)
                
                out_str = ''''''
                agentsList = []
                
                for sub_task in plan['sub_tasks']:
                    addn_questions.append(plan['sub_tasks'][sub_task]['content'])
                    agent_name = plan['sub_tasks'][sub_task]['agent']
                    agent_role = plan['sub_tasks'][sub_task]['agent_role_description']
                    local_constraints = plan['sub_tasks'][sub_task]['local_constraints']
                    task = plan['sub_tasks'][sub_task]['content']
                    dependencies = plan['sub_tasks'][sub_task]['require_data']
                    tools_list = plan['sub_tasks'][sub_task]['tools']
                    print(f'processing {agent_name}')
                    agent = Agent(sub_task, agent_name, agent_role, local_constraints, task,dependencies, tools_list, agent_state)
                    agentsList.append(agent)
                
                # Execute the task results using the Smack agent
                smack = Smack(agentsList)
                taskResultsDict = smack.executeSmack()
                for task in taskResultsDict:
                    out_str += f'{taskResultsDict[task]} \n'
                resp = drafterAgent_rag(query,rag_context, out_str)
                resp = re.sub(r'\\\[(.*?)\\\]', lambda m: f'$${m.group(1)}$$', resp, flags=re.DOTALL)
                resp = generate_chart(resp)
                '''additionalQuestions = []
                for que in addn_questions:
                    finQue = await genQuestionComplex(query, addn_questions)
                    additionalQuestions.append(finQue)'''
                additionalQuestions = await genQuestionSimple(addn_questions)

                    
                with open ('./output/drafted_response.md', 'w') as f:
                    f.write(str(resp))

            elif query_type == 'simple':
                print("========================")
                print(query_type)
                print("========================")
                print("RUNNING SIMPLE TASK PIPELINE")   
                resp = rag_context
                resp = re.sub(r'\\\[(.*?)\\\]', lambda m: f'$${m.group(1)}$$', resp, flags=re.DOTALL)
                additionalQuestions = await genQuestionSimple(query)
                
        await asyncio.sleep(1)
        await websocket.send(json.dumps({"type": "response", "response": resp}))
        additionalQuestions = list(additionalQuestions)
        print("Additional Questions",additionalQuestions)
        await asyncio.sleep(1)
        await websocket.send(json.dumps({"type": "questions", "response": additionalQuestions[:3]}))

    else:
        for key in reasonings:
            resp += f'''**{key}**\n\n'''
            resp += f'''{reasonings[key]}\n\n'''
        with open("Bad_Question.md", "w") as f:
            f.write(resp)
        print(f'Total Time: {time.time()-now}')
        await asyncio.sleep(1)
        await websocket.send(json.dumps({"type": "response", "response": resp}))

async def handle_connection(websocket):
    """
    Manages incoming WebSocket connections and routes messages to the appropriate handlers.
    
    Args:
        websocket (WebSocket): The WebSocket connection to manage.
    
    Returns:
        None: The function processes messages asynchronously and sends back responses to the client.
    """
    rag = False
    async for message in websocket:
        data = json.loads(message)
        if data['type'] == 'query':
            print(f"Received query: {data['query']}")
            await mainBackend(data['query'], websocket, rag)

        if data['type'] == 'toggleRag':
            print(f"Received query: {data['query']}")
            rag = not rag

        if data['type'] == 'cred':
                print(f"Received credentials: {data['formData']}")
                env_file_path = '../.env'
                with open(env_file_path, 'r') as fp:
                    env_content = fp.readlines()

                env_dict = {}
                for line in env_content:
                    if line.strip() and not line.startswith('#'):
                        key, value = line.strip().split('=', 1)
                        value = value.strip('"')
                        env_dict[key] = value

                # Update the env_dict with new values from formData
                form_data = data['formData']
                for key, value in form_data.items():
                    if value:  # Only update if the value is not empty
                        if key in env_dict:
                            print(f"Updating API key for {key}")
                        else:
                            print(f"Adding new API key for {key}")
                        env_dict[key] = value

                # Write the updated environment variables back to the .env file
                with open(env_file_path, 'w') as fp:
                    for key, value in env_dict.items():
                        fp.write(f"{key}=\"{value}\"\n")

                print(".env file has been updated.")

async def main():
    """       
     Starts the WebSocket server and keeps it running indefinitely.
    """
    print("WebSocket server starting on ws://0.0.0.0:8080")
    async with websockets.serve(handle_connection, "localhost", 8080):
        await asyncio.Future()  # run forever


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nServer shutdown by user")