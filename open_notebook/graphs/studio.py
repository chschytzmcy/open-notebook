from typing import Any, Optional

from loguru import logger

from ai_prompter import Prompter
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.runnables import RunnableConfig
from langgraph.graph import END, START, StateGraph
from typing_extensions import TypedDict

from open_notebook.ai.provision import provision_langchain_model
from open_notebook.utils.error_classifier import classify_error
from open_notebook.utils.text_utils import clean_thinking_content, extract_text_content


class FlashcardState(TypedDict):
    prompt: str
    parser: Optional[Any]
    input_text: str
    output: str


class MindMapState(TypedDict):
    prompt: str
    parser: Optional[Any]
    input_text: str
    output: str


async def generate_flashcards(state: dict, config: RunnableConfig) -> dict:
    logger.info("generate_flashcards: Starting")
    content = state["input_text"]
    template_name = state.get("template_name", "studio/flashcard")
    logger.info(f"generate_flashcards: content length = {len(content) if content else 0}")
    logger.info(f"generate_flashcards: template_name = {template_name}")

    system_prompt = Prompter(
        prompt_template=template_name
    ).render(data={"input_text": content})
    logger.info(f"generate_flashcards: system_prompt length = {len(system_prompt) if system_prompt else 0}")

    payload = [SystemMessage(content=system_prompt)] + [HumanMessage(content=content)]
    logger.info(f"generate_flashcards: payload has {len(payload)} messages")

    model_id = config.get("configurable", {}).get("model_id")
    logger.info(f"generate_flashcards: model_id from config = {model_id}")

    chain = await provision_langchain_model(
        str(payload),
        model_id,
        "transformation",
        max_tokens=8000,
    )
    logger.info(f"generate_flashcards: chain type = {type(chain).__name__}")

    try:
        response = await chain.ainvoke(payload)
        logger.info(f"generate_flashcards: response received, type = {type(response)}")
    except Exception as e:
        logger.error(f"generate_flashcards: LLM invocation failed: {str(e)}")
        error_class, user_message = classify_error(e)
        raise error_class(user_message) from e

    output = clean_thinking_content(extract_text_content(response.content))
    logger.info(f"generate_flashcards: output length = {len(output) if output else 0}")
    return {"output": output}


async def generate_mindmap(state: dict, config: RunnableConfig) -> dict:
    logger.info("generate_mindmap: Starting")
    content = state["input_text"]
    template_name = state.get("template_name", "studio/mindmap")
    logger.info(f"generate_mindmap: content length = {len(content) if content else 0}")
    logger.info(f"generate_mindmap: template_name = {template_name}")

    system_prompt = Prompter(
        prompt_template=template_name
    ).render(data={"input_text": content})
    logger.info(f"generate_mindmap: system_prompt length = {len(system_prompt) if system_prompt else 0}")

    payload = [SystemMessage(content=system_prompt)] + [HumanMessage(content=content)]
    logger.info(f"generate_mindmap: payload has {len(payload)} messages")

    model_id = config.get("configurable", {}).get("model_id")
    logger.info(f"generate_mindmap: model_id from config = {model_id}")

    chain = await provision_langchain_model(
        str(payload),
        model_id,
        "transformation",
        max_tokens=4000,
    )
    logger.info(f"generate_mindmap: chain type = {type(chain).__name__}")

    try:
        response = await chain.ainvoke(payload)
        logger.info(f"generate_mindmap: response received, type = {type(response)}")
    except Exception as e:
        logger.error(f"generate_mindmap: LLM invocation failed: {str(e)}")
        error_class, user_message = classify_error(e)
        raise error_class(user_message) from e

    output = clean_thinking_content(extract_text_content(response.content))
    logger.info(f"generate_mindmap: output length = {len(output) if output else 0}")
    return {"output": output}


flashcard_graph = StateGraph(FlashcardState).add_node("agent", generate_flashcards).add_edge(START, "agent").add_edge("agent", END).compile()
mindmap_graph = StateGraph(MindMapState).add_node("agent", generate_mindmap).add_edge(START, "agent").add_edge("agent", END).compile()