""" 
This script evaluates the performance of a model by comparing its responses with a base model's responses.
"""
import google.generativeai as genai
import time
import pandas as pd
import os
from dotenv import load_dotenv

load_dotenv('../.env')

model = genai.GenerativeModel("gemini-1.5-flash")
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
    



# Function to evaluate a single prompt
def evaluate_responses(prompt, response_a, response_b):
    """ 
    Use the model to evaluate two responses to a given prompt and return the better response.
    Args:
        prompt (str): The prompt for the responses.
        response_a (str): The first response to evaluate.
        response_b (str): The second response to evaluate.
    Returns:
        str: The better response, either "A", "B", or "Tie". 
    """
    prompt = (
    "Please act as an impartial judge and evaluate which among the two responses are better across the metrics helpfulness, relevance, accuracy, depth, creativity, and level of detail of the response."
    "Avoid any position biases and ensure that the order in which the responses were presented does not influence your decision. "
    "Do not allow the length of the responses to influence your evaluation,"
    "Do not favor certain names of the assistants."
    "Be as objective as possible."
    "Example Output:"
    # "Reasoning: [Provide a brief explanation of your decision.]"
    "Decision: [A, B, or Tie]"
    "Now, evaluate the following:"
    f"Prompt: {prompt}"
    f"Response A: {response_a}"
    f"Response B: {response_b}"
    )
    decision = generate(prompt).text
    if "Decision: A" in decision:
        return "A"
    elif "Decision: B" in decision:
        return "B"
    elif "Decision: Tie" in decision:
        return "Tie"
    else:
        return "Error"

# Evaluate all prompts and calculate win rate
results = {"Prompt": [], "Decision": []}
model_a_wins = 0
model_b_wins = 0
ties = 0
errors = 0


def load_md_files():
    # mention the path
    evals_path = '' 
    md_files = [f for f in os.listdir(evals_path) if f.endswith('.md')]
    
    file_contents = {}
    for md_file in md_files:
        with open(os.path.join(evals_path, md_file), 'r', encoding='utf-8') as file:
            variable_name = os.path.splitext(md_file)[0]  # removes the .md extension
            file_contents[variable_name] = file.read()
    
    return file_contents
responses = []
for key,response in load_md_files().items():
    responses.append(response)


#"Explicty mention the queries here"
questions  = ["",]

for i in range(len(responses)//2):
    decision = evaluate_responses(questions[i], responses[i], responses[i+4])
    results["Prompt"].append(questions[i])
    results["Decision"].append(decision)
    if decision == "A":
        model_a_wins += 1
    elif decision == "B":
        model_b_wins += 1
    elif decision == "Tie":
        ties += 1
    else:
        errors += 1

total  = model_a_wins+model_b_wins+ties+errors

# Print results
print(f"Model A Wins: {model_a_wins} {model_a_wins/total}")
print(f"Model B Wins: {model_b_wins} {model_b_wins/total}")
print(f"Ties: {ties}")
print(f"Errors: {errors}")

output_file = "evaluat_results.csv"
results_df = pd.DataFrame(results)
results_df.to_csv(output_file, index=False)
print(f"Evaluation results saved to {output_file}")