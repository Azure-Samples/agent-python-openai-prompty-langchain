from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from langserve import add_routes

app = FastAPI()

from dotenv import load_dotenv
load_dotenv('.env')

@app.get("/")
async def redirect_root_to_docs():
    return RedirectResponse("/docs")

from openai_functions_agent import agent_executor as openai_functions_agent_chain
add_routes(app, openai_functions_agent_chain, path="/openai-functions-agent")

# from rag_elasticsearch import chain as rag_elasticsearch_chain
# add_routes(app, rag_elasticsearch_chain, path="/rag-elasticsearch")

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
