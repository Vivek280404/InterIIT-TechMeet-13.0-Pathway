def makeGraphJSON(plan_subTasks):
    """
    This function is used to generate a JSON representation of a graph from a given set of plan sub-tasks.
    Functions:
        makeGraphJSON(plan_subTasks): Generates a JSON representation of a graph from the provided plan sub-tasks.
    makeGraphJSON(plan_subTasks)
        Generates a JSON representation of a graph from the provided plan sub-tasks.
        Parameters:
            plan_subTasks (dict): A dictionary where keys are task identifiers and values are dictionaries containing 
                                  details about each task, including agent, content, agent_role_description, tools, 
                                  and required data.
        Returns:
            dict: A dictionary containing nodes and edges representing the graph. Nodes contain metadata about each task, 
                  and edges represent dependencies between tasks.
    """
    graphData = dict()
    graphData_nodes = []
    graphData_edges = []

    planner = {
        "value": 0,
            "metadata": {
                "agentRole": "Planning Agent",
                "taskDesc": "Dynamically Synthesize Agents and Orchestrate Information Passing",
                "agentDesc": "Dynamically Synthesize Agents and Orchestrate Information Passing",
                "tools": []
            }
    }
    graphData_nodes.append(planner)

    mapping = {}

    cnt = 1
    for task in plan_subTasks:
        mapping[task] = cnt
        dic = {}
        dic["value"] = cnt
        dic["metadata"] = {}
        dic["metadata"]["agentRole"] = plan_subTasks[task]["agent"]
        dic["metadata"]["taskDesc"] = plan_subTasks[task]["content"]
        dic["metadata"]["agentDesc"] = plan_subTasks[task]["agent_role_description"]
        dic["metadata"]["tools"] = plan_subTasks[task]["tools"]
        dic["metadata"]["connected_to"] = plan_subTasks[task]["require_data"]
        graphData_nodes.append(dic)
        if not plan_subTasks[task]["require_data"]:
            graphData_edges.append({ "source": 0, "target": cnt })
        else:
            for tas in plan_subTasks[task]["require_data"]:
                graphData_edges.append({"source": tas, "target": cnt})
        
        cnt+=1
    
    for i in graphData_edges:
        if i["source"]!=0:
            i["source"] = mapping[i["source"]]

    graphData["nodes"] = graphData_nodes
    graphData["edges"] = graphData_edges
    print(mapping)
    return graphData