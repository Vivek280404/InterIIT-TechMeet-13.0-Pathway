import google.generativeai as genai
import time
import pandas as pd
import os
from dotenv import load_dotenv

load_dotenv('../../.env')

requests = 1
model = genai.GenerativeModel("gemini-1.5-pro")

from google.generativeai.types import HarmCategory, HarmBlockThreshold

def generate(prompt):
    try:
        safety_settings = {
            HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
        }
        # requests+=1
        return model.generate_content(prompt, safety_settings=safety_settings)
    except Exception as e:
        time.sleep(65)
        return generate(prompt)
min_words = 800
max_words = 1200

prompt = '''
    You are a highly advanced AI with expertise in providing detailed answers on financial and legal aspects in merger and acquistion deals. Answer the following question comprehensively, covering all aspects and nuances. Ensure the response is atleast to {min_words} and around {max_words} words and concludes naturally at the end of a sentence. Use structured explanations where needed for clarity.
'''

Questions  = [
    "Determine the post-merger financial performance of the combined Expedia and Orbitz entity, focusing on key performance indicators (KPIs) and shareholder returns.",
    "Assess the impact of the Schlumberger-Cameron International merger on the competitive landscape of the oil and gas services industry, referencing relevant legal and financial documentation.",
    "Compare the financial performance metrics (e.g., return on equity, debt-to-equity ratio) of Booz Allen Hamilton and EverWatch to identify key differences and potential areas of improvement.",
    "What were the major financial projections made by Johnson & Johnson regarding Actelion's contribution to its overall financial performance post-acquisition and how did these compare to actual results?",
    "Compare and contrast the debt structures of Boston Scientific and BTG, assessing their respective credit ratings and potential vulnerabilities to interest rate changes.",
    "Identify key provisions in the Bristol Myers Squibb-Celgene merger agreement regarding intellectual property rights and future drug development.",
    "Summarize the regulatory approvals required for the Loxo Oncology acquisition and any subsequent regulatory actions impacting the combined entity.",
]

data = []

for idx, question in enumerate(Questions):
    final_prompt = prompt + "\n" + question
    print(f"Generating response for question {idx + 1}...")
    print(question)
    answer = generate(final_prompt).text
    data.append({"Index": idx + 1, "Answers": answer})  # Store as a dictionary

df = pd.DataFrame(data)


# Save to CSV
output_file = "dataocho.csv"
df.to_csv(output_file, index=False)
