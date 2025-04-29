import os
import json
from dotenv import load_dotenv
import time


load_dotenv('../../.env')
GOOGLE_API_KEY = os.getenv('GEMINI_API_KEY_30')
OPENAI_API_KEY = os.getenv('OPEN_AI_API_KEY_30')



import google.generativeai as genai

from langchain.globals import set_verbose
set_verbose(True)

from datetime import datetime
from LLMs import conversation_complex, GPT4o_mini_Complex



def clean(text):
    return text[text.index('{'):text.rfind('}')+1]


def plannerAgent(query):
    
    sys = f'''Note: The Current Date and Time is {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}. All your searches and responses
        must be with respect to this time frame.'''
    sys_prompt =  '''
    
    You are a task management assistant designed to break down tasks and manage task progress.

    While breaking down the main task into sub tasks, analyze from a multi-dimensional aspect, for instance interdependency
    between multiple domains like finance, microeconomics, macroeconomics, public policy, politics, law, environment etc,
    Large Scale considerations v/s Small Scale considerations, Long Term Considerations v/s Short Term Considerations etc. 
    For each of these domains like economics, public policy, finance, law, antitrust issues, management, consultancy, market 
    strategy etc, generate an individual agents which do intensive research on these specific topics, leveraging the tools provided. 

    Each subtask should only cover one domain/aspect of the problem, and only one entity related to the problem, hence there
    can be many subtasks for a complex problem, and single or low number of tasks for a unidimensional problem.
    
    You can use multiple tools for each task. The research crew of agents must be extensive to ensure in depth research.
    The main job in task breakdown is populating the JSON template below : 
    
    'json 

        {
        " main_task ": "..." , 
        " sub_tasks ": { 
        " task_1 ": {" content ": "..." , " agent ": "..." , "agent_role_description": "..." ," tools ": [...], " , " local_constraints ": [...] , " require_data ": [...]} ,
        " task_2 ": {" content ": "..." , " agent ": "..." , "agent_role_description": "..." ," tools ": [...], " local_constraints ": [...] , " require_data ": [...]}
        } 
        }
    '

    Before you design your task , you should understand what tools you have 
    , what each tool can do and cannot do. You must not design the subtask
    that do not have suitable tool to perform . Never design subtask that
    does not use any tool. Utilize specialized tools, like financial tools,
    legal tools etc over simple web search, but if no specialized tool usage is possible,
    then use the scrape or search tools.
     
    Based on user’s query , your main task is to gather valid information, create sub-tasks and synthesize agents which would execute these sub-tasks effectively. 
    
    You must first output the Chain of Thoughts ( COT ) . In the COT , you 
    need to explain how you break down the main task into sub - tasks and
    justify why each subtask can be completed by a singular agent which you synthesize. The sub - tasks
    need to be broken down to a very low granularity , hence it ’ s possible
    that some sub - tasks will depend on the execution results of previous
    tasks . You also need to specify which sub - tasks require the execution
    results of previous tasks . When writing about each sub - task , you must
    also write out its respective local constraints . Finally , you write
    the global constraint of the main task. While applying Chain of thought, think
    about related domains, topics and issues in order to take an interdisciplinary
    and holistic approach. 
    
    Try to maximize the number of independent tasks so that we can run them parallelly but
    where dependence from previous tasks is necessary, do add dependence.
    
    Before filling in the template , you must first understand the user ’ s 
    request , carefully analyzing the tasks contained within it . Once you
    have a clear understanding of the tasks , you determine the sequence in
    which each task should be executed . Following this sequence , you
    rewrite the tasks into complete descriptions , taking into account the
    dependencies between them.
    
    In the JSON template you will be filling , " main_task " is your main 
    task , which is gather valid information based on user ’ s
    query . " sub_task " is the sub - tasks that you would like to break down
    the task into . The number of subtasks in the JSON template can be
    adjusted based on the actual number of sub - tasks you want to break
    down the task into . The break down process of the sub - tasks must be
    simple with low granularity . There is no limit to the number of
    subtasks. 

    Each sub - tasks consist of either one or multiple step . It contains 6
    information to be filled in , which are " content " , " agent " , "agent_role_description", "tools"  , " require_data " and " data ".
    
    " require_data " is a list of previous sub - tasks which their information 
    is required by the current sub - task . Some sub - tasks require the
    information of previous sub - task . If that happens , you must fill in
    the list of " require_data " with the previous sub - tasks.

    Note: require_data should contain a list of task names like "task_1", "task_2"
    etc, and nothing else. Ensure that the strings match with the task names strictly. 
    
    " content " is the description of the subtask , formatted as string . When 
    generating the description of the subtask , please ensure that you add
    the name of the subtask on which this subtask depends . For example ,
    if the subtask depends on item A from the search result of task_1 , you
    should first write ’ Based on the item A searched in task_1 , ’ and then
    continue with the description of the subtask . It is important to
    indicate the names of the dependent subtasks .
    
    " agent " is the agent required for each step of execution . For each subtask there must
    only be one agent.Please use the original name of the agent synthesized.
    . This list cannot be empty . If you could not think of any agent to
    perform this sub - task , please do not write this sub - task.
    Examples of agents might include: Environmental Researcher, Macroeconomist, 
    Macroeconomist, Public Policy Researcher, ParaLegal Researcher, Financial Analyst,
    Quantitative Researches, Fundamental Researcher, Data Collection Agent, Data Interpreter,
    Market Researcher, General Researcher, Political Analyst, News Researcher, 
    Mergers Specialist, Acquisitions Specialist, Investment Banker etc. Note that this is not an exhaustive list and you can 
    make other agents on the same lines. 
    
    "agent_role_description" is the detailed job role  description of the agent and
    it's specializations which are required to solve the specific task. This is a 
    detailed string which describes what the agent is supposed to do and what output
    and specialization is expected from that agent.
    " tools " is the list of tools required for each step of execution . 
    Please use the original name of the tool without " functions ." in front. 
    This list cannot be empty . If you could not think of any tool to
    perform this sub - task , please do not write this sub - task.
    DO NOT add function arguments or parameters in front of the tool names. 
    The tool names must be the same as the name of the functions provided 
    and nothing else.

    After determining your subtasks , you must first identify the local 
    constraints for each sub - task , then the global constraints . Local
    constraints are constraints that needed to be considered in only in
    each specific sub - task.
    Please write the local constraints of each sub - task in its 
    corresponding " local_constraints " Local constraints of each sub - 
    task must be unique .
    When writing " local_constraints " , please write it as specific as 
    possible , as you should assume the agents of each task have no
    knowledge of the user ’ s query . You should also be aware local
    constraints filters the items individually , and some constraints can
    only be satisfied by multiple items .

    Never design subtask that uses tools which are beyond the functionality
    of LLMs or the tools defined. Also don't mention a tool not present in
    the tools list provided.

    You must output the JSON at the end .
    The Query is Given as follows:
    '''

    prompt = sys + sys_prompt + f"{query}"


    def load_json(file_path):
        try:
            with open(file_path, 'r') as file:
                data = json.load(file)  # Parse JSON into a Python dictionary or list
                return data
        except FileNotFoundError:
            print(f"Error: The file '{file_path}' was not found.")
            return None
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON: {e}")
            return None

    # Access specific information from the JSON
    def get_value_from_json(data, key):
        try:
            value = data.get(key)  # Fetch value associated with the key
            return value
        except AttributeError:
            print("Error: The JSON data is not a dictionary.")
            return None

    # Example usage
    file_path = 'Tools/info.json'  # Replace with your JSON file path
    json_data = load_json(file_path)


    tools_prompt = f'''
    The information about tools is encoded in a list of dictionaries, each dictionary having four keys: with 4 keys: first key being the 'name' where you enter the name of the function, second being 'docstring', where you fill the docstring of the function and third being 'parameters', fourth being output where you mention the output and output type. 
    NOTE that you can only use these tools and not anything apart from these. The names of the following tools are the only names valid for any of the tools. 
    The tools available to us are as follows:

    {json_data}

    '''
    prompt = prompt + tools_prompt

    response = GPT4o_mini_Complex.invoke(f'''{prompt}''').content
    dic =  json.loads(clean(response.split("```")[-2].split("json")[1]))


    with open('./Agents/plan.txt', 'w') as f:
        f.write(response)
    
    with open('./Agents/plan.json', 'w') as f:
        json.dump(dic, f)

    return dic



def plannerAgent_rag(query, ragContent):
    
    sys = f'''Note: The Current Date and Time is {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}. All your searches and responses
        must be with respect to this time frame.'''
    sys_prompt =  '''
    
    You are a task planning assistant designed to break down tasks and manage task progress based on a prompt and context from a document.

    While breaking down the main task into sub tasks, analyze from a multi-dimensional aspect, for instance interdependency
    between multiple domains like finance, microeconomics, macroeconomics, public policy, politics, law, environment etc,
    Large Scale considerations v/s Small Scale considerations, Long Term Considerations v/s Short Term Considerations etc. 
    For each of these domains like economics, public policy, finance, law, antitrust issues, management, consultancy, market 
    strategy etc, generate an individual agents which do intensive research on these specific topics, leveraging the tools provided.
    The agents have access to extensive documents relevant to the query encourage them to make as many queries as possible to retrieve_documents to get relevant context for answering the query. 
    The agents should focus HEAVILY ON extracting numbers from the context . Extract AS MANY NUMBERS as possible . Also the source provided to you should be mentioned EXPLICITLY.
    Your Job is to extract as much relevant information from retrieve_documents .  Make sure to extract information from tables as much as you can. Basically you have lots of information waiting to be extracted from the document do it. Its a treasure trove of information 


    The task divison should be very specific to the context. Following is the context:

    =======================================================
    {ragContent}
    =======================================================

    
    
    You can use multiple tools for each task. The research crew of agents must be extensive to ensure in depth research.
    The main job in task breakdown is populating the JSON template below : 
    
    'json 

        {
        " main_task ": "..." , 
        " sub_tasks ": { 
        " task_1 ": {" content ": "..." , " agent ": "..." , "agent_role_description": "..." ," tools ": [...], " , " local_constraints ": [...] , " require_data ": [...]} ,
        " task_2 ": {" content ": "..." , " agent ": "..." , "agent_role_description": "..." ," tools ": [...], " local_constraints ": [...] , " require_data ": [...]}
        } 
        }
    '

    Before you design your task , you should understand what tools you have 
    , what each tool can do and cannot do. You must not design the subtask
    that do not have suitable tool to perform . Never design subtask that
    does not use any tool. Utilize specialized tools, like financial tools,
    legal tools etc over simple web search, but if no specialized tool usage is possible,
    then use the scrape or search tools.
     
    Try to minimize the number of tasks, but make at least 3 tasks.
    
    In the JSON template you will be filling , " main_task " is your main 
    task , which is gather valid information based on user ’ s
    query . " sub_task " is the sub - tasks that you would like to break down
    the task into . 

    Each sub - tasks consist of either one or multiple step . It contains 6
    information to be filled in , which are " content " , " agent " , "agent_role_description", "tools"  , " require_data " and " data ".
    
    "require_data " is a list of previous sub - tasks which their information 
    is required by the current sub - task . Some sub - tasks require the
    information of previous sub - task . If that happens , you must fill in
    the list of " require_data " with the previous sub - tasks.

    Note: require_data should contain a list of task names like "task_1", "task_2"
    etc, and nothing else. Ensure that the strings match with the task names strictly. 
    
    " content " is the description of the subtask , formatted as string.
    
    " agent " is the agent required for each step of execution . For each subtask there must
    only be one agent.Please use the original name of the agent synthesized.
    . This list cannot be empty . If you could not think of any agent to
    perform this sub - task , please do not write this sub - task.
    
    "agent_role_description" is the detailed job role  description of the agent and
    it's specializations which are required to solve the specific task. 
    
    " tools " is the list of tools required for each step of execution . 
    Please use the original name of the tool without " functions ." in front. 
    
    DO NOT add function arguments or parameters in front of the tool names. 
    The tool names must be the same as the name of the functions provided 
    and nothing else.

    After determining your subtasks , you must first identify the local 
    constraints for each sub - task. Local
    constraints are constraints that needed to be considered in only in
    each specific sub - task.
    Please write the local constraints of each sub - task in its 
    corresponding " local_constraints " Local constraints of each sub - 
    task must be unique .
    When writing " local_constraints " ,

    Never design subtask that uses tools which are beyond the functionality
    of LLMs or the tools defined. Also don't mention a tool not present in
    the tools list provided.

    You must output the JSON at the end .
    The Query is Given as follows:
    '''

    prompt = sys + sys_prompt + f"{query}"


    def load_json(file_path):
        try:
            with open(file_path, 'r') as file:
                data = json.load(file)  # Parse JSON into a Python dictionary or list
                return data
        except FileNotFoundError:
            print(f"Error: The file '{file_path}' was not found.")
            return None
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON: {e}")
            return None

    # Access specific information from the JSON
    def get_value_from_json(data, key):
        try:
            value = data.get(key)  # Fetch value associated with the key
            return value
        except AttributeError:
            print("Error: The JSON data is not a dictionary.")
            return None

    # Example usage
    file_path = 'Tools/info.json'  # Replace with your JSON file path
    json_data = load_json(file_path)


    tools_prompt = f'''
    The information about tools is encoded in a list of dictionaries, each dictionary having four keys: with 4 keys: first key being the 'name' where you enter the name of the function, second being 'docstring', where you fill the docstring of the function and third being 'parameters', fourth being output where you mention the output and output type. 
    NOTE that you can only use these tools and not anything apart from these. The names of the following tools are the only names valid for any of the tools. 
    The tools available to us are as follows:

    {json_data}

    '''
    prompt = prompt + tools_prompt

    response = GPT4o_mini_Complex.invoke(f'''{prompt}''').content
    dic =  json.loads(clean(response.split("```")[-2].split("json")[1]))


    with open('./Agents/plan.txt', 'w') as f:
        f.write(response)
    
    with open('./Agents/plan.json', 'w') as f:
        json.dump(dic, f)

    return dic




if __name__ == "__main__":
    start = time.time()
    query = 'Analyze the impact of US-China trade wars on multiple financial assets'
    out = plannerAgent(query)
    print("Complete")
    print(f"Time for planning: {time.time()-start}")