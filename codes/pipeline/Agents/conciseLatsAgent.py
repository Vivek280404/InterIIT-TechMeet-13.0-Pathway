from Agents.LATS.Solve_subquery import SolveSubQuery
from langchain_openai import ChatOpenAI
from openai import OpenAI

import os
import json
from dotenv import load_dotenv
from datetime import datetime

from LLMs import conversation_complex, GPT4o_mini_Complex

load_dotenv('../../.env')
GOOGLE_API_KEY = os.getenv('GEMINI_API_KEY_30')
OPENAI_API_KEY = os.getenv('OPEN_AI_API_KEY_30')

def drafterAgentSimplified(text, query):
    system_prompt = f'''
    Your ultimate task is to give a comprehensive answer to the query:{query}
    Judge the length of the response on the basis of the query and generate the response accordingly.
    '''
    user_prompt = f'''
    Following is the content:
    {text}
        '''
    prompt = f'''{system_prompt}\n\n {user_prompt}'''
    '''client = OpenAI(api_key=OPENAI_API_KEY)
    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {
                "role": "user",
                "content": f"{user_prompt}"
            }
        ]
    )
    response = completion.choices[0].message.content.strip()'''

    response = conversation_complex.run(f'''{prompt}''')
    
    return response

def conciseAns_vanilla_LATS(query, tools_list):
    print("RUNNING conciseAns_vanilla_LATS")
    CombinedResearch = [SolveSubQuery(query,tools=tools_list)]
    CombinedResearch_json = json.dumps(CombinedResearch,indent=2)
    fin_resp = drafterAgentSimplified(CombinedResearch_json,query)
    with open("conciseResponse_LATS.md", "w") as f1:
        f1.write(fin_resp)
    print("COMPLETED conciseAns_vanilla_LATS")
    return fin_resp