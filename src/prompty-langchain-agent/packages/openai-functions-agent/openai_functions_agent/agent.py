from typing import List, Tuple

from langchain.agents import AgentExecutor
from langchain.agents.format_scratchpad import format_to_openai_function_messages
from langchain.tools import BaseTool, StructuredTool, tool
from langchain.agents.output_parsers import OpenAIFunctionsAgentOutputParser
from langchain_community.chat_models import ChatOpenAI
from langchain_community.tools.convert_to_openai import format_tool_to_openai_function
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_openai import AzureChatOpenAI
from langchain_community.document_loaders import TextLoader
from langchain_openai import AzureOpenAIEmbeddings
from langchain_elasticsearch import ElasticsearchStore
import os
from langchain_prompty import create_chat_prompt
from langchain_text_splitters import CharacterTextSplitter
from azure.identity import DefaultAzureCredential, get_bearer_token_provider
# Define the arguments schema model
class SearchQueryArgs(BaseModel):
    query: str = Field(..., example="What is the current state of the stock market?")

token_provider = get_bearer_token_provider(
        DefaultAzureCredential(), "https://cognitiveservices.azure.com/.default"
    )

def prepare_search_client(local_load: bool = False):
    embeddings = AzureOpenAIEmbeddings(azure_endpoint=os.getenv('AZURE_OPENAI_ENDPOINT'), deployment=os.getenv('AZURE_OPENAI_EMBEDDING_DEPLOYMENT'), azure_ad_token_provider=token_provider)
    index_name = "langchain-test-index"
    if local_load:
        loader = TextLoader(os.path.join(os.path.dirname(os.path.abspath(__file__)), './data/documents.json'))
        documents = loader.load()
        text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
        docs = text_splitter.split_documents(documents)
        db = ElasticsearchStore.from_documents(index_name=index_name, documents=docs, embedding=embeddings, es_url=os.getenv('ELASTICSEARCH_ENDPOINT'), es_api_key=os.getenv('ELASTICSEARCH_API_KEY'))
    else:
        db = ElasticsearchStore(
            es_url=os.getenv('ELASTICSEARCH_ENDPOINT'),
            index_name="test_index",
            embedding=embeddings,
            es_api_key=os.getenv('ELASTICSEARCH_API_KEY')
        )
    db.client.indices.refresh(index=index_name)
    return db

docsearch = prepare_search_client(True)

def elastic_search_tool(query:str):
    results = docsearch.similarity_search(query)
    return results[0].page_content

elastic_search = StructuredTool.from_function(
    func=elastic_search_tool,
    name="elastic_search",
    description="useful for when you need to answer questions about current doc",
    args_schema=SearchQueryArgs
)

llm = AzureChatOpenAI(
    azure_deployment=os.getenv('AZURE_OPENAI_DEPLOYMENT'),
    azure_ad_token_provider=token_provider
)
tools = [elastic_search]
llm_with_tools = llm.bind(functions=[format_tool_to_openai_function(t) for t in tools])

prompt = create_chat_prompt(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'basic_chat.prompty'))




def _format_chat_history(chat_history: List[Tuple[str, str]]):
    buffer = []
    for human, ai in chat_history:
        buffer.append(HumanMessage(content=human))
        buffer.append(AIMessage(content=ai))
    return buffer

agent = (
    {
        "input": lambda x: x["input"],
        "chat_history": lambda x: _format_chat_history(x["chat_history"]),
        "agent_scratchpad": lambda x: format_to_openai_function_messages(
            x["intermediate_steps"]
        ),
    }
    | prompt
    | llm_with_tools
    | OpenAIFunctionsAgentOutputParser()
)


class AgentInput(BaseModel):
    input: str
    chat_history: List[Tuple[str, str]] = Field(
        ..., extra={"widget": {"type": "chat", "input": "input", "output": "output"}}
    )


agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True).with_types(
    input_type=AgentInput
)