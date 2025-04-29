""" 
This script evaluates the performance of a model by comparing its responses with a base model's responses. 
The evaluation is conducted based on a predefined metrics schema, and the responses are judged by a judge agent, expert agents, and a grader agent. 
The evaluation results are saved to a CSV file for further analysis.
"""
import pandas as pd
import os
import ast
import csv
from langchain.prompts import ChatPromptTemplate
from langchain.schema import HumanMessage
from langchain_community.chat_models import ChatOpenAI  
from langchain_community.callbacks import get_openai_callback
from dotenv import load_dotenv

load_dotenv('../.env')

# Mention the dataset csv filepath
file_path = ''

# Read CSV data
def extract_csv_data(file_path):
    queries, base_response, gen_response = [], [], []
    try:
        with open(file_path, mode='r', newline='', encoding='utf-8') as file:
            csv_reader = csv.reader(file)
            next(csv_reader)  # Skip header row
            for row in csv_reader:
                queries.append(row[0]) 
                base_response.append(row[1])  
                gen_response.append(row[2])  
    except Exception as e:
        print(f"Error reading CSV: {e}")
    return queries, base_response, gen_response



judge_prompt = ChatPromptTemplate.from_template("""
You are an IMPARTIAL and RIGOROUS judge tasked with synthesizing each expert's reviews for a given query.  
Each EXPERT AGENT specializes in domains such as Mergers and Acquisitions and Legal practice. Their role is to objectively compare two responses, Response A and Response B, based on the predefined metrics schema.  

Your duties are as follows:  
1. Thoroughly analyze the query and the detailed reviews provided by the experts in line with the established metrics schema.  
2. Independently evaluate Response A and Response B prior to expert reviews. Rigorously compare the responses with each other and deliver an unbiased judgment for each metric schema. Ensure no favoritism or undue preference affects your assessment.  
3. Summarize the judgment with clear and transparent reasoning for each metric, and forward it to a grader agent for quantitative scoring of each metric element.  

Proceed with the review process:  
Query: {query}  
Expert A Review : {review1}  
Expert B Review : {review2}  
""")

expert_prompt = ChatPromptTemplate.from_template("""
You are a HIGHLY SKILLED expert in domains such as Mergers and Acquisitions and Legal practices.  
Your assignment is to OBJECTIVELY COMPARE the following two responses, Response A and Response B, based on the detailed metrics schema outlined below:  

**'Relevance':** Evaluate how directly and effectively the response addresses the specific query, ensuring alignment with the query's objectives. Responses deviating into irrelevant or unnecessary details must be penalized appropriately.  
**'Logical Coherence':** Assess the clarity, coherence, and logical progression of the arguments presented. Emphasize the interconnection of ideas and penalize disorganized reasoning.  
**'Quantitative Rigor':** Scrutinize the inclusion and accuracy of numerical data, such as statistics or quantitative analysis. Reward precise and up-to-date data while harshly penalizing vague, unsupported, or outdated information.  
**'Analytical Depth':** Examine the depth of financial or market analysis supporting the arguments. Ensure robust incorporation of metrics and effective evaluation of financial trends or legal frameworks.  

**Instructions:**  
Carefully compare and contrast the responses based on the above metrics. For each metric, provide a detailed comparison explaining your reasoning in a fair and unbiased manner. Avoid evaluating or assigning scores—simply provide a thorough comparison with reasoned explanations.  

Query: {query}  
Response A: {response_a}  
Response B: {response_b}  
""")


grader_prompt = ChatPromptTemplate.from_template("""
You are a STRICT and UNCOMPROMISING GRADER Agent. Using the judgments provided by the judge and the context of the query, assign scores for each metric for both responses based on the following criteria:  

**'Relevance':** Judge how well the response aligns with the query's goals. Responses that include extraneous details or fail to directly address the query must be penalized.  
**'Logical Coherence':** Evaluate the clarity, logical flow, and coherence of the response. Disorganized or unclear arguments must be penalized heavily.  
**'Quantitative Rigor':** Assess the quality and relevance of numerical evidence, including statistics and quantitative insights. Heavily penalize vague or unsupported claims.  
**'Analytical Depth':** Critically evaluate the incorporation of financial or market analysis in supporting the arguments. Penalize shallow or superficial evaluations.  

**Evaluation Format:** Assign scores STRICTLY from 1 to 5 for each response based on the following scale:  
1 - Completely fails to address the metric.  
2 - Only partially addresses the metric.  
3 - Adequately addresses the metric, but with considerable room for improvement.  
4 - Effectively addresses the metric with good quality but lacks perfection.  
5 - Fully addresses the metric with the highest level of quality.  

**Return Format:** Only provide scores in this strict format:  
[[score1_A, score2_A, score3_A, score4_A], [score1_B, score2_B, score3_B, score4_B]]  

**Note:** Return only the scores in this exact format. Ensure all judgments remain OBJECTIVE, RIGOROUS, and UNBIASED.  

Judge Reviews: {judge_reviews}  
""")


# Model setup
judge_model = ChatOpenAI(temperature=0, model="gpt-4o-mini")
expert_model = ChatOpenAI(temperature=0, model="gpt-4o-mini")
grader_model = ChatOpenAI(temperature=0, model="gpt-4o-mini")

# Evaluation workflow
def evaluate_responses(query, our_response, base_response):
    
    expert1_message = expert_prompt.format(query=query, response_a=our_response, response_b=base_response)
    expert1_review = expert_model.invoke([HumanMessage(content=expert1_message)]).content
    print(f"expert1 response: {expert1_review}\n\n")

    expert2_message = expert_prompt.format(query=query, response_a=our_response, response_b=base_response)
    expert2_review = expert_model.invoke([HumanMessage(content=expert2_message)]).content
    print(f"expert2 response: {expert2_review}\n\n")

        
    judge_message = judge_prompt.format(query=query, review1=expert1_review, review2=expert2_review)
    judge_response = judge_model.invoke([HumanMessage(content=judge_message)])
    print(f"Judge response: {judge_response}\n\n")
        
    # Step 3: Grader evaluates
    grader_message = grader_prompt.format(judge_reviews=judge_response)
    grader_response = grader_model.invoke([HumanMessage(content=grader_message)]).content
    print(f"grader response: {grader_response}\n\n") 
        
    # Parse grader's response
    try:
        scores = ast.literal_eval(grader_response)
    except Exception as e:
        print(f"Error parsing grader response: {e}")
        scores = [[0, 0, 0, 0], [0, 0, 0, 0]]
    return scores

# Main execution

queries, our_response, base_response = extract_csv_data(file_path)

with open('eval_results.csv', mode='a', newline='', encoding='utf-8') as file:
    csv_writer = csv.writer(file)
    if file.tell() == 0:  # Write header if empty
        csv_writer.writerow(['Query', 'Our Response', 'Base Response', 'Our Response Score', 'Base Response Score'])

    for query, our_res, base_res in zip(queries, our_response, base_response):
        scores = evaluate_responses(query, our_res, base_res)
        print(f"Our model scores : {scores[0]} \nChatGpt scores : {scores[1]} \n")
        base_score = sum(scores[0]) * 2
        gen_score = sum(scores[1]) * 2
        csv_writer.writerow([query, our_res, base_res, base_score, gen_score])  
print("Evaluation results appended to langchain_eval_results.csv")
