# Langchain+Prompyt+Pinecone

## How to run locally

### Prerequisite
In order to host this app, you need to have:

- A valid Elastic Search account
- An Azure OpenAI endpoint with two deployments: one GPT deployment for chat and one embedding deployment for embedding.
- A created index in your Elastic Search account consistent with the index name in `test-app\packages\openai-functions-agent\openai_functions_agent\agent.py`. By default it is called `langchain-test-index`
- Put the data you want Elastic Search work with in `test-app\packages\openai-functions-agent\openai_functions_agent\data` folder and change the data file name in `agent.py` (change the `local_load` settings as well)
- Create and save your elastic search api key. Remember to pass the encoded key to the environment variables.


### dependency requirements:

- Python=3.11
- poetry==1.6.1

### go to `test-app` folder and do followings:

1. use poetry to install all dependency
`RUN poetry install --no-interaction --no-ansi`

1. set environment variables(on Windows)

```ps1
$Env:PINECONE_API_KEY = <your pinecone api key>
$Env:AZURE_OPENAI_API_KEY= <your aoai api key>
$Env:AZURE_OPENAI_ENDPOINT= <your aoai endpoint>
$Env:OPENAI_API_VERSION= <your aoai api version>
$Env:AZURE_DEPLOYMENT= <your aoai deployment name for chat>
$Env:AZURE_OPENAI_EMBEDDING_DEPLOYMENT= <your aoai deployment name for embedding>
```

3. Now try to run it on your local
`langchian serve`

1. you can go to http://localhost:8000/openai-functions-agent/playground/ to test.

1. you can mention your index in `input` to tell agent to use search tool.
e.g. ![alt text](image.png)![alt text](image-1.png)

## deploy to MIR
 TODO: working on the script that can deploy to MIR.