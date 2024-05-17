# Function Calling with Prompty, LangChain and Elastic Search
In this sample, we utilize the new Prompty tool, Langchain, and Elasticsearch to build a large language model (LLM) search agent. This agent with Retrieval-Augmented Generation (RAG) technologyis is capable of answering user questions based on the provided data by integrating real-time information retrieval with generative responses.
# Function Calling with Prompty, LangChain and Elastic Search
 This sample uses Azure's new Promptly tool, Langchain, and Elasticsearch to build a large language model (LLM) search agent capable of answering user questions based on the provided data. It leverages Retrieval-Augmented Generation (RAG) to enhance the agent's response capabilities.

By the end of deploying this template, you should be able to:

1. Describe the integration and functionality of Azure's Promptly, [Langchain](https://python.langchain.com/v0.1/docs/get_started/introduction), and [Elasticsearch](https://www.elastic.co/elasticsearch) within the LLM search agent.
2. Explain how Retrieval-Augmented Generation (RAG) enhances the search capabilities of the agent.
3. Build, run, evaluate, and deploy the LLM search agent to Azure.
 
 
## Features
 
This project framework provides the following features:
 
* A `agent.py` file that serves as a chat agent. This agent is designed to receive users' questions, generate queries, perform searches within the data index using Elasticsearch, and refine the search outputs for user presentation.
* A `data` folder that stores local data. A new index is created during initialization, enabling efficient search capabilities.
* Built-in evaluations to test your Prompt Flow against a variety of test datasets with telemetry pushed to Azure AI Studio
* You will be able to use this app with Azure AI Studio
 
### Architecture Diagram
![architecture-diagram-prompty-elasticsearch](/images/architecture-diagram-prompty-elasticsearch.png)


 
## Getting Started
 
### Azure Account 

**IMPORTANT:** In order to deploy and run this example, you'll need:

* **Azure account**. If you're new to Azure, [get an Azure account for free](https://azure.microsoft.com/free/cognitive-search/) and you'll get some free Azure credits to get started. See [guide to deploying with the free trial](docs/deploy_lowcost.md).
* **Azure subscription with access enabled for the Azure OpenAI service**. You can request access with [this form](https://aka.ms/oaiapply). If your access request to Azure OpenAI service doesn't match the [acceptance criteria](https://learn.microsoft.com/legal/cognitive-services/openai/limited-access?context=%2Fazure%2Fcognitive-services%2Fopenai%2Fcontext%2Fcontext), you can use [OpenAI public API](https://platform.openai.com/docs/api-reference/introduction) instead. Learn [how to switch to an OpenAI instance](docs/deploy_existing.md#openaicom-openai).
* **Azure account permissions**:
  * Your Azure account must have `Microsoft.Authorization/roleAssignments/write` permissions, such as [Role Based Access Control Administrator](https://learn.microsoft.com/azure/role-based-access-control/built-in-roles#role-based-access-control-administrator-preview), [User Access Administrator](https://learn.microsoft.com/azure/role-based-access-control/built-in-roles#user-access-administrator), or [Owner](https://learn.microsoft.com/azure/role-based-access-control/built-in-roles#owner). If you don't have subscription-level permissions, you must be granted [RBAC](https://learn.microsoft.com/azure/role-based-access-control/built-in-roles#role-based-access-control-administrator-preview) for an existing resource group and [deploy to that existing group](docs/deploy_existing.md#resource-group).
  * Your Azure account also needs `Microsoft.Resources/deployments/write` permissions on the subscription level.


Once you have an Azure account you have two options for setting up this project. The easiest way to get started is GitHub Codespaces, since it will setup all the tools for you, but you can also set it up [locally]() if desired.
### Elasticsearch Account
Go to [Elasticsearch](https://www.elastic.co/elasticsearch) and create your account if you don't have one. For this quickstart template, please create a index in your Elasticsearch account named `langchain-test-index`. Keep your Elasticsearch encoded API key in a safe place and you will need to pass it for this template.

### Security requirements
The Elastic Search tool does not support Microsoft Managed Identity now. It is recommended to use [Azure Key Vault](https://azure.microsoft.com/en-us/products/key-vault/) to secure your API keys.
### Project setup

You have a few options for setting up this project.
The easiest way to get started is GitHub Codespaces, since it will setup all the tools for you,
but you can also [set it up locally](#local-environment) if desired.

#### GitHub Codespaces

You can run this repo virtually by using GitHub Codespaces, which will open a web-based VS Code in your browser:

[![Open in GitHub Codespaces](https://img.shields.io/static/v1?style=for-the-badge&label=GitHub+Codespaces&message=Open&color=brightgreen&logo=github)](https://codespaces.new/Azure-Samples/agent-python-openai-prompty-langchain)

Once the codespace opens (this may take several minutes), open a terminal window.

#### VS Code Dev Containers

A related option is VS Code Dev Containers, which will open the project in your local VS Code using the [Dev Containers extension](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers):

1. Start Docker Desktop (install it if not already installed)
1. Open the project:
    [![Open in Dev Containers](https://img.shields.io/static/v1?style=for-the-badge&label=Dev%20Containers&message=Open&color=blue&logo=visualstudiocode)](https://vscode.dev/redirect?url=vscode://ms-vscode-remote.remote-containers/cloneInVolume?url=https://github.com/azure-samples/agent-python-openai-prompty-langchain)
1. In the VS Code window that opens, once the project files show up (this may take several minutes), open a terminal window.
### Local Environment 

- Install [azd](https://aka.ms/install-azd)
    - Windows: `winget install microsoft.azd`
    - Linux: `curl -fsSL https://aka.ms/install-azd.sh | bash`
    - MacOS: `brew tap azure/azd && brew install azd`
- [Python 3.9, 3.10, or 3.11](https://www.python.org/downloads/)
    Important: Python and the pip package manager must be in the path in Windows for the setup scripts to work.
    Important: Ensure you can run python --version from console. On Ubuntu, you might need to run sudo apt install python-is-python3 to link python to python3.
 - This sample uses `gpt-3.5-turbo` and [OpenAI text to speech models](https://learn.microsoft.com/en-us/azure/ai-services/openai/concepts/models#text-to-speech-preview) which may not be available in all Azure regions. Check for [up-to-date region availability](https://learn.microsoft.com/azure/ai-services/openai/concepts/models#standard-deployment-model-availability) and select a region during deployment accordingly
    - We recommend using `swedencentral`for Azure OpenAI and `eastus` for the speech to text services 
 - A valid Elastic Search account
### Quickstart
 
1. Clone the repository and intialize the project: 
```
azd init agent-python-openai-prompty-langchain
```
Note that this command will initialize a git repository, so you do not need to clone this repository.

2. Login to your Azure account:
```
azd auth login
```
3. Set following environment variables:
`ELASTICSEARCH_ENDPOINT` and `ELASTICSEARCH_API_KEY`
1. Create a new azd environment:
```
azd env new
```
Enter a name that will be used for the resource group. This will create a new folder in the .azure folder, and set it as the active environment for any calls to azd going forward.

1. Provision and deploy the project to Azure: `azd up`
2. Set up CI/CD with `azd pipeline config`
3. Talk to your agent: 
please take the `validate_deployment.ipynb` as reference.
 
### Local Development
#### Prerequisite
- A valid Elasticsearch account
- An Azure OpenAI endpoint with two deployments: one GPT deployment for chat and one embedding deployment for embedding.
- Assign yourself `Cognitive Services User` role to the corresponding Azure AI services.
- A created index in your Elasticsearch account consistent with the index name in `src\prompty-langchain-agent\packages\openai-functions-agent\openai_functions_agent\agent.py`. By default it is called `langchain-test-index`
- Put the data you want Elasticsearch work with in `src\prompty-langchain-agent\packages\openai-functions-agent\openai_functions_agent\data` folder and change the data file name in `agent.py` (change the `local_load` settings as well)
- Create and save your Elasticsearch api key.

#### Dependency requirements
- Python=3.11
- poetry==1.6.1

#### Go to `src\prompty-langchain-agent` folder and do followings:

1. use poetry to install all dependency for the app.

`poetry install --no-interaction --no-ansi`

2. use poetry to install all dependency for the packages:

Go to  `packages\openai-functions-agent` and run:
`poetry install --no-interaction --no-ansi`

3. set environment variables

```
AZURE_OPENAI_ENDPOINT= <your aoai endpoint>
OPENAI_API_VERSION= <your aoai api version>
AZURE_OPENAI_DEPLOYMENT= <your aoai deployment name for chat>
AZURE_OPENAI_EMBEDDING_DEPLOYMENT= <your aoai deployment name for embedding>
ELASTICSEARCH_ENDPOINT = <your ELASTICSEARCH ENDPOINT>
ELASTICSEARCH_API_KEY= <Your encoded ELASTICSEARCH API key>
```

4. Now try to run it on your local
`langchian serve`

1. you can go to http://localhost:8000/openai-functions-agent/playground/ to test.

1. you can mention your index in `input` to tell agent to use search tool.

## Clean up

To clean up all the resources created by this sample:

1. Run `azd down`
2. When asked if you are sure you want to continue, enter `y`
3. When asked if you want to permanently delete the resources, enter `y`

The resource group and all the resources will be deleted.
## Costs
You can estimate the cost of this project's architecture with [Azure's pricing calculator](https://azure.microsoft.com/pricing/calculator/)
 
- Azure OpenAI: Standard tier, GPT and Ada models. Pricing per 1K tokens used, and at least 1K tokens are used per question. [Pricing](https://azure.microsoft.com/pricing/details/cognitive-services/openai-service/)
- Azure AI Speech: Pay as you go, Standard,	$1 per hour [Pricing](https://azure.microsoft.com/en-gb/pricing/details/cognitive-services/speech-services/)

## Securtiy Guidelines

We recommend using keyless authentication for this project. Read more about why you should use managed identities on our [blog](https://techcommunity.microsoft.com/t5/microsoft-developer-community/using-keyless-authentication-with-azure-openai/ba-p/4111521). 

## Resources

- For more information about working with Prompty and Prompt Flow, read the docs [here](https://microsoft.github.io/promptflow/how-to-guides/develop-a-prompty/index.html)
- [azure-search-openai-demo](https://github.com/Azure-Samples/azure-search-openai-demo?tab=readme-ov-file)
- [Develop Python apps that use Azure AI services](https://learn.microsoft.com/azure/developer/python/azure-ai-for-python-developers)
 
## Langsmith

We do support Langsmith and you can follow their doc make it work.

[Get started with LangSmith](https://docs.smith.langchain.com/
)

![langsmith](images/image-2.png)
