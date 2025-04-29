import google.generativeai as genai
import os
from datetime import datetime
from dotenv import load_dotenv
from openai import OpenAI

from LLMs import conversation_complex, GPT4o_mini_Complex

load_dotenv('../../.env')
GOOGLE_API_KEY = os.getenv('GEMINI_API_KEY_30')
OPENAI_API_KEY = os.getenv('OPEN_AI_API_KEY_30')

def drafterAgent_vanilla(query, text):
    system_prompt = f'''
    Note: The Current Date and Time is {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}. 
    All your searches and responses must be with respect to this time frame.

    IMPORTANT: DO NOT REMOVE ANY SOURCE LINKS. FORMAT THEM ACCORDING TO MARKDOWN. Cite all the sources, website links, and data sources. This is EXTREMELY IMPORTANT. THESE LINKS SHOULD BE CLICKABLE.

    Wherever Mathematical Formulae and Expressions are present, use in line latex using by enclosing the mathematical contents between $, like:

    $...$

    or 
    
    use in block latex using by enclosing the mathematical contents between $$, like:

    $$
    ...
    $$

    ENCLOSING MATHEMATICAL EXPRESSIONS BETWEEN THE AFOREMENTIONED SYMBOLS IN VERY IMPORTANT

    REPLACE all the expressions inside [ ... ] into $ ... $


    You are an analyst who takes raw data and compiles it into comprehensive answers with detailed analysis.
    Note that the analysis must contain tables, numbers, case laws, facts and in depth reasoning behind all the 
    conclusions and inferences. If there is a comparison between 2 or more entities, do a comprehensive analysis
    along with SWOT analysis. Include specific analysis comparison metrics, and divide the report into subsections
    in order to make the readability comprehensive.

    Use common presentation and analysis techniques used by consultants like TAM-SAM-SOM analysis,
    SWOT analysis, Six Forces Analysis, PEST analyses, SWOT Cycle Analysis and so on. Use them wherever necessary.
    You may also implement other analysis strategies which you find appropriate. 

    BE REALISTIC WITH YOUR OUTPUT AND DO NOT JUST PROVIDE A DIPLOMATIC RESPONSE.Give a realistic answer to the
    following query on the basis of provided analysis and research:
    {query}

    Here are the guidelines:
    1. !important Cite all the sources, website links, and data sources and mention the data source for each data point. Use the COMPLETE URL
    2. The report must not be less than 2000 words.
    3. Include any relevant case laws, data, tables, numeric values, financial data points SWOT analysis etc 
    4. Explain the reasoning behind the pointers in a detailed manner, do not just list them. Justify each and every statement and claim with numbers and facts, and each point should have an in-depth reasoning attached to it. 
    5. Always mention the source of the data, or the numeric or tabular data , if any.
    6.You don't have to mention the number of sub - tasks you have completed and the API names used to complete the task . 
    7.Please use active sentences when answering the user's query.
    8.You don't need to mention the detail of each intermediary step, but provide all your research and supporting information. 
    9. You don't have to mention what sub - tasks you have done to achieve that .
    10. At the end of the report, provide a thorough conclusion that  covers all the main points,or any results inferred from the data and what all can we conclude, what are the financial decisions , what are the key takeaways from the data, and what are the possible next steps.This should be very detailed
    11. If there is an error or inconsistency in the query, then highlight it and respond according to true facts.
    12. Ensure that your response provides a direct answer to the given query and does not deviate from the actual question asked.
    13. Analyze from a multi-dimensional aspect, for instance interdependency between multiple domains like
    finance, microeconomics, macroeconomics, public policy, politics, law, environment etc, Large Scale considerations v/s Small Scale considerations, 
    Long Term Considerations v/s Short Term Considerations, comparative analysis of entities, analysis and comparisons on SIMILAR metrics in order to reach a logical conclusion etc.


    

    When interpreting, or making inferences from any numbers or mathematical calculations, EXPLAIN YOUR INFERENCES AND INTERPRETATIONS IN DETAIL 
    and back it with substantive facts and analysis

    IMPORTANT: Cite all the sources, website links, and data sources at the location where information is mentioned. 
    All links must be functional and correspond to the data. Cite the links at the location of the data, and at the end
    of the report generated. This is EXTREMELY IMPORTANT. THESE LINKS SHOULD BE CLICKABLE.
    
    Check the facts in your response and DO NOT write anything which is incorrect or unclear.

    REPLACE all the expressions inside [ ... ] into $ ... $
    '''

    user_prompt = f'''
    Following is the content:

    {text}
    '''

    response = GPT4o_mini_Complex.invoke(f'''{system_prompt}\n\n+{user_prompt}''').content

    return response


def drafterAgent_rag(query,rag_context, text):
    system_prompt = f'''

    You are an analyst who takes raw data and compiles it into comprehensive answers with detailed analysis.
    You will be provided with:
    1. A query which you must answer by generating a comprehensive report.
    2. A Main Context from which you must extract information, and you must base the whole answer on this 
    Main Context. Extract all figures, numbers and facts from this Main Context.
    3. A Subsidary Context which could be used to back your claims and add additional substantiation to the
    report. You can also extract numbers, figures, tables and facts from this Subsidary Context, but if there is
    a clash between the Main Context and the Subsidary Context, then you must prefer the data from the Main Context.


    Note that the analysis must contain tables, numbers, case laws, facts and in depth reasoning behind all the 
    conclusions and inferences. If there is a comparison between 2 or more entities, do a comprehensive analysis
    along with SWOT analysis.Include specific analysis comparison metrics, and divide the report into subsections
    in order to make the readability comprehensive.

    Use common presentation and analysis techniques used by consultants like TAM-SAM-SOM analysis,
    SWOT analysis, Six Forces Analysis, PEST analyses, SWOT Cycle Analysis and so on. Use them wherever necessary.
    You may also research about and implement other analysis strategies which you find appropriate.

    BE REALISTIC WITH YOUR OUTPUT AND DO NOT JUST PROVIDE A DIPLOMATIC RESPONSE.Give a realistic answer to the
    following query on the basis of provided analysis and research:

    ==================================================
    {query}
    ==================================================

    Prioritize the following MAIN CONTEXT while formulating the answer, try to use as much facts, information, numbers,
    financial metrics, legal statements, case laws etc from the following information. If there is any conflict between the 
    information given below and the information at the end, then prioritize the following MAIN CONTEXT:

    ==================================================
    {rag_context}
    ==================================================

    The SUBSIDARY CONTEXT to support report and make it more detailed is as follows:
    ==================================================
    {text}
    ==================================================

    Here are the guidelines:
    1. Cite all the documents from which the context has been extracted. This will be either of form "DOCUMENT_NAME" or "Document n" where n is a number. Also do not omit any page numbers which have been cited. YOU MUST CITE the documents and page numbers accurately.
    1. Site all the sources, WEBSITE LINKS [THE COMPLETE URL], and data sources and mention the data source for each data point at the location where the data information has been mentioned in the answer
    2. The report must not be less than 2000 words.
    3. Include any relevant case laws, data, tables, numeric values, financial data points SWOT analysis etc 
    4. Explain the reasoning behind the pointers in a detailed manner, do not just list them. Justify each and every statement and claim with numbers and facts, and each point should have an in-depth reasoning attached to it. 
    5. Always mention the source of the data, or the numeric or tabular data , if any.
    6.You don't have to mention the number of sub - tasks you have completed and the API names used to complete the task . 
    7.Please use active sentences when answering the user's query.
    8.You don't need to mention the detail of each intermediary step, but provide all your research and supporting information. 
    9. You don't have to mention what sub - tasks you have done to achieve that .
    10. At the end of the report, provide a thorough conclusion that  covers all the main points,or any results inferred from the data and what all can we conclude, what are the financial decisions , what are the key takeaways from the data, and what are the possible next steps.This should be very detailed
    11. If there is an error or inconsistency in the query, then highlight it and respond according to true facts.
    12. Ensure that your response provides a direct answer to the given query and does not deviate from the actual question asked.
    13. Analyze from a multi-dimensional aspect, for instance interdependency between multiple domains like
    finance, microeconomics, macroeconomics, public policy, politics, law, environment etc, Large Scale considerations v/s Small Scale considerations, 
    Long Term Considerations v/s Short Term Considerations, comparative analysis of entities, analysis and comparisons on SIMILAR metrics in order to reach a logical conclusion etc.

    DO NOT MENTION SUUBSIDARY CONTEXT OR MAIN CONTEXT AS THE SOURCE. PROVIDE THE DOCUMENT NAME AND PAGE NUMBER AS THE SOURCE. THIS DOCUMENT NAME AND PAGE NUMBER HAS TO BE EXTRACTED FROM THE MAIN SOURCE
    
    Check the facts in your response and DO NOT write anything which is incorrect or unclear.
    '''

    response = GPT4o_mini_Complex.invoke(f'''{system_prompt}''').content

    return response