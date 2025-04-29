""" 
This module contains the custom functions for generating candidates in the LATS agent. 
functions:
    - custom_generate_candidates: This function generates candidates for the LATS agent.
    - select: This function selects the best node in the tree.
    - custom_expand: This function expands the tree.
"""
import os
from langchain_openai import ChatOpenAI
from Agents.LATS.Reflection import  Node,reflection_chain
from langchain_core.prompt_values import ChatPromptValue
from langchain_core.runnables import RunnableConfig
from Agents.LATS.Initial_response import prompt_template
from Agents.LATS.TreeState import TreeState
from langchain_core.messages import AIMessage
from langchain_core.output_parsers.openai_tools import (
    JsonOutputToolsParser,
    PydanticToolsParser,
)

from collections import defaultdict
from langgraph.prebuilt import ToolNode
from Agents.LATS.NewTools import *
from dotenv import load_dotenv
load_dotenv('../../../.env')
parser = JsonOutputToolsParser(return_id=True)

from LLMs import GPT4o_mini_LATS

def custom_generate_candidates(tools):
    """ 
    Generate candidates for the LATS agent.
    """
    def generate_candidates(messages: ChatPromptValue, config: RunnableConfig):
        bound_kwargs = GPT4o_mini_LATS.bind_tools(tools=tools).kwargs
        chat_result = GPT4o_mini_LATS.generate(
            [messages.to_messages()],
            callbacks=config["callbacks"],
            run_name="GenerateCandidates",
            **bound_kwargs,
        )
        return [gen.message for gen in chat_result.generations[0]]
    return generate_candidates

def select(root: Node) -> dict:
    """
    Starting from the root node a child node is selected at each tree level until a leaf node is reached.
    """

    if not root.children:
        return root

    node = root
    while node.children:
        max_child = max(node.children, key=lambda child: child.upper_confidence_bound())
        node = max_child

    return node

def custom_expand(tools):
    """ Expand the tree for the LATS agent.
    Args:
        tools: The tools available to the agent.
    Returns:
        function: The function to expand the tree.
    """
    expansion_chain = prompt_template | custom_generate_candidates(tools)
    tool_node = tool_node = ToolNode(tools=tools)

    def expand(state: TreeState, config: RunnableConfig) -> dict:
        """
        Starting from the "best" node in the tree, generate N candidates for the next step.
        """
        root = state["root"]
        best_candidate: Node = select(root)
        messages = best_candidate.get_trajectory() 
        # Generate N candidates from the single child candidate
        new_candidates = expansion_chain.invoke(
            {"input": state["input"], "messages": messages}, config
        )
        parsed = parser.batch(new_candidates)
        flattened = [
            (i, tool_call)
            for i, tool_calls in enumerate(parsed)
            for tool_call in tool_calls
        ]
        tool_responses = [
            (
                i,
                tool_node.invoke(
                    {
                        "messages": [
                            AIMessage(
                                content="",
                                tool_calls=[
                                    {
                                        "name": tool_call["type"],
                                        "args": tool_call["args"],
                                        "id": tool_call["id"],
                                    }
                                ],
                            )
                        ]
                    }
                ),
            )
            for i, tool_call in flattened
        ]
        collected_responses = defaultdict(list)
        for i, resp in tool_responses:
            collected_responses[i].append(resp["messages"][0])
        output_messages = []
        for i, candidate in enumerate(new_candidates):
            output_messages.append([candidate] + collected_responses[i])

        # Reflect on each candidate
        reflections = reflection_chain.batch(
            [{"input": state["input"], "candidate": msges} for msges in output_messages],
            config,
        )

        # We have already extended the tree directly, so we just return the state
        child_nodes = [
            Node(cand, parent=best_candidate, reflection=reflection)
            for cand, reflection in zip(output_messages, reflections)
        ]
        best_candidate.children.extend(child_nodes)
        return state
    return expand