import concurrent.futures
from collections import defaultdict
from typing import List, Any, Dict
import threading
from Agents.Agents import Agent

def executeTask(task_info: tuple[Any, Dict, set, threading.Lock, threading.Lock]):
    agent, task_results_internal, completed_tasks_internal, results_lock, completed_lock = task_info
    print(f"Executing {agent.taskNumber}")
    with open("ProcessLogs.md", 'a') as f:
        f.write(f"### Executing {agent.taskNumber}\n")
    try:
        dependency_results = {
            dep: task_results_internal.get(dep) 
            for dep in agent.dependencies 
            if dep in task_results_internal
        }
        
        response = agent.genContext_andRunLATS(dependency_results)
        
        with results_lock:
            task_results_internal[agent.taskNumber] = response
        
        with completed_lock:
            completed_tasks_internal.add(agent.taskNumber)
        
        print(f"Executed {agent.taskNumber}")
        with open("ProcessLogs.md", 'a') as f:
            f.write(f"### Executed {agent.taskNumber}\n\n")
        
        return response
    except Exception as e:
        print(f"Error in task {agent.taskNumber}: {e}")
        with open("ProcessLogs.md", 'a') as f:
            f.write(f"### Error in task {agent.taskNumber}: {e}\n\n")
        print(f"Executed {agent.taskNumber}")
        return None


class Smack:
    def __init__(self, agents: List[Agent]):
        self.raccoons = agents

    def generateGraph(self):
        dependency_graph = defaultdict(list)
        indegree = defaultdict(int)

        for agent in self.raccoons:
            if not agent.dependencies:
                indegree[agent.taskNumber] = 0
        
            for dependent_task in agent.dependencies:
                dependency_graph[dependent_task].append(agent.taskNumber)
                indegree[agent.taskNumber] += 1
        ready_tasks = [task for task, degree in indegree.items() if degree == 0]
        return dependency_graph, indegree, ready_tasks

    def executeSmack(self):
        dependency_graph, indegree, ready_tasks = self.generateGraph()
        task_results = {}
        completed_tasks = set()

        results_lock = threading.Lock()
        completed_lock = threading.Lock()


        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = {}

            while ready_tasks or futures:
                while ready_tasks:
                    task = ready_tasks.pop(0)
                    agent = next((raccoon for raccoon in self.raccoons if raccoon.taskNumber == task), None)
                    if agent:
                        # Submit task for execution
                        future = executor.submit(
                            executeTask, 
                            (agent, task_results, completed_tasks, results_lock, completed_lock)
                        )
                        futures[future] = task
                done, _ = concurrent.futures.wait(
                    futures.keys(), 
                    return_when=concurrent.futures.FIRST_COMPLETED
                )

                for future in done:
                    task_number = futures.pop(future)

                    for dependent_task in dependency_graph[task_number]:
                        indegree[dependent_task] -= 1

                        if indegree[dependent_task] == 0:
                            ready_tasks.append(dependent_task)
        return task_results