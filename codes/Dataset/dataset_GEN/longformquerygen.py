import google.generativeai as genai
import time
import pandas as pd
import os
from dotenv import load_dotenv
load_dotenv('../../.env')

requests = 1

model = genai.GenerativeModel("gemini-1.5-flash")

from google.generativeai.types import HarmCategory, HarmBlockThreshold

def generate(prompt):
    try:
    #if 15 RPM for gemini model exceeds
    # global requests
    # if (requests%15 == 0):
    #     time.sleep(65)
        safety_settings = {
            HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
        }
        # requests+=1
        return model.generate_content(prompt, safety_settings=safety_settings)
    except Exception as e:
        time.sleep(65)
        return generate(prompt)
    

prompt = '''
similar to mergers like bank of america and nation bank, exxon mobile and pioneer, microsoft and activistion, give me a list of REAL 100 Merger and aquistiion case study (simply output both companies name)
'''

prompt2 = '''
Example queries:
1. Quantify the potential synergies from a merger between Company D and Company E. Break down the estimated cost savings, revenue enhancements, and tax benefits, and assess the time frame required to realize these synergies fully. Address potential risks to achieving these outcomes
2. Generate Company Z's recent annual report for compliance with key financial and operational regulations. Highlight any disclosures of potential regulatory risks or areas of non-compliance.
3. Evaluate the integration strategies employed by Company X post-acquisition of Company Y and their success in the market.
4. Create a report summarizing the merger deal between Company A and Company B. Include the valuation metrics, deal structure, synergies highlighted by management, and the immediate impact on stock prices of both companies.
5. Prepare a risk assessment report for Company G based on their quarterly financial statements and market conditions. Highlight potential risks in operations, financial stability, and market competition
'''

prompt3 = '''
for the above mentioned company, generate SEVEN queries (do not give reasoning) similar to the below example queries that would require a document analysis as an answer, focus on financial and legal aspects only
'''

companies = [
    "H.J. Heinz and Kraft Foods Group",
    "Charter Communications and Time Warner Cable",
    "CenturyLink and Embarq",
    "Level 3 Communications and Global Crossing",
    "Windstream and EarthLink",
    "Frontier Communications and Verizon's wireline operations in California, Texas, and Florida",
    "Altice and Cablevision Systems",
    "Dish Network and EchoStar Communications",
    "DirectTV and AT&T (pre-Time Warner merger)",
    "Viacom and CBS (multiple mergers and separations)",
    "Lionsgate and Starz",
    "Discovery and Scripps Networks Interactive",
    "Tegna and Standard Media Group",
    "Nexstar and Tribune Media",
    "Gray Television and Quincy Media",
    "E.W. Scripps Company and Ion Media",
    "Meredith Corporation and Time Inc. (magazine division)",
    "Gannett and GateHouse Media",
    "Vox Media and Group Nine Media",
    "BuzzFeed and Complex Media",
    "Axel Springer and Politico",
    "IAC and Dotdash",
    "Zillow Group and Trulia",
    "Redfin and RentPath",
    "CoStar Group and LoopNet",
    "Expedia and Orbitz Worldwide",
    "Priceline Group (Booking Holdings) and Kayak",
    "TripAdvisor and Viator",
    "Booking Holdings and OpenTable",
    "United Airlines and Continental Airlines",
    "Delta Air Lines and Northwest Airlines",
    "American Airlines and US Airways",
    "Southwest Airlines and AirTran Airways",
    "Alaska Airlines and Virgin America",
    "JetBlue and Spirit Airlines (pending)",
    "Boeing and McDonnell Douglas",
    "Airbus and Bombardier CSeries program (now A220)",
    "United Technologies and Raytheon (forming Raytheon Technologies)",
    "Lockheed Martin and Sikorsky Aircraft",
    "Northrop Grumman and Orbital ATK",
    "General Dynamics and CSRA",
    "L3Harris Technologies and Aerojet Rocketdyne",
    "Leidos and Dynetics",
    "Booz Allen Hamilton and EverWatch",
    "CACI International and Six3 Systems",
    "Huntington Ingalls Industries and Newport News Shipbuilding",
    "General Electric and Baker Hughes (oilfield services)",
    "Schlumberger and Cameron International",
    "Halliburton and Baker Hughes (terminated)",
    "Technip and FMC (forming TechnipFMC)",
    "McDermott and CB&I",
    "Fluor and Stork",
    "Jacobs Engineering Group and CH2M Hill",
    "AECOM and URS Corporation",
    "WSP Global and Parsons Brinckerhoff",
    "Stantec and MWH Global",
    "Tetra Tech and Coffey International",
    "Wood and Amec Foster Wheeler",
    "WorleyParsons and Jacobs ECR",
    "KBR and Wyle",
    "Danaher and Pall Corporation",
    "Thermo Fisher Scientific and Life Technologies",
    "PerkinElmer and Euroimmun",
    "Agilent Technologies and Varian",
    "Waters Corporation and TA Instruments",
    "Mettler Toledo and Sartorius Mechatronics",
    "Becton Dickinson and C. R. Bard",
    "Cardinal Health and Cordis Corporation",
    "Medtronic and Covidien",
    "Zimmer Biomet and Biomet",
    "Stryker and Wright Medical",
    "Smith & Nephew and Osiris Therapeutics",
    "Boston Scientific and BTG",
    "Abbott Laboratories and St. Jude Medical",
    "Hologic and Gen-Probe",
    "Roche and Genentech",
    "Amgen and Onyx Pharmaceuticals",
    "Gilead Sciences and Pharmasset",
    "Celgene and Juno Therapeutics",
    "Bristol Myers Squibb and Celgene",
    "Takeda and Shire",
    "AstraZeneca and Alexion Pharmaceuticals",
    "Pfizer and Arena Pharmaceuticals",
    "Merck & Co. and Acceleron Pharma",
    "Eli Lilly and Loxo Oncology",
    "Novartis and The Medicines Company",
    "Sanofi and Bioverativ",
    "Regeneron and Libytec",
    "CSL Behring and Vifor Pharma",
    "Horizon Therapeutics and Viela Bio",
    "Illumina and Grail",
    "Agilent and Resolution Bioscience",
    "Danaher and Cytiva",
    "Thermo Fisher Scientific and PPD",
    "LabCorp and Dynacare",
    "Quest Diagnostics and AmeriPath",
    "Walgreens Boots Alliance and Rite Aid (partial acquisition)",
    "Kroger and Harris Teeter",
    "Albertsons and Safeway",
    "Ahold Delhaize and Hannaford",
    "Disney and Pixar",
    "Disney and Marvel Entertainment",
    "Disney and 21st Century Fox",
    "AT&T and Time Warner",
    "Verizon and Yahoo!",
    "Verizon and AOL",
    "Facebook and WhatsApp",
    "Facebook and Instagram",
    "Google and YouTube",
    "Google and Waze",
    "Amazon and Whole Foods Market",
    "Amazon and MGM",
    "Microsoft and LinkedIn",
    "Microsoft and Skype",
    "Apple and Beats Electronics",
    "Oracle and Sun Microsystems",
    "Salesforce and Slack",
    "Adobe and Figma",
    "IBM and Red Hat",
    "Avago Technologies and Broadcom",
    "Broadcom and CA Technologies",
    "CVS Health and Aetna",
    "Cigna and Express Scripts",
    "Anthem and WellPoint Health Networks",
    "Pfizer and Wyeth",
    "Glaxo Wellcome and SmithKline Beecham",
    "Novartis and Alcon",
    "Sanofi-Synthelabo and Aventis",
    "AbbVie and Allergan",
    "Johnson & Johnson and Actelion",
    "Bayer and Monsanto",
    "Dow Chemical and DuPont",
    "Praxair and Linde",
    "Chevron and Texaco",
    "Exxon and Mobil",
    "BP and Amoco",
    "Royal Dutch Shell and BG Group",
    "Conoco and Phillips Petroleum",
    "AT&T and BellSouth",
    "Sprint and Nextel",
    "T-Mobile and MetroPCS",
    "Comcast and NBCUniversal",
    "Anheuser-Busch InBev and SABMiller",
    "Kraft and Heinz",
    "Mars and Wrigley",
    "Sysco and US Foods (terminated)",
    "J.P. Morgan Chase and Bank One",
    "Bank of America and Merrill Lynch",
    "Wells Fargo and Wachovia",
    "NationsBank and BankAmerica (formed Bank of America)"
]

data = []

for i in range(len(companies)):
    finalprompt = companies[i] + prompt3 + prompt2
    queries = generate(finalprompt).text
    queries = queries.split("\n")
    for query in queries:
        parts = query.split(". ")
        if len(parts)==2:
            index,text = parts
            data.append((int(index),text))

df = pd.DataFrame(data, columns=["Index", "Queries"])

# Save to CSV
output_file = "dataCINQ.csv"
df.to_csv(output_file, index=False)



