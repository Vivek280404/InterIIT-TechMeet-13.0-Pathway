import os
import json
from dotenv import load_dotenv
import time
load_dotenv('../../.env')

from datetime import datetime
import google.generativeai as genai

from langchain.globals import set_verbose
set_verbose(True)

from Agents.LATS.NewTools import *

from LLMs import conversation_complex, GPT4o_mini_Complex



def clean(text):
    return text[text.index('{'):text.rfind('}')+1]


def ragAgent(query, state):
    fin_context = ''''''
    
    if state == "report":
        rag_result = retrieve_documents.invoke(query)
        fin_context += f'{rag_result} \n'
        sys_prompt =  '''
        Extract the Key Words, Jargons and Important Concepts from the information given below and make queries for further research:
        {
            "query_1": "...",
            "query_2": "...",
            "query_3": "..."
        }
        Following is the information to be used:
        \n
        '''
        rag_result_str = ''
        if type(rag_result) is list:
            for i in rag_result:
                if type(i) is str:
                    rag_result_str += i
                elif type(i) is str:
                    rag_result_str += f"{i['url']}+{i['content']}"
        elif type(rag_result) is str:
            rag_result_str = rag_result
        else:
            print(type(rag_result))
            

        prompt = f"""Note: The Current Date and Time is {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}. All your searches and responses must be with respect to this time frame""" + sys_prompt + rag_result_str
        response = GPT4o_mini_Complex.invoke(f'''{prompt}''').content

        dic =  dict(json.loads(clean(response.split("```")[-2].split("json")[1])))
        for p in dic:
            rag_resp = retrieve_documents.invoke(dic[p])
            fin_context += f'{rag_resp} \n'

        """prompt_2 =  f'''
        Note: The Current Date and Time is {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}. All your searches and responses
        must be with respect to this time frame
        
        Based on the given main query, 3 sub-queries, and given context, conduct intensive research from 
        a multi-domain perspective (such as finance, economics, law, market research, consumer research, compliance etc)
        and generate a comprehensive answer to the main query.
        The main query is: {query}
        The sub-queries are: {dic}
        The context is: 
        {fin_context}
        The answer should be backed by all the facts gathered and research conducted, hence the answer should be extremely detailed.
        \n
        '''

        fin_response = GPT4o_mini_Complex.invoke(f'''{prompt_2}''').content"""


        return fin_context
        
    elif state == "concise":
        print("Hello This is concise")
        #return json.dumps(simple_query_documents.invoke(query))
        resp = simple_query_documents.invoke(query)
        if type(resp) == str:
            return resp
        elif type(resp) == dict:
            return resp['answer']

