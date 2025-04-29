import google.generativeai as genai
import os
from openai import OpenAI
from dotenv import load_dotenv
load_dotenv('../../.env')
load_dotenv('../.env')

OPENAI_API_KEY = os.getenv('OPEN_AI_API_KEY_30')
print(OPENAI_API_KEY)
client = OpenAI(
    api_key=OPENAI_API_KEY
)

def classifierAgent(query):
    
    prompt = f'''
    INstructions:
    1. For every input, think about the task, reason it out.
    2. But DO NOT WRITE THE REASONING IN THE OUTPUT. This is just for your thought process.
    3. output should be a single word answer between 'simple' or 'complex'.

    A 'simple' query is a query in which the answer is concise and generating the answer does not require multiple agents.
    It might require multiple tools like web search, case law extractions etc, but the answer is a short answer or a paragraph or two.

    Questions like "Who am I?" or "What is the capital of France?", "What is the stock price of apple", "What was the judgement of a case" etc
    require brief answers. Hence they are classified as 'simple'.

    A 'complex' query is query in which the answer should be a long report covering multiple aspects of the query, it will
    require multiple agents, complex orchestration. 

    Questions like "Analyze the merger between 2 companies", "Compare and contrast 2 resumes", "What are the economic implications of an event",
    "Provide me case laws related to a particular topic", "Give a detailed report on something" etc are classified as 'complex'.

    Your task is to classify the given query as 'simple' or 'complex'. Give a single word answer between 'simple' and 'complex'.

    Following is the query
    {query}
    '''
    messages = [
        {"role": "system", "content": prompt},
    ]
    response = client.chat.completions.create(
        model='gpt-4o-mini', messages=messages, temperature=0
    )
    return response.choices[0].message.content

def classifierAgent_RAG(query, ragContext):
    prompt = f'''
    You are a classifier which determines if a question asks for a detailed response or a concise response.
    
    A query is detailed if it expects a long response, in form of a report and expects in depth analysis and reasoning.
    When a user expects a detailed response, they would mention some key words like "in depth", "deep analysis", "report",
    "long answer", "comprehensive report", "comprehensive analysis". OR it would ask for a multi-dimensional analysis of a topic.

    If the query has phrases like "analyze", "detailed analysis","in-depth analysis", "generate a report", "comprehensive analysis", "Evaluate comprehensively"
    or other phrases which indicate an in depth answer, return 'detailed'

    For example: 'How did the merger of Jio and Disney Plus Hotstar impact the Indian OTT market?' is a detailed query because it has
    to be analyzed from multiple standpoints and perspectives.

    A query which is not detailed is concise. Even if a query has complex jargons, concepts and numbers, then also it can be answered in a concise manner.
    For example: Questions about complex topics self attention, depreciating marginal returns etc can also be answered in a concise manner. 

    output should be a single word answer between 'concise' or 'detailed'.

    Following is the query:
    {query}
    '''
    messages = [
        {"role": "system", "content": prompt},
    ]
    response = client.chat.completions.create(
        model='gpt-4o-mini', messages=messages, temperature=0
    )
    cat_1 = response.choices[0].message.content.lower()

    if cat_1 == 'detailed':
        query2 = f'''''Does the following answer the query to it's fullest extent? Evaluate on the following metrics, only return yes when all metrics are fulfilled:
        a. Competion: Does the Answer contains answers to all aspects of the query?
        b. Detail: Does the Answer provide as much detail as asked in the query? If the query asks for a detailed or in-depth analysis, does the answer provide that level of deep analysis?

        query: {query}
        Answer: {ragContext}

        Answer only in 'yes' or 'no'
        '''
        
        messages = [
            {"role": "system", "content": query2},
        ]
        response = client.chat.completions.create(
            model='gpt-4o-mini', messages=messages, temperature=0
        )
        cat_2 = response.choices[0].message.content.lower()
        if cat_2 == 'yes':
            return 'simple'
        else:
            return 'complex' 
        
    else:
        return 'simple'
    
if __name__ == '__main__':
    queries = [
        'What is the difference between the Annual Incomes of Apple and Google',
        'What is the Difference between the Grades of Einstein and Tesla',
        #'Provide the evaluation metrics of attenton is all you need along with the outputs',
        #'Explain the Encoder-Decoder Mdodel of Transformers',
        #'Provide the Formula in latex for Scaled Dot-Product Attention and explain how it works',
        'What is Multi-Head attention and what are its applications',
        'Why is self attention important in transformers',
        #'What is the performance of Deep-Att + PosUnk, GNMT + RL, ConvS2S, Deep-Att + PosUnk Ensemble and Transformer (base model) on BLEU and Training Cost (FLOPs) performance metrics',
        "What are the impacts of merger of FlipKart and Walmart on the Indian Economy and Markets",
        "Analyze CoStar Group's and LoopNet's financial statements to identify potential areas of legal and financial risk associated with their overlapping business operations",
        'Compare the legal compliance records of Tegna and Standard Media Group regarding broadcasting regulations',
        #'Summarize the key terms and conditions of the merger agreement between Pfizer and Arena Pharmaceuticals, including payment structure and deal contingencies.',
        "Analyze the legal implications of data privacy regulations (GDPR, CCPA) on Google's business model.",
        "Determine the impact of the merger on the employment levels and compensation structures within Bank of America, using publicly available financial and SEC filings."
    ]

    for query in queries:
        print(classifierAgent_RAG(query, 'ragContext'), classifierAgent(query))
