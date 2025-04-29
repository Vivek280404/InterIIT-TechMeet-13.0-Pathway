import yfinance as yf
import requests
import json
import logging
import os
import re
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv('../.env')
api_gemini = os.getenv("GEMINI_API_KEY_30")

def extract_and_convert_to_json(text):
    """
    Extract company names from text, get ticker symbols using `get_ticker`,
    and fetch stock data. Save the data into a JSON file.
    """
    # Extract company names using Gemini (simulated as a placeholder here)
    company_names = gemini_extract_companies(text)
    
    # Prepare the JSON structure
    companies = []
    start_date = '2023-05-01'
    end_date = '2024-11-30'

    for company_name in company_names:
        ticker_symbol = get_ticker(company_name)
        print(ticker_symbol)
        if ticker_symbol:
            file_path = f"src/{company_name.replace(' ', '_')}_stock_data.csv"
            get_stock_data(ticker_symbol, start_date, end_date, file_path)
            companies.append({
                "company_name": company_name,
                "ticker_symbol": ticker_symbol,
                "file_path": file_path
            })
    
    # Save the data to a JSON file
    json_data = json.dumps(companies, indent=4)
    with open('companies.json', 'w') as f:
        f.write(json_data)
    print(json_data)

def gemini_extract_companies(query):
    genai.configure(api_key=api_gemini)
    model = genai.GenerativeModel("gemini-1.5-flash")
    message = f"""SYSTEM: you are a helpful AI assistant. you are given a query. your job is to carefully analyze the query, and extract the name of companies mentioned in the query\
    Return the name of the companies in the format: company1|company2|company3.
    Strictly follow this format. Do not return any other redundant text. Only return this answer in plaim text.
    HUMAN: {query}"""

    ai_msg = model.generate_content(message)
    print(ai_msg.text)
    company_names = ai_msg.text.split("|")

    company_names = [name.rstrip('\n') for name in company_names]
    print(company_names)
    # Simulated company names for demonstration
    return company_names

def get_ticker(company_name):
    """
    Retrieve the ticker symbol for a company name using the Yahoo Finance API.
    """
    yfinance_url = "https://query2.finance.yahoo.com/v1/finance/search"
    user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36'
    params = {"q": company_name, "quotes_count": 1, "country": "United States"}

    try:
        res = requests.get(url=yfinance_url, params=params, headers={'User-Agent': user_agent})
        res.raise_for_status()
        data = res.json()

        if "quotes" in data and len(data["quotes"]) > 0:
            return data["quotes"][0]["symbol"]
        else:
            logging.warning(f"No ticker found for {company_name}.")
            return None
    except Exception as e:
        logging.error(f"Error fetching ticker for {company_name}: {e}")
        return None

def get_stock_data(ticker_symbol, start_date, end_date, output_file):
    """
    Fetch stock data for a given ticker and save it to a CSV file.
    """
    try:
        stock = yf.Ticker(ticker_symbol)
        df = stock.history(start=start_date, end=end_date)
        if not df.empty:
            df.to_csv(output_file)
            logging.info(f"Stock data for {ticker_symbol} saved to {output_file}.")
        else:
            logging.warning(f"No stock data available for {ticker_symbol}.")
    except Exception as e:
        logging.error(f"Error fetching stock data for {ticker_symbol}: {e}")



