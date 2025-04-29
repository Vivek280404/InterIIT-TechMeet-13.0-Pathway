---
title: Evaluation 
---

# Evaluation

In the Evaluation folder, we have four python scripts, each referring to a different eval strategy.

To run any python script in this folder,
To run the script :

1. Install the dependencies

`pip install -r requirements.txt`

2. Specify the dataset file path wherever indicated in the script.
3. Run the python script
4. The script generates a CSV file as output, containing detailed scores.

## Main evaluation Strategy : main_eval.py

In this methodology, we are implementing multi-agentic framework where we have expert reviewer agent to review and compare the responses, judge agent which passes the judgment based on the reviews and then we have grader agent to grade the scores based on pre-defined metric rubric.

To run the script :

1. Install the dependencies

`pip install -r requirements.txt`

2. Specify the dataset file path wherever indicated in the script.
3. Run the python script
4. The script generates a CSV file as output, containing detailed scores.

### Evaluation using Swarm Agents :

The `swarm_agent.py` script uses a multi-agent framework powered by Swarm, including a Moderator, Experts, Parser, and Grader agents. It compares generated and baseline responses to queries based on predefined metrics. The evaluation results, including scores, are appended to a CSV file (`eval_results.csv`). Ensure to install the necessary dependencies via `requirements.txt` before running the script and mention the `file_path` of the dataset, wherever mentioned.

### LLM as a Judge

This script evaluates and compares two responses to a given query using an LLM as a judge. It calculates scores based on four key metrics: relevance, logical flow, financial analysis, and numerical data incorporation. The results are appended to a CSV file, providing a detailed assessment of both responses. Ensure to set up the environment and input dataset before running.

### Winrate

`winrate.py` uses a Gemini 1.5 Flash model as an impartial judge to evaluate and compare two responses based on helpfulness, relevance, accuracy, depth, creativity, and detail. The responses are assessed for their quality, and the results, including win rates and ties, are saved in a CSV file. Ensure to specify the correct file path for evaluation
