"""
This module sets up various configurations for different ChatOpenAI models using the langchain library.
"""
import os
from dotenv import load_dotenv
load_dotenv('../.env')

openai_api_key=os.getenv("OPEN_AI_API_KEY_30")

from langchain_openai import ChatOpenAI

#For Memory
from langchain.memory import CombinedMemory, ConversationBufferMemory, ConversationSummaryMemory, ConversationEntityMemory
from langchain.chains import ConversationChain
from langchain.prompts import PromptTemplate
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain.memory.prompt import ENTITY_MEMORY_CONVERSATION_TEMPLATE


# Agents/LATS/generate_candidates -> done
# Agents/LATS/Initial_response -> done 
# Agents/LATS/Reflection -> done
GPT4o_mini_LATS = ChatOpenAI(model="gpt-4o-mini",openai_api_key = openai_api_key, temperature=0.4, model_kwargs={"top_p": 0.4})


# Agents/ConciseAnsAgent -> done
#GPT4o_mini_SimpleAnswers = ChatOpenAI(model="gpt-4o-mini",openai_api_key = openai_api_key, temperature=0.3, model_kwargs={"top_p": 0.3})

# Agents/conciseLATS -> done
#GPT4o_mini_SimpleAnswersLATS = ChatOpenAI(model="gpt-4o-mini",openai_api_key = openai_api_key, temperature=0.3, model_kwargs={"top_p": 0.3})

# Agents/ChartGenAgent -> done
GPT4o_mini_GraphGen = ChatOpenAI(model="gpt-4o-mini",openai_api_key = openai_api_key, temperature=0.2, model_kwargs={"top_p": 0.1})

# Agents/DrafterAgent -> done
# Agents/RAG_Agent -> done
# Generate Questions -> done
# Agents/PlannerAgent -> done

GPT4o_mini_Complex = ChatOpenAI(model="gpt-4o-mini",openai_api_key = openai_api_key, temperature=0.6, model_kwargs={"top_p": 0.7})

#buffer_memory_complex = ConversationBufferMemory(memory_key="chat_history_lines",return_messages=True, input_key="input")
summary_memory_complex = ConversationSummaryMemory(llm=GPT4o_mini_Complex, input_key="input")
summary_memory_complex_entity = ConversationEntityMemory(llm=GPT4o_mini_Complex, input_key="input", return_messages=True)


'''combined_memory_complex = CombinedMemory(
    memories=[
        buffer_memory_complex,
        summary_memory_complex
    ]
)'''


"""_DEFAULT_TEMPLATE = '''
Summary of conversation:
{history}
Current conversation:
{chat_history_lines}

{input}
AI:
'''


PROMPT = PromptTemplate(
    input_variables=["history", "input", "chat_history_lines"],
    template=_DEFAULT_TEMPLATE,
)"""

conversation_complex = ConversationChain(
    llm=GPT4o_mini_Complex,
    #memory=summary_memory_complex_entity,
    #verbose=True,
    #prompt=ENTITY_MEMORY_CONVERSATION_TEMPLATE
)




#TopicalGuardrails
GPT4o_mini_GuardRails = ChatOpenAI(model="gpt-4o-mini",openai_api_key = openai_api_key, temperature=0.2, model_kwargs={"top_p": 0.1})
