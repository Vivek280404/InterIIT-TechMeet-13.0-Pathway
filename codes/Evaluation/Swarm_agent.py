""" 
This script evaluates the performance of a model by comparing its responses with a base model's responses.
"""
import pandas as pd
import os
import ast
import csv
from langchain_openai import ChatOpenAI
from swarm import Swarm, Agent
from dotenv import load_dotenv

load_dotenv('../.env')

def extract_csv_data(file_path):
    queries = []
    base_response = []
    gen_response = []

    try:
        with open(file_path, mode='r', newline='', encoding='utf-8') as file:
            csv_reader = csv.reader(file)
            next(csv_reader)  
            for row in csv_reader:
                queries.append(row[0]) 
                base_response.append(row[1])  
                gen_response.append(row[2])  
        
        return queries, base_response, gen_response
    
    except Exception as e:
        print(f"Error : {e}")

def extract_agent_tool_content(messages, output_file="agent_tool_content.txt"):
    with open(output_file, "a") as file:
        if hasattr(messages, "messages"):
            messages = messages.messages
        for message in messages:
            agent_name = message.get("sender", "Unknown Agent")
            tool_calls = message.get("tool_calls", [])
            content = message.get("content", "No Content")
            
            if tool_calls:
                for tool_call in tool_calls:
                    tool_name = tool_call.get("function", {}).get("name", "Unknown Tool")
                    file.write(f"Agent: {agent_name}\nTool Called: {tool_name}\nContent: {content}\n\n")
            else:
                # If no tool calls, just write the agent and content
                file.write(f"Agent: {agent_name}\nContent: {content}\n\n")
    return content
        
#mention the file path
file_path = ''  
queries, base_response, gen_response = extract_csv_data(file_path)

client = Swarm()

judge_prompt = '''
You are an unbiased moderator, who listens to both the experts impartially, DOES NOT PASS ANY JUDGEMENT ON ITS OWN and DECIDES IF BOTH THE EXPERTS ARE IN AGREEMENT OR NOT.
ONLY ALLOW 3 ROUNDS OF CONVERSATION BETWEEN THE EXPERTS.
'''

metric = '''
'metric1': Compare how well the response directly addresses the specific query, focusing on the alignment with the query's goals. Make sure that the response does not stray into unnecessary details that would not help in answering the query, and suitably punish such responses.
'metric2': Consider the logical reasoning, clarity of the writing and the logical flow of ideas. Focus on how well the ideas are connected across the response.
'metric3': This focuses on how well the response incorporates numerical data, including factual numbers, statistics, or quantitative analysis. Encourage more recent data and discredit vague answers without enough reasoning and numbers backing them by explicitly discouraging it.
'metric4': Evaluate how effectively the financial metrics support the report’s arguments and recommendations and comment on the incorporation of good market analysis practices.
'''

review_prompt = '''
You are an expert in the field of mergers and acquisitions, with extensive knowledge of corporate finance, strategic management, and market analysis.  Your task is to compare two responses (Response A and Response B) which are 
detailed reports in markdown format to a given query and review them based ONLY on the following four metrics without scoring:

'METRIC1': Compare how well the response directly addresses the specific query, focusing on the alignment with the query's goals. Make sure that the response does not stray into unnecessary details that would not help in answering the query, and suitably punish such responses.
'METRIC2': Consider the logical reasoning, clarity of the writing and the logical flow of ideas. Focus on how well the ideas are connected across the response.
'METRIC3': This focuses on how well the response incorporates numerical data, including factual numbers, statistics, or quantitative analysis. Encourage more recent data and discredit vague answers without enough reasoning and numbers backing them by explicitly discouraging it.
'METRIC4': Evaluate how effectively the financial metrics support the reports arguments and recommendations and comment on the incorporation of good market analysis practices.
Instructions:
mention your name
Compare and contrast with the reasoning of the previous experts (if available) and give reasoning on why you think they are incorrect or correct
Do not evaluate, simply review induvidually each metric for both responses and give proper explaining of what your thoughts are and its reasoning.
Try to understand the other experts analysis and improve on your own.
Structure your review by EXPLICITLY mentioning all metrics as 'metric1', 'metric2', 'metric3', 'metric4', etc.
'''

review_parser = '''
Return in  this json format
    {
    metric1 [
        {
        responseA: review,
        responseB: review,
        }
    ]
    metric2 [
        {
        responseA: review,
        responseB: review,
        }
    ]
    metric3 [ 
        {
        responseA: review,
        responseB: review,
        }
    ]
    metric4 [
        {
        responseA: review,
        responseB: review,
        }
    ]
    }
'''



grader_prompt = '''
You are a strict grader 
Evaluate the two responses based on the query, the final json review generated by the review parser, and assign a STRICT score for each response, based on the following table
1 - The response completely fails to address the metric. 
2 - The response only partially addresses the metric.
3 - The response adequately addresses the metric, but there is considerable room for improvement. 
4 - The response effectively addresses the metric with good quality, but it may lack perfection.
5 - The response fully addresses the metric with the highest level of quality.
and assign a score from 1 to 5 for both responseA and responseB.
Return the scores for each response as a list in the following format:[[score1_A, Score2_A, Score3_A, Score4_A],[Score1_B,Score2_B,Score3_B, Score4_B]] AND NOTHING ELSE.
'''

def transfer_to_expert1():
    return expert1

def transfer_to_expert2():
    return expert2


def transfer_to_parser():
    """If both the experts are in agreement then call this function"""
    return parser


moderator = Agent(
    name = "Moderator",
    instructions = judge_prompt,
    model = "gpt-4o-mini",
    functions = [transfer_to_expert1,transfer_to_expert2,transfer_to_parser],
    parallel_tool_calls=False
)

expert1 = Agent(
    name = "domain expert 1",
    instructions = review_prompt,
    model = "gpt-4o-mini"
)

expert2 = Agent(
    name = "domain expert 2",
    instructions = review_prompt,
    model = "gpt-4o-mini"
)

parser = Agent(
    name = "Review Agent",
    model = "gpt-4o-mini",
    instructions = f"You have to consider all the discussion that has happened and summarize it in a json format mentioned as below {review_parser}",
)

grader = Agent(
    name = "Grader Agent",
    model = "gpt-4o-mini",
    instructions = grader_prompt,
)


def evaluate_responses(idx,query, response_a, response_b):
    """ 
    Evaluate the responses based on the query, the final json review generated by the review parser, and assign a STRICT score for each response, based on the following table
    Args:
        query (str): The query
        response_a (str): The response A
        response_b (str): The response B
    Returns:
        list: The scores for each response as a list in the following format:[[score1_A, Score2_A, Score3_A, Score4_A],[Score1_B,Score2_B,Score3_B, Score4_B]]
    """
    prompt = (
    review_prompt  + 
    "Now, review the following:"
    f"query: {query}"
    f"Response A: {response_a}"
    f"Response B: {response_b}"
    )
    context = ""
    agent = moderator
    scores = client.run(
                agent = moderator,
                messages = [{"role":"user",
                             "content":f"the experts have come together to come up with this review of responses A and B against defined metrics"}]
            )
    while True:
        if (scores.agent.name == "Review Agent"):
            print(final)
            scores = client.run(
                agent = grader,
                messages = [{"role":"user",
                             "content":f"the experts have come together to come up with this review of responses A and B against defined metrics {metric} {final}"}]
            )
            final = extract_agent_tool_content(scores)
            break
        else:
            scores = client.run(
                agent = agent,
                messages = [{"role":"user",
                            "content":f"query: {query}, responseA: {response_a}, responseB: {response_b} {context}"}]
            )
            # print(scores)
            final = extract_agent_tool_content(scores)
            with open("agent_tool_content.txt","r") as f:
                context= f.read()
            if scores.agent.name == "Review Agent":
                # agent = grader
                print(final)
            print(scores.agent.name)
    
    print(final)
    score_list = ast.literal_eval(final)

    return score_list


with open('eval_results.csv', mode='a', newline='', encoding='utf-8') as file:
    csv_writer = csv.writer(file)
    
    file.seek(0, 2) 
    if file.tell() == 0:
        csv_writer.writerow(['Query', 'Base Response', 'Generated Response', 'Base Response Score', 'Generated Response Score'])

    for idx, query in enumerate(queries):
        gen_res = gen_response[idx]
        base_res = base_response[idx]

        score = evaluate_responses(idx,query, base_res, gen_res)
        print(score[0][2],score[1][2])
        
        base_response_score = (score[0][0] + score[0][1] + score[0][2] + score[0][3])*2
        gen_response_score =  (score[1][0] + score[1][1] + score[1][2] + score[1][3])*2

        csv_writer.writerow([query, base_res, gen_res, base_response_score, gen_response_score])

print("Evaluation results appended to eval_results.csv")    