import os
import json
import traceback
from pathlib import Path
from typing import Dict, List, Union
from opentelemetry import trace as otracer

from .core import (
    Frontmatter,
    ModelSettings,
    Prompty,
    PropertySettings,
    TemplateSettings,
    param_hoisting,
)

from .renderers import *
from .parsers import *
from .processors import *

def load_global_config(
    prompty_path: Path = Path.cwd(), configuration: str = "default"
) -> Dict[str, any]:
    # prompty.config laying around?
    prompty_config = list(Path.cwd().glob("**/prompty.json"))

    # if there is one load it
    if len(prompty_config) > 0:
        # pick the nearest prompty.json
        config = sorted(
            [
                c
                for c in prompty_config
                if len(c.parent.parts) <= len(prompty_path.parts)
            ],
            key=lambda p: len(p.parts),
        )[-1]

        span = current_span()
        span.add_event(
            "Using prompty.json for connection information",
            attributes={
                "file": str(Path(config).as_posix()),
                "connection": configuration,
            },
        )
        with open(config, "r") as f:
            c = json.load(f)
            if configuration in c:
                return c[configuration]
            else:
                raise ValueError(f'Item "{configuration}" not found in "{config}"')

    return {}


def headless(
    api: str,
    content: str | List[str] | dict,
    configuration: Dict[str, any] = {},
    parameters: Dict[str, any] = {},
    connection: str = "default",
) -> Prompty:
    # get caller's path (to get relative path for prompty.json)
    caller = Path(traceback.extract_stack()[-2].filename)
    templateSettings = TemplateSettings(type="NOOP", parser="NOOP")
    modelSettings = ModelSettings(
        api=api,
        configuration=Prompty.normalize(
            param_hoisting(
                configuration, load_global_config(caller.parent, connection)
            ),
            caller.parent,
        ),
        parameters=parameters,
    )

    return Prompty(model=modelSettings, template=templateSettings, content=content)


def load(prompty_file: str, configuration: str = "default") -> Prompty:
    p = Path(prompty_file)
    if not p.is_absolute():
        # get caller's path (take into account trace frame)
        caller = Path(traceback.extract_stack()[-3].filename)
        p = Path(caller.parent / p).resolve().absolute()

    # load dictionary from prompty file
    matter = Frontmatter.read_file(p)
    attributes = matter["attributes"]
    content = matter["body"]

    # normalize attribute dictionary resolve keys and files
    attributes = Prompty.normalize(attributes, p.parent)

    # load global configuration
    global_config = Prompty.normalize(
        load_global_config(p.parent, configuration), p.parent
    )
    if "model" not in attributes:
        attributes["model"] = {}
        
    if "configuration" not in attributes["model"]:
        attributes["model"]["configuration"] = global_config
    else:
        attributes["model"]["configuration"] = param_hoisting(
            attributes["model"]["configuration"],
            global_config,
        )

    # pull model settings out of attributes
    try:
        model = ModelSettings(**attributes.pop("model"))
    except Exception as e:
        raise ValueError(f"Error in model settings: {e}")

    # pull template settings
    try:
        if "template" in attributes:
            t = attributes.pop("template")
            if isinstance(t, dict):
                template = TemplateSettings(**t)
            # has to be a string denoting the type
            else:
                template = TemplateSettings(type=t, parser="prompty")
        else:
            template = TemplateSettings(type="jinja2", parser="prompty")
    except Exception as e:
        raise ValueError(f"Error in template loader: {e}")

    print('-----------------------------------', attributes)
    print('-----------------------------------', attributes.pop("inputs").items())
    # formalize inputs and outputs
    if "inputs" in attributes:
        try:
            inputs = {
                k: PropertySettings(**v) for (k, v) in attributes.pop("inputs").items()
            }
        except Exception as e:
            raise ValueError(f"Error in inputs: {e}")
    else:
        inputs = {}
    if "outputs" in attributes:
        try:
            outputs = {
                k: PropertySettings(**v) for (k, v) in attributes.pop("outputs").items()
            }
        except Exception as e:
            raise ValueError(f"Error in outputs: {e}")
    else:
        outputs = {}

    # recursive loading of base prompty
    if "base" in attributes:
        # load the base prompty from the same directory as the current prompty
        span = current_span()
        span.add_event(f"Recursively loading base prompty {attributes['base']}")
        base = load(p.parent / attributes["base"])
        # hoist the base prompty's attributes to the current prompty
        model.api = base.model.api if model.api == "" else model.api
        model.configuration = param_hoisting(
            model.configuration, base.model.configuration
        )
        model.parameters = param_hoisting(model.parameters, base.model.parameters)
        model.response = param_hoisting(model.response, base.model.response)
        attributes["sample"] = param_hoisting(attributes, base.sample, "sample")

        p = Prompty(
            **attributes,
            model=model,
            inputs=inputs,
            outputs=outputs,
            template=template,
            content=content,
            file=p,
            basePrompty=base,
        )
    else:
        p = Prompty(
            **attributes,
            model=model,
            inputs=inputs,
            outputs=outputs,
            template=template,
            content=content,
            file=p,
        )
    return p


def prepare(
    prompt: Prompty,
    inputs: Dict[str, any] = {},
):
    invoker = InvokerFactory()

    inputs = param_hoisting(inputs, prompt.sample)

    if prompt.template.type == "NOOP":
        render = prompt.content
    else:
        # render
        result = invoker(
            "renderer",
            prompt.template.type,
            prompt,
            SimpleModel(item=inputs),
        )
        render = result.item

    if prompt.template.parser == "NOOP":
        result = render
    else:
        # parse
        result = invoker(
            "parser",
            f"{prompt.template.parser}.{prompt.model.api}",
            prompt,
            SimpleModel(item=result.item),
        )

    if isinstance(result, SimpleModel):
        return result.item
    else:
        return result


def run(
    prompt: Prompty,
    content: dict | list | str,
    configuration: Dict[str, any] = {},
    parameters: Dict[str, any] = {},
    raw: bool = False,
):
    invoker = InvokerFactory()

    if configuration != {}:
        prompt.model.configuration = param_hoisting(
            configuration, prompt.model.configuration
        )

    if parameters != {}:
        prompt.model.parameters = param_hoisting(parameters, prompt.model.parameters)

    # execute
    result = invoker(
        "executor",
        prompt.model.configuration["type"],
        prompt,
        SimpleModel(item=content),
    )

    # skip?
    if not raw:
        # process
        result = invoker(
            "processor",
            prompt.model.configuration["type"],
            prompt,
            result,
        )

    if isinstance(result, SimpleModel):
        return result.item
    else:
        return result


def execute(
    prompt: Union[str, Prompty],
    configuration: Dict[str, any] = {},
    parameters: Dict[str, any] = {},
    inputs: Dict[str, any] = {},
    raw: bool = False,
    connection: str = "default",
):

    if isinstance(prompt, str):
        path = Path(prompt)
        if not path.is_absolute():
            # get caller's path (take into account trace frame)
            caller = Path(traceback.extract_stack()[-3].filename)
            path = Path(caller.parent / path).resolve().absolute()
        prompt = load(path, connection)

    invoker = InvokerFactory()
    span = current_span()
    span.set_attribute("invokers", invoker.to_json())

    # prepare content
    content = prepare(prompt, inputs)

    # run LLM model
    result = run(prompt, content, configuration, parameters, raw)

    return result
