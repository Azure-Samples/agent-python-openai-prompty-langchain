from openai_functions_agent.langchain_prompty import create_chat_prompt
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import AzureChatOpenAI
import langchain
# langchain.verbose = True
# langchain.debug = True
# langchain.llm_cache = False
from typing import Dict
import os

# Import things that are needed generically
from langchain.pydantic_v1 import BaseModel, Field
from langchain.tools import BaseTool, StructuredTool, tool
from langchain_community.tools.convert_to_openai import format_tool_to_openai_function
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.messages.base import BaseMessage
from typing import List, Tuple
from langchain.agents.format_scratchpad import format_to_openai_function_messages
from langchain.agents.output_parsers import OpenAIFunctionsAgentOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

@tool
def search(query: str) -> str:
    """Look up things online."""
    return "Thea meaning of life is Microsoft"

llm = AzureChatOpenAI(
    openai_api_version="2023-12-01-preview",
    azure_deployment="gpt-4",
)

tools = [search]
llm_with_tools = llm.bind(functions=[format_tool_to_openai_function(t) for t in tools])

def _format_chat_history(chat_history: List[Tuple[str, str]]):
    buffer = []
    for human, ai in chat_history:
        buffer.append({"role": 'user', "content": human})
        buffer.append({"role": 'assistant', "content": ai})
    return buffer

from langchain_core.runnables import RunnableLambda

run_prompty = create_chat_prompt(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'basic_chat.prompty'))

agent = (
    {
        "input": lambda x: x["input"],
        "chat_history": lambda x: _format_chat_history(x["chat_history"]),
        "agent_scratchpad": lambda x: format_to_openai_function_messages(
            x["intermediate_steps"]
        ),
    }
    | run_prompty
    | llm_with_tools
    | OpenAIFunctionsAgentOutputParser()
)

from langchain.agents import AgentExecutor

class AgentInput(BaseModel):
    input: str
    chat_history: List[Tuple[str, str]] = Field(
        ..., extra={"widget": {"type": "chat", "input": "input", "output": "output"}}
    )


agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True).with_types(
    input_type=AgentInput
)