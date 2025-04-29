"""
 This file contains list of all tools that can be used by the agents. 
"""
from typing import Type , Dict , List , Union, Tuple, Callable, Any, Optional, Annotated
from pydantic import BaseModel, Field
import wikipedia
import requests
import google.generativeai as genai
from langchain_google_community import GoogleSearchAPIWrapper
import json
import re
import finnhub
from functools import wraps
import random
from datetime import datetime
from collections import defaultdict
from dotenv import load_dotenv
import yfinance as yf
from pandas import DataFrame
import dotenv
import logging
from langchain_experimental.utilities import PythonREPL
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from bs4 import BeautifulSoup
import base64
import os.path
import praw
import http.server
import socketserver
from langchain.tools import BaseTool, tool
import time
from edgar import *
from edgar import Company
import time
import urllib.parse 
from langchain.tools import Tool
from langchain.llms import OpenAI
from langchain.agents import initialize_agent, AgentType
from typing import Dict

ERROR_LOG_FILE = "./error_logs.log"
load_dotenv('.env')

# Step 1: Create a logger
logger = logging.getLogger('my_logger')
file_Handler = logging.FileHandler(ERROR_LOG_FILE)
logger.setLevel(logging.DEBUG)  # Set the base logging level
file_Handler.setLevel(logging.ERROR)  # Set the handler logging level
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger.addHandler(file_Handler)
def log_error(tool_name, error_message, additional_info=None):
    error_entry = {
        "tool" : tool_name,
        "error_message" : error_message,
        "timestamp" : datetime.now().isoformat(),
        "additional info" : additional_info or {}
    }
    logger.error(json.dumps(error_entry, indent=4))


os.environ["GOOGLE_API_KEY"]= os.getenv('GEMINI_API_KEY_30')
os.environ["OPENAI_API_KEY"] = os.getenv('OPEN_AI_API_KEY_30')
os.environ["DISCORD_AUTH_KEY"] = os.getenv('DISCORD_AUTH_KEY')
os.environ["GOOGLE_CSE_ID"] =  os.getenv("GOOGLE_CSE_ID_30")
os.environ["TAVILY_API_KEY"] = os.getenv("TAVILY_API_KEY_30")
os.environ["GOOGLE_API_KEY"] = os.getenv("GOOGLE_API_KEY_30")
os.environ["reddit_client_id"]= os.getenv('reddit_client_id_30')
os.environ["reddit_client_secret"] = os.getenv('reddit_client_secret_30')
os.environ["reddit_user_agent"] = os.getenv('reddit_user_agent_30')
finnhub_client = finnhub.Client(api_key=os.getenv('FINNHUB_API_KEY_30'))

def clean_text(text):
    text = re.sub(r'http\S+|www\S+|https\S+', '', text)
    text = re.sub(r'[^a-zA-Z0-9\s.,!?\'"]', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text



# Initialize Tavily search tool once
from langchain_community.tools import TavilySearchResults

class MyCustomToolInput(BaseModel):
    """Input schema for MyCustomTool."""
    argument: str = Field(..., description="Description of the argument.")

class MyCustomTool(BaseTool):
    name: str = "Name of my tool"
    description: str = (
        "Clear description for what this tool is useful for, you agent will need this information to use it."
    )
    args_schema: Type[BaseModel] = MyCustomToolInput

    def _run(self, argument: str) -> str:
        # Implementation goes here
        return "this is an example of a tool output, ignore it and move along."
    

@tool
def web_scrape(url, query) -> Union[Dict, str]:
    """
    Use this to scrape a web page using links found using web search to give detailed response. Input should be the URL of the page to scrape.
    Returns the scraped data as JSON if successful, else move on to the next best site in case of errors like required login, captcha etc.
    Args:
        url (str): The URL of the page to scrape.
        query (str): The query for which the page is being scraped.
    Returns:
        Union[Dict, str]: The scraped data as JSON if successful
    """
    api_url = f'http://34.41.213.72:3000/{url}'
    headers = {
        'Accept': 'application/json',
        'X-Respond-With':'markdown',
        
    }
    output_folder = 'temp_rag_space'
    try:
        # Create output folder if it doesn't exist
        os.makedirs(output_folder, exist_ok=True)
        
        # Generate filename based on URL and timestamp
        filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        filepath = os.path.join(output_folder, filename)

        response = requests.get(api_url, headers=headers)
        response.raise_for_status()

        try:
            data = response.json()
            data_str = str(data)
        except ValueError:
            data_str = response.text
        finally:
            # Save the data to file
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(data_str)
            delay = 2
            time.sleep(delay)

            return query_documents.invoke({"prompt":query,"source":url})

    except requests.RequestException as e:
        log_error(
            tool_name="web_scrape",
            error_message=str(e),
            additional_info={"url": url}
        )
        return url

search = GoogleSearchAPIWrapper()
@tool
def web_search(query: str):
    """
    If you do not know about an entity, Perform web search using google search engine. 
    This should be followed by web scraping the most relevant page to get detailed response.
    Args:
        query (str): The query to search for.
    Returns:
        str: The URL of the most relevant page to scrape.
    """
    tavily_search = TavilySearchResults(
        max_results=2,
        search_depth="basic",
        include_answer=True,
        include_raw_content=False,
        include_images=False,
    )
    try:
        res = []
        search_results = tavily_search.invoke({"query": query})
        try:
            for search_result in search_results:
                url = search_result['url']
                content = search_result['content']
                res.append(web_scrape.invoke({"url": url, "query": query}))
            return res
        except Exception as e:
            # If both fail, return error message
            log_error(
                tool_name="tavily_web_search",
                error_message=str(e),
                additional_info={"query": query}
            )
            return search_results
    except Exception as e:
        # If both fail, return error message
        log_error(
            tool_name="tavily_web_search",
            error_message=str(e),
            additional_info={"query": query}
        )
        return ''

@tool
def web_search_simple(query: str):
    """
    If you do not know about an entity, Perform web search using google search engine.
    Args:
        query (str): The query to search for.
    Returns:
        str: The URL of the most relevant page to scrape.      
    """
    tavily_search = TavilySearchResults(
        max_results=3,
        search_depth="advanced",
        include_answer=True,
        include_raw_content=False,
        include_images=False,
    )
    
    try:
        search_results = tavily_search.invoke({"query": query})
        return search_results
            
    except Exception as e:
        # If both fail, return error message
        log_error(
            tool_name="tavily_web_search_simple",
            error_message=str(e),
            additional_info={"query": query}
        )
        return ''


@tool
def get_sec_filings(query:str,ticker: str, start_date: str, end_date: str, form: str) -> str:
    """
    Query SEC to retrieve any filings as required to find answers you generally find in filings. Filings published between start_date and end_date will be retrieved.

    Args:
        ticker (str): The symbol of the company.
        start_date (str): YYYY-MM-DD format 
        end_date (str): YYYY-MM-DD format
        form (str): form type like 10-K, 10-Q, 8-K, etc.

    Returns:
        str: SEC filing to be sent to RAG endpoint for retrieval.
    """
    company = ''
    try:
        company = Company(ticker)
        start_year = int(start_date[:4])
        end_year = int(end_date[:4])
        try:
            filing =  company.get_filings().filter(ticker = f"{ticker}",form = f"{form}",date = f"{start_date}:{end_date}")[0].markdown()
        except Exception as e:
            log_error(
                tool_name="get_sec_filings",
                error_message=str(e),
                additional_info={"ticker": ticker, "start_date": start_date, "end_date": end_date, "form": form}
            )
            return "This tool is not working right now. DO NOT CALL THIS TOOL AGAIN!"

        finally:
            if not filing:
                return web_search.invoke(f"SEC filings for {company} from {start_year} to {end_year}")
            output_folder = "temp_rag_space"
            filename = f"{ticker+datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            print(filename)
            filepath = os.path.join(output_folder, filename)
            with open(filepath,"w",encoding = "utf-8") as f:
                f.write(filing)
        
            delay = 2
            time.sleep(delay)
            return query_documents.invoke(query)

    except Exception as e:
        log_error(
            tool_name="get_sec_filings",
            error_message=str(e),
            additional_info={"ticker": ticker, "start_date": start_date, "end_date": end_date, "form": form}
        )
        return "This tool is not working right now. DO NOT CALL THIS TOOL AGAIN!"

@tool
def get_and_download_annual_report(query:str,ticker: str, financial_year: str) -> str:
    """
    Get the annual report URL and download the PDF for a given company ticker and financial year.
    
    Args:
        ticker (str): Company ticker symbol (e.g., 'RELIANCE')
        financial_year (str): Financial year (e.g., '2023')
    
    Returns:
        str: Path to the saved PDF file if successful, None otherwise
    """
    save_dir = "./kb_sec"
    os.makedirs(save_dir, exist_ok=True)
    url = f"https://www.screener.in/company/{ticker}/consolidated/"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        div = soup.find('div', class_='documents annual-reports flex-column')
        if div is None:
            return "No annual reports section found"
        
        a_tags = div.find_all('a')
        pdf_url = next((a.get('href') for a in a_tags if f'Financial Year {financial_year}' in a.get_text(strip=True)), None)
        
        if pdf_url is None:
            return f"No annual report found for {ticker} for FY {financial_year}"
        
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"}
        pdf_response = requests.get(pdf_url, stream=True, headers=headers)
        pdf_response.raise_for_status()
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{ticker}_FY{financial_year}_{timestamp}.pdf"
        filepath = os.path.join(save_dir, filename)
        
        with open(filepath, 'wb') as f:
            for chunk in pdf_response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
        delay = 2
        time.sleep(delay)
        return query_documents.invoke(query)
    
    except requests.RequestException as e:
        log_error("get_and_download_annual_report", str(e), {"ticker": ticker, "financial_year": financial_year})
        return "This tool is not working right now. DO NOT CALL THIS TOOL AGAIN!"
    except Exception as e:
        log_error("get_and_download_annual_report", str(e), {"ticker": ticker, "financial_year": financial_year})
        return "This tool is not working right now. DO NOT CALL THIS TOOL AGAIN!"

@tool
def break_query_into_subqueries(query: str) -> str:
    """
    Breaks down a complex query into simple subqueries.

    Args:
        query (str): The complex query to be broken down.

    Returns:
        str: The list of subqueries formatted in a point-wise manner.
    """
    # Configure the API key
    try:
        genai.configure()
        # Initialize the model
        model = genai.GenerativeModel('gemini-1.5-flash')
        # Prepare the prompt
        prompt = f'''You are someone who loves simple sentences, and solving problems one by one.
    Given a query, you will break it down into sub queries such that each query is a simple
    sentence asking exactly one thing. Don't infer questions, but break them down directly from the query.
    Generate this list of subqueries in a point wise manner in complete sentences. 
    Query: {query}

    Respond with a JSON object like this:
        
        {{
            "Query1": "QUERY", 
            "Query2": "QUERY",
                ......
            "QueryN": "QUERY", 
        }}

    Guidelines:
    1. Response Must not contain any starter/ending text or heading text.
    2. Do not include any json inside any punctuation.
    '''
        # Generate the response
        response = model.generate_content(prompt)
        response = json.loads(response.text)
        queries = list(response.values())
        return queries
    except Exception as e:
        log_error(
            tool_name="break_query_into_subqueries",
            error_message=str(e),
            additional_info={"query": query}
        )
        return "This tool is not working right now. DO NOT CALL THIS TOOL AGAIN!"
        
@tool
def get_ticker(company_name : str) -> str :
    """
    Get the annual report URL and download the PDF for a given company ticker and financial year.
    Args:
    company_name (str): Company name like Apple whose ticker is to be retrieved
    Returns:
    str: Ticker of the company
    """
    yfinance_url = "https://query2.finance.yahoo.com/v1/finance/search"
    user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36'
    params = {"q": company_name, "quotes_count": 1}
    
    res = requests.get(url=yfinance_url, params=params, headers={'User-Agent': user_agent})
    data = res.json()
    
    if 'quotes' in data and len(data['quotes']) > 0:
        company_code = data['quotes'][0]['symbol']
        return company_code
    else:
        return False

@tool
def get_indian_kanoon(query: str):
    """
    Retrieves Indian LEGAL data and CASE LAWs from Indian Kanoon based on the query

    Args:
        query (str): The legal query to search for.

    Returns:
        tuple: A tuple containing the title (str), date (str), and document text (str).
    """
    # Load environment variables
    dotenv.load_dotenv('../../../.env')

    INDIAN_KANOON_API_KEY = os.getenv('INDIAN_KANOON_API_KEY_30')

    try:
        search_url = f"https://api.indiankanoon.org/search/?formInput={query}&pagenum=0&maxcites=20"
        headers = {
            'Authorization': f'Token {INDIAN_KANOON_API_KEY}'
        }
        search_response = requests.post(search_url, headers=headers)
        search_result = search_response.json()

        # Retrieve the document ID
        doc_id = str(search_result['docs'][0]['tid'])
        doc_url = f"https://api.indiankanoon.org/doc/{doc_id}/"
        doc_response = requests.post(doc_url, headers=headers)
        doc_result = doc_response.json()

        # Extract title, date, and cleaned document text
        title = doc_result['title']
        date = doc_result['publishdate']
        doc = clean_text(doc_result['doc'])
        output_folder = "temp_rag_space"
        print(os.getcwd())
        os.makedirs(output_folder, exist_ok=True)        
        # Generate filename based on URL and timestamp
        filename = f"legal{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        filepath = os.path.join(output_folder, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(doc)

        delay = 2
        time.sleep(delay)
        source = 'Indian Kanoon'
        response_query_document = query_documents.invoke({"prompt":query,"source": source}) 
        if response_query_document == "This tool is not working right now. DO NOT CALL THIS TOOL AGAIN!":
            return doc
        else:
            return response_query_document

    except Exception as e:
        log_error(
            tool_name="get_Indian_kanoon",
            error_message=str(e),
            additional_info={"query": query}
        )
        return "This tool is not working right now. DO NOT CALL THIS TOOL AGAIN!"


@tool
def case_law(query: str) -> Tuple[str, str]:
    """
    Provides legal research for the given queries, for instance case laws, precedents, legal documents etc.
    Args:
        query (str): The search query for the case law.

    Returns:
        Tuple[str, str]: A tuple containing the links and descriptions from Tavily.
    """
    try:
        tavily_search = TavilySearchResults(
            max_results=3,
            search_depth="advanced",
            include_answer=True,
            include_raw_content=False,
            include_images=False,
        )
        modified_query = f"Laws and legal documents and related to {query}"
        search_results = tavily_search.invoke({"query": query})
        modified_query = f"Case laws, proceedings and precedents related to {query}"
        search_results += tavily_search.invoke({"query": query})
        return search_results
    except:
        return ''


@tool
def query_documents(prompt: str, source: str) -> Dict:
    """
    Query documents using a Retrieval-Augmented Generation (RAG) endpoint.
    This should be the first choice before doing web search,
    if this fails or returns unsatisfactory results, then use web search for the same query.
    Args:
        prompt (str): The prompt to send to the RAG endpoint.
        source (str): The source URL of the document.

    Returns:
        Dict: The JSON response from the RAG endpoint, containing the retrieved information and generated answer.
    """
    try:    
        print("Started")
        start = time.time()
        
        payload = {
            "query": prompt,  # No need to quote the prompt
            "source": source  # source should be a string, not a set
        }
        
        response = requests.post(
            "http://localhost:4005/generate",
            headers={"Content-Type": "application/json"},

            json=payload

        )
        
        print(f"Response status code: {response.status_code}")
        print("Posted")
        response.raise_for_status()  # Raise an error for HTTP issues
        print("Raised")
        
        end = time.time()
        print(f"Time taken: {end - start} seconds")
        
        result = response.json()
        print(result)
        return result
    
    except requests.RequestException as e:
        print(f"HTTP Request failed: {e}")
        if hasattr(e, 'response'):
            print(f"Response status code: {e.response.status_code}")
            print(f"Response content: {e.response.text}")
        log_error(
            tool_name="query_documents",
            error_message=str(e),
            additional_info={"prompt": prompt, "source": source}
        )
        return "This tool is not working right now. DO NOT CALL THIS TOOL AGAIN!"

@tool
def get_basic_financials_history(company: str, freq: str, start_date: str, end_date: str, selected_columns: list = None,query=None) -> dict:
    """
    Get historical basic financials for a company using Finnhub API.
    
    Args:
        company (str): The company's name
        freq (str): Reporting frequency ('annual' or 'quarterly')
        start_date (str): Start date in YYYY-MM-DD format
        end_date (str): End date in YYYY-MM-DD format
        selected_columns (list): List of specific financial metrics to return
        query (str): The original query that triggered this tool
        
    Returns:
        dict: Historical financial data for the company
    """
    try:
        symbol = get_ticker.invoke(company)
        if symbol:
            if freq not in ["annual", "quarterly"]:
                log_error(
                tool_name="get_basic_financial_history",
                error_message=f"error:Invalid reporting frequency {freq}. Please specify either 'annual' or 'quarterly'.",
                additional_info={"query": query}
                )
                return web_search_simple.invoke(f"Fetch the historical basic financials for {company} from {start_date} to {end_date}")

            else:       

                basic_financials = finnhub_client.company_basic_financials(symbol, "all")
                if not basic_financials["series"]:
                    log_error(
                    tool_name="get_basic_financial_history",
                    error_message=f"error:Failed to find basic financials for symbol {symbol} from finnhub!",
                    additional_info={"query": query}
                    )
                    return web_search_simple.invoke(f"Fetch the historical basic financials for {company} from {start_date} to {end_date}")
                
                else:
                    output_dict = defaultdict(dict)
                    for metric, value_list in basic_financials["series"][freq].items():
                        if selected_columns and metric not in selected_columns:
                            continue
                        for value in value_list:
                            if value["period"] >= start_date and value["period"] <= end_date:
                                output_dict[metric].update({value["period"]: value["v"]})

                    return dict(output_dict)
        else:
            return web_search_simple.invoke(f"Fetch the historical basic financials for {company} from {start_date} to {end_date}")
    
    except Exception as e:
        log_error(
            tool_name="get_basic_financials_history",
            error_message=str(e),
            additional_info={"query": symbol}
        )
        
        return web_search_simple.invoke(f"Fetch the historical basic financials for {company} from {start_date} to {end_date}")

@tool
def get_basic_financials(company: str, selected_columns: list = None):
    """
    Get latest basic financials for a company using Finnhub API.
    
    Args:
        company (str): The company's name
        selected_columns (list): List of specific financial metrics to return
        
    Returns:
        str: JSON string containing the latest financial metrics
    """
    try:
        symbol = get_ticker.invoke(company)
        if symbol:
            basic_financials = finnhub_client.company_basic_financials(symbol, "all")
            if not basic_financials["series"]:
                return web_search_simple.invoke(f"Get latest basic financials for {symbol}")
            else:
                output_dict = basic_financials["metric"]
                for metric, value_list in basic_financials["series"]["quarterly"].items():
                    value = value_list[0]
                    output_dict.update({metric: value["v"]})

                if selected_columns:
                    output_dict = {k: v for k, v in output_dict.items() if k in selected_columns}

                return json.dumps(output_dict, indent=2)
        else:
            return web_search_simple.invoke(f"What are the latest basic financials for {company}")
    
    except Exception as e:
        log_error(
            tool_name="get_basic_financials",
            error_message=str(e),
            additional_info={"query": symbol}
        )
        print("Invoking Fallback for get_basic_financials")
        return web_search_simple.invoke(f"What are the latest basic financials for {company}")

@tool
def get_stock_data(
    company: Annotated[str, "company name"],
    start_date: Annotated[str, "start date for retrieving stock price data, YYYY-mm-dd"],
    end_date: Annotated[str, "end date for retrieving stock price data, YYYY-mm-dd"]
):
    """
    Retrieve stock price data for designated company.
    Args:
        company (str): The company name.
        start_date (str): Start date in YYYY-MM-DD format.
        end_date (str): End date in YYYY-MM-DD format.
    Returns:
        DataFrame: Stock price data for the company.
    """
    try:
        symbol = get_ticker.invoke(company)
        if symbol:
            ticker = yf.Ticker(symbol)
            return ticker.history(start=start_date, end=end_date)
        else:
            return web_search_simple.invoke(f"What are the stock prices for {company}")
    except Exception as e:
        log_error(
            tool_name="get_stock_data",
            error_message=str(e),
            additional_info={"query": symbol}
        )
        return web_search_simple.invoke(f"What are the stock prices for {company}")

@tool
def get_stock_info(company: Annotated[str, "company name"]):
    """
    Get the Summary description, Employee count, Marketcap, Volume, P/E ratios, and Dividends for a company's stock
    Args:
        company (str): The company name.
    Returns:
        dict: The stock information.
    """
    try:
        symbol = get_ticker.invoke(company)
        if symbol:
            ticker = yf.Ticker(symbol)
            info = ticker.info 
            if info['trailingPegRatio'] is None:
                log_error(
                    tool_name="get_stock_info",
                    error_message="Empty DataFrame: Invalid symbol or no data available.",
                    additional_info={"query": symbol}
                )
                return "This tool is not working right now. DO NOT CALL THIS TOOL AGAIN!"
            else:
                return ticker.info
        else:
            return web_search_simple.invoke(f"Give the Summary description, Employee count, Marketcap, Volume, P/E ratios, and Dividends for {company}")
    except Exception as e:
        log_error(
            tool_name="get_stock_info",
            error_message=str(e),
            additional_info={"query": symbol}
        )
        return web_search_simple.invoke(f"Give the Summary description, Employee count, Marketcap, Volume, P/E ratios, and Dividends for {company}")


@tool
def get_company_info(company: Annotated[str, "company name"]):
    """
    Fetches and returns company information like Company Name, Industry, Sector, Country, Website
    Args:
        company (str): The company name.
    Returns:
        dict: The company information.
    """
    try:
        symbol = get_ticker.invoke(company)
        if symbol:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            if info['trailingPegRatio'] is None:
                log_error(
                    tool_name="get_company_info",
                    error_message="Empty DataFrame: Invalid symbol or no data available.",
                    additional_info={"query": symbol}
                )
                return web_search_simple.invoke(f"Give detailed company information for {symbol}")
            else:
                return {
                    "Company Name": info.get("shortName", "N/A"),
                    "Industry": info.get("industry", "N/A"),
                    "Sector": info.get("sector", "N/A"),
                    "Country": info.get("country", "N/A"),
                    "Website": info.get("website", "N/A"),
                }
        else:
            return web_search_simple.invoke(f"Give the Company Name, Industry, Sector, Country, Website for {company}")
    except Exception as e:
        log_error(
            tool_name="get_company_info",
            error_message=str(e),
            additional_info={"query": symbol}
        )
        return web_search_simple.invoke(f"Give the Company Name, Industry, Sector, Country, Website for {company}")
    


@tool
def get_stock_dividends(company: Annotated[str, "company name"]):
    """
    Fetches and returns the latest dividends data.
    Args:
        company (str): The company name.
    Returns:
        DataFrame: The dividends data.
    """
    try:
        symbol = get_ticker.invoke(company)
        if symbol:
            ticker = yf.Ticker(symbol)
            dividends = ticker.dividends
            if dividends.empty:
                log_error(
                    tool_name="get_stock_dividends",
                    error_message="Empty DataFrame: Invalid symbol or no data available.",
                    additional_info={"query": symbol}
                )
                return web_search_simple.invoke(f"What are the latest dividends for {symbol}")
                
            else:
                return dividends
        else:
            return web_search_simple.invoke(f"What are the latest dividends for {symbol}")
    except Exception as e:
        log_error(
            tool_name="get_stock_dividends",
            error_message=str(e),
            additional_info={"query": symbol}
        )
        return web_search_simple.invoke(f"What are the latest dividends for {symbol}")



@tool
def get_income_stmt(company: Annotated[str, "company name"]):
    """
    Fetches and returns the latest income statement of the company.
    Args:
        company (str): The company name.
    Returns:
        DataFrame: The income statement data.
    """
    try:
        symbol = get_ticker.invoke(company)
        if symbol:
            ticker = yf.Ticker(symbol)
            financials = ticker.financials
            
            if financials.empty:
                log_error(
                    tool_name="get_income_stmt",
                    error_message="Empty DataFrame: Invalid symbol or no data available.",
                    additional_info={"query": symbol}
                )
                return web_search_simple.invoke(f"Provide the latest income statement of {symbol}")
            else:
                return financials 
        else:
            return web_search_simple.invoke(f"Provide the latest income statement of {symbol}")
    except Exception as e:
        log_error(
            tool_name="get_income_stmt",
            error_message=str(e),
            additional_info={"query": symbol}
        )
        return web_search_simple.invoke(f"Provide the latest income statement of {symbol}")
    

@tool
def get_balance_sheet(company: Annotated[str, "company name"]):
    """
    Fetches and returns the latest balance sheet of the company.
    Args:
        company (str): The company name.
    Returns:
        DataFrame: The income statement data.
    """
    try:
        symbol = get_ticker.invoke(company)
        if symbol:
            ticker = yf.Ticker(symbol)
            balance_sheet = ticker.balance_sheet
            
            if balance_sheet.empty:
                log_error(
                    tool_name="get_balance_sheet",
                    error_message="Empty DataFrame: Symbol Error",
                    additional_info={"query": symbol}
                )
                return web_search_simple.invoke(f"Official Balance Sheet of {symbol}")
            else:
                return balance_sheet
        else:
            return web_search_simple.invoke(f"Official Balance Sheet of {symbol}")
    except Exception as e:
        log_error(
            tool_name="get_balance_sheet",
            error_message=str(e),
            additional_info={"query": symbol}
        )
        return web_search_simple.invoke(f"Official Balance Sheet of {symbol}")


@tool
def get_cash_flow(company: Annotated[str, "company name"]):
    """
    Fetches and returns the latest cash flow statement of the company.
    Args:
        company (str): The company name.
    Returns:
        DataFrame: The income statement data.
    """
    try:
        symbol = get_ticker.invoke(company)
        if symbol:
            ticker = yf.Ticker(symbol)
            return ticker.cashflow
        else:
            return web_search_simple.invoke(f"latest cash flow statement of {company}")
    
    except Exception as e:
        log_error(
            tool_name="get_cash_flow",
            error_message=str(e),
            additional_info={"query": symbol}
        )
        return web_search_simple.invoke(f"latest cash flow statement of {company}")
        

@tool
def get_analyst_recommendations(company: Annotated[str, "company name"]):
    """
    Fetches the latest analyst recommendations and returns the most common recommendation and its count.
    Args:
        company (str): The company name.
    Returns:
        DataFrame: The income statement data.
    """
    try:
        symbol = get_ticker.invoke(company)
        if symbol:
            ticker = yf.Ticker(symbol)
            recommendations = ticker.recommendations
            if recommendations.empty:
                log_error(
                tool_name="get_analyst_recommendations",
                error_message=str(e),
                additional_info={"query": symbol}
                )
            
                return None, 0

            row_0 = recommendations.iloc[0, 1:]
            max_votes = row_0.max()
            majority_voting_result = row_0[row_0 == max_votes].index.tolist()

            return majority_voting_result[0]
        else:
            return web_search_simple.invoke(f"Get the latest analyst recommendations for {company}")
        
    except Exception as e:
        log_error(
            tool_name="get_analyst_recommendations",
            error_message=str(e),
            additional_info={"query": symbol}
        )
        
        return web_search_simple.invoke(f"Get the latest analyst recommendations for {company}")

@tool
def get_wikipedia_summary(query: str):
    """
    Fetches a summary from Wikipedia based on a search query.
    Args:
        query (str): The search query terms to look up on Wikipedia. Also there should be less than four terms.

    Returns:
        str: A summary of the Wikipedia page found for the query. If no results are found,
             or if there is an error fetching the page, appropriate messages are returned.
    """
    
    try:
        search_results = wikipedia.search(query)
        if not search_results:
            return web_search_simple.invoke(query)
        try:
            result = wikipedia.page(search_results[0])
            return f"Found match with {search_results[0]}, Here is the result:\n{result.summary}"
        except:
            result = wikipedia.page(search_results[1])
            return f"Found match with {search_results[1]}, Here is the result:\n{result.summary}"
    except Exception as e:
        log_error(
            tool_name="get_wikipedia_summary",
            error_message=str(e),
            additional_info={"query": query}
        )
        
        return "This tool is not working right now. DO NOT CALL THIS TOOL AGAIN!"


@tool
def get_discord(channel_id):
    """
    Fetch and process messages from a Discord channel.

    Args:
        channel_id (str): The ID of the Discord channel.

    Returns:
        list: A list of dictionaries containing formatted message data.
    """
    try:
        headers = {
            'authorization': os.getenv("DISCORD_AUTH_KEY")
        }
        url = f"https://discord.com/api/v9/channels/{channel_id}/messages"
        
        
            # Fetch messages
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        messages = response.json()
    except Exception as e:
        log_error(
            tool_name="get_discord",
            error_message=str(e),
            additional_info={"channel_id": channel_id}
        )
        
        print(f"Error fetching messages: {e}")
        return []

    formatted_messages = []
    for msg in messages:
        # Extract basic details
        author = f"{msg['author']['username']}#{msg['author']['discriminator']}"
        content = msg.get('content', "")
        timestamp = msg.get('timestamp', "")
        attachments = [att.get('url') for att in msg.get('attachments', [])]

        # Replace mentions (IDs) with usernames
        mentions = msg.get('mentions', [])
        for mention in mentions:
            user_mention = f"<@{mention['id']}>"
            username = f"@{mention['username']}"
            content = content.replace(user_mention, username)

        # Format message
        formatted_message = {
            "author": author,
            "content": content,
            "timestamp": timestamp,
            "attachments": attachments
        }
        formatted_messages.append(formatted_message)
   

@tool 
def gmail_search_tool(query: str, top_n: int = 10) -> str:
    """
    Fetches and retrieves Gmail emails matching the given query.

    Args:
        query (str): The Gmail search query (e.g., "subject:invoice after:2024/01/01").
        top_n (int): The number of top results to fetch (default is 10).

    Returns:
        str: A formatted string containing email results.
    """
    SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]
    creds = None

    # Load or authenticate credentials
    try:
        if os.path.exists("token.json"):
            creds = Credentials.from_authorized_user_file("token.json", SCOPES)
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
                creds = flow.run_local_server(port=8000)
            # Save credentials for future use
            with open("token.json", "w") as token:
                token.write(creds.to_json())

    
        # Build the Gmail API service
        service = build("gmail", "v1", credentials=creds)

        # Perform the search query
        results = service.users().messages().list(userId="me", q=query).execute()
        messages = results.get("messages", [])
        if not messages:
            return "No emails found for the given query."

        email_data = []
        for msg in messages[:top_n]:  # Limit to the specified number of results
            msg_details = service.users().messages().get(userId="me", id=msg["id"]).execute()
            headers = msg_details["payload"]["headers"]

            # Extract subject and sender
            subject = next((header["value"] for header in headers if header["name"] == "Subject"), "No Subject")
            sender = next((header["value"] for header in headers if header["name"] == "From"), "No Sender")

            # Extract body
            body = ""
            payload = msg_details["payload"]
            if "body" in payload and payload["body"].get("data"):
                body = base64.urlsafe_b64decode(payload["body"]["data"]).decode("utf-8")
            elif "parts" in payload:
                for part in payload["parts"]:
                    if part["mimeType"] == "text/plain" and "data" in part["body"]:
                        body += base64.urlsafe_b64decode(part["body"]["data"]).decode("utf-8")
                    elif part["mimeType"] == "text/html" and "data" in part["body"]:
                        html_body = base64.urlsafe_b64decode(part["body"]["data"]).decode("utf-8")
                        body += BeautifulSoup(html_body, "html.parser").get_text()

            email_data.append({
                "subject": subject,
                "sender": sender,
                "body": body.strip(),
            })

        # Format email data for output
        formatted_emails = []
        for i, email in enumerate(email_data, start=1):
            formatted_emails.append(
                f"Email {i}:\n"
                f"Subject: {email['subject']}\n"
                f"Sender: {email['sender']}\n"
                f"Body: {email['body'][:500]}\n"  # Limit body for readability
            )
        return "\n\n".join(formatted_emails)

    except Exception as error:
        log_error(
            tool_name="get_gmail_search",
            error_message=str(error),
            additional_info={"query": query}
        )
        
        return f"An error occurred: {error}"
    
# Set up the Reddit instance with your credentials
reddit = praw.Reddit(
    client_id=os.environ["reddit_client_id"],  # Replace with your client_id
    client_secret=os.environ["reddit_client_secret"],  # Replace with your client_secret
    redirect_uri="http://localhost:8080",  # Replace with your redirect URI
    user_agent=os.environ["reddit_user_agent"],  # Replace with a meaningful user agent
)

@tool
def get_reddit_search(query, limit=5):
    """
    Search for Reddit posts based on a query and fetch the content of the first result.

    Args:
        query (str): The query to search for on Reddit.
        limit (int): Number of posts to return in the search results (default is 5).

    Returns:
        dict: A dictionary containing the title, body, comments, and metadata of the first post.
    """
    # Search for posts matching the query
    try:
        search_results = reddit.subreddit('all').search(query, limit=limit)
        
        # Fetch content from the first post in the search results
        for submission in search_results:
            # Fetch submission details
            submission_data = {
                "title": submission.title,
                "body": submission.selftext,  # Post content (if it's a text post)
                "comments": [],
                "score": submission.score,  # Upvote count
                "subreddit": submission.subreddit.display_name,
                "author": str(submission.author),
            }

            # Fetch top-level comments
            submission.comments.replace_more(limit=0)  # Avoid "More comments" placeholder
            for comment in submission.comments[:5]:  # Limit to 5 comments
                submission_data["comments"].append({
                    "author": str(comment.author),
                    "body": comment.body,
                    "score": comment.score
                })

            data = ""
            if submission_data:
                data += f"Title: {submission_data['title']}\n\n\n"
                data += f"Body: {submission_data['body']}\n\n\n"
                data += f"Subreddit: {submission_data['subreddit']}\n\n\n"
                data += f"Author: {submission_data['author']}\n\n\n"
                data += f"Score: {submission_data['score']}\n\n\n"
                data += "\nComments:\n"

                for i, comment in enumerate(submission_data["comments"], 1):
                    data += f"{i}. Author: {comment['author']}, Score: {comment['score']}\n"
                    data += f"   {comment['body']}\n\n" # Return the populated data dictionary
                return data
    except Exception as e:
        log_error(
            tool_name="get_reddit_search",
            error_message=str(e),
            additional_info={"query": query}
        )
        
        return "No posts found matching the query."

@tool
def simple_query_documents(prompt: str) -> Dict:
    """
    Query documents using a Retrieval-Augmented Generation (RAG) endpoint.
    This should be the first choice before doing web search,
    if this fails or returns unsatisfactory results, then use web search for the same query.

    Args:
        prompt (str): The prompt to send to the RAG endpoint.
        source (str): The source URL of the document.

    Returns:
        Dict: The JSON response from the RAG endpoint, containing the retrieved information and generated answer.
    """
    try:    
        print("Started_simple")
        start = time.time()
        
        payload = {
            "query": prompt, 
            "destination": 'user' 
        }
        print(payload)
        response = requests.post(
            "http://localhost:4005/generate",
            headers={"Content-Type": "application/json"},
            json=payload
        )
        
        print(f"Response status code: {response.status_code}")
        print("Posted_simple")
        response.raise_for_status()  # Raise an error for HTTP issues
        print("Raised_simple")
        
        end = time.time()
        print(f"Time taken: {end - start} seconds")
        
        result = response.json()
        print(result)
        return result
    
    except requests.RequestException as e:
        print(f"HTTP Request failed: {e}")
        if hasattr(e, 'response'):
            if e.response is not None:
                print(f"Response status code: {e.response.status_code}")
                print(f"Response content: {e.response.text}")
        log_error(
            tool_name="simple_query_documents",
            error_message=str(e),
            additional_info={"prompt": prompt}
        )
        
        return ''
        
@tool
def retrieve_documents(prompt: str) -> str:
    """
    Extract Information from the provided internal document
    Since this is the main source of information which is always 
    correct, this should be the first choice of tool for any agent.
    CALL THIS BEFORE CALLING ANY OTHER TOOL.
    Args:
        prompt (str): The prompt to send to the RAG endpoint.
        source (str): The source URL of the document.
    Returns:
        Dict: The JSON response from the RAG endpoint, containing the retrieved information and generated answer.
    """

    try:    
        print("Started")
        start = time.time()
        
        payload = {
            "query": prompt,
            "k" : 2  , 
            "destination" : 'user'
        }
        
        response = requests.post(
            "http://localhost:4006/v1/retrieve",
            headers={"Content-Type": "application/json"},

            json=payload

        )
        
        print(f"Response status code: {response.status_code}")
        print("Posted")
        response.raise_for_status()  # Raise an error for HTTP issues
        print("Raised")
        
        end = time.time()
        print(f"Time taken: {end - start} seconds")
        
        result = response.json()
        out = ''
        for i in result:
            for j in i.values():
                if type(j) is str:
                    out += f"{j} "
                elif type(j) is dict:
                    for k in j.values():
                        out += f"{str(j)} "
                    out+= '\n'
            out+= '\n'
        return out
    
    except requests.RequestException as e:
        print(f"HTTP Request failed: {e}")
        if hasattr(e, 'response'):
            if e.response is not None:
                print(f"Response status code: {e.response.status_code}")
                print(f"Response content: {e.response.text}")
        log_error(
            tool_name="query_documents",
            error_message=str(e),
            additional_info={"prompt": prompt}
        )
        return web_search_simple.invoke(prompt)

