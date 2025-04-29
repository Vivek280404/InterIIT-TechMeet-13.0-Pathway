""" 
This file contains the code to generate the initial response for the LATS agent. 
functions:
    - custom_generate_initial_response: This function generates the initial response for the LATS agent.
"""
from langchain_core.output_parsers.openai_tools import (
    JsonOutputToolsParser,
    PydanticToolsParser,
)
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from Agents.LATS.TreeState import TreeState
from Agents.LATS.Reflection import reflection_chain, Node
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, ToolMessage
from langgraph.prebuilt import ToolNode
from Agents.LATS.NewTools import *
import os
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
load_dotenv('../../../.env')

from LLMs import GPT4o_mini_LATS

prompt_template = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                """
                Generate a detailed response backed by numbers and sources to the user question below
                1. If 'retrieve_documents' tool is present in the available set of tools, ALWAYS CALL IT FIRST
                2. Any other tool will only be called after 'retrieve_documents'
                3. If required information has been extracted from 'retrieve_documents' and it provides satisfactory answer, DO NOT call any other tool.
                4. Do not remove Document and page number for any response from 'retrieve_documents'
                4. Use specialized tools to generate the response.
                5. Cite the sources,the link of the exact webpage  next to there relevant information in each response.
                """,
            ),
            ("user", "{input}"),
            MessagesPlaceholder(variable_name="messages", optional=True),
        ]
    )

# Define the node we will add to the graph
def custom_generate_initial_response(tools):
    """ 
    Generate the initial response for the LATS agent.
    Args:
        tools: The tools available to the agent.
    Returns:
        function: The function to generate the initial response.
    """
    tool_node = ToolNode(tools=tools)
    def generate_initial_response(state: TreeState) -> dict:
        initial_answer_chain = prompt_template | GPT4o_mini_LATS.bind_tools(tools=tools).with_config(
            run_name="GenerateInitialCandidate"
        )

        parser = JsonOutputToolsParser(return_id=True)

        #Generate the initial candidate response.
        res = initial_answer_chain.invoke({"input": state["input"]})
        parsed = parser.invoke(res)
        tool_responses = [
            tool_node.invoke(
                {
                    "messages": [
                        AIMessage(
                            content="",
                            tool_calls=[
                                {"name": r["type"], "args": r["args"], "id": r["id"]}
                            ],
                        )
                    ]
                }

            )
            for r in parsed
        ]
        output_messages = [res] + [tr["messages"][0] for tr in tool_responses]
        reflection = reflection_chain.invoke(
            {"input": state["input"], "candidate": output_messages}
        )
        root = Node(output_messages, reflection=reflection)
        return {
            **state,
            "root": root,
        }
    return generate_initial_response