from Agents.LATS.Create_graph import generateGraph_forLATS
import json
from Agents.LATS.NewTools import *
from dotenv import load_dotenv
load_dotenv('../../../.env')

def SolveSubQuery(query:str, tools):
    question = query
    last_step = None
    graph = generateGraph_forLATS(tools)
    for step in graph.stream({"input": question}):
        last_step = step
        step_name, step_state = next(iter(step.items()))
        print(step_name)
        print("rolled out: ", step_state["root"].height)
        print("---")
    try:
        solution_node = last_step["expand"]["root"].get_best_solution()
    except Exception as e:
        solution_node = last_step["start"]["root"].get_best_solution()
    best_trajectory = solution_node.get_trajectory(include_reflections=False)
    return best_trajectory[-1].content