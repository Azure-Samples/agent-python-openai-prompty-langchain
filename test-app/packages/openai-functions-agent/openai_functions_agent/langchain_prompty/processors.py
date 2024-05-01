from typing import List
from pydantic import BaseModel
from openai.types.completion import Completion
from openai.types.chat.chat_completion import ChatCompletion
from openai.types.create_embedding_response import CreateEmbeddingResponse
from .core import Invoker, InvokerFactory, Prompty, SimpleModel

from pydantic import BaseModel


class ToolCall(BaseModel):
    id: str
    name: str
    arguments: str


class OpenAIProcessor(Invoker):
    def __init__(self, prompty: Prompty) -> None:
        self.prompty = prompty

    def invoke(self, data: BaseModel) -> BaseModel:
        assert (
            isinstance(data, ChatCompletion)
            or isinstance(data, Completion)
            or isinstance(data, CreateEmbeddingResponse)
        )
        if isinstance(data, ChatCompletion):
            response = data.choices[0].message
            # tool calls available in response
            if response.tool_calls:
                return SimpleModel[List[ToolCall]](
                    item=[
                        ToolCall(
                            id=tool_call.id,
                            name=tool_call.function.name,
                            arguments=tool_call.function.arguments,
                        )
                        for tool_call in response.tool_calls
                    ]
                )
            else:
                return SimpleModel[str](item=response.content)

        elif isinstance(data, Completion):
            return SimpleModel[str](item=data.choices[0].text)
        elif isinstance(data, CreateEmbeddingResponse):
            if len(data.data) == 0:
                raise ValueError("Invalid data")
            elif len(data.data) == 1:
                return SimpleModel[List[float]](item=data.data[0].embedding)
            else:
                return SimpleModel[List[List[float]]](
                    item=[item.embedding for item in data.data]
                )
        else:
            raise ValueError("Invalid data type")


InvokerFactory().register_processor("openai", OpenAIProcessor)
InvokerFactory().register_processor("azure", OpenAIProcessor)
