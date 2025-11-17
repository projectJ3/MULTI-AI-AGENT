# app/core/ai_agent.py
from typing import Any, List, Dict, Optional
from app.config.settings import settings
from app.common.logger import get_logger

logger = get_logger(__name__)

# Try to import the Groq-specific exception class if available
try:
    # groq.BadRequestError is raised for tool failures in the Groq client
    from groq import BadRequestError as GroqBadRequestError  # type: ignore
except Exception:
    GroqBadRequestError = None  # type: ignore

def _import_llm_components() -> Dict[str, Any]:
    """
    Lazy import of third-party LLM/tool libraries. Raises ImportError with a
    clear message if required packages are missing or fail to import.
    """
    try:
        # These package names match how you referenced them in your code.
        # If pip install fails for any of these names, tell me the pip error.
        from langchain_groq import ChatGroq  # type: ignore
        from langchain_tavily import TavilySearch  # type: ignore
        from langgraph.prebuilt import create_react_agent  # type: ignore
        from langchain_core.messages import AIMessage, HumanMessage  # type: ignore
        from langchain_core.prompts import ChatPromptTemplate  # type: ignore

        return {
            "ChatGroq": ChatGroq,
            "TavilySearch": TavilySearch,
            "create_react_agent": create_react_agent,
            "AIMessage": AIMessage,
            "HumanMessage": HumanMessage,
            "ChatPromptTemplate": ChatPromptTemplate,
        }
    except Exception as e:
        logger.exception("Failed to import LLM/tool libraries (langchain_groq/langchain_tavily/langgraph/langchain_core).")
        raise ImportError(
            "Missing or broken LLM/tool dependencies. Please install the required packages "
            "(e.g. langchain_groq, langchain_tavily, langgraph, langchain_core) and restart. "
            "See server logs for full import error."
        ) from e

def make_tools(allow_search: bool) -> List[Any]:
    """
    Build and return a list of tools for the agent.
    If allow_search is False, return an empty list.
    """
    if not allow_search:
        return []

    comps = _import_llm_components()
    TavilySearch = comps["TavilySearch"]

    try:
        # Example configuration for TavilySearch — adjust if your API expects different args
        tavily_tool = TavilySearch(
            max_results=3,
            search_depth="advanced",
            include_answer=True,
            include_raw_content=False
        )
        return [tavily_tool]
    except Exception as e:
        logger.exception("Failed to initialize TavilySearch tool")
        # Return empty list rather than failing hard — we'll fallback later if needed
        return []

def _extract_failed_generation_from_groq(exc: Exception) -> str:
    """
    Try to extract the 'failed_generation' or a meaningful message from a Groq BadRequestError.
    Returns a short string summarizing the cause.
    """
    try:
        resp = getattr(exc, "response", None)
        # If response is already a dict-like object
        if isinstance(resp, dict):
            err = resp.get("error", {}) or {}
            fg = err.get("failed_generation")
            if fg:
                return str(fg)
            return err.get("message") or str(resp)
        # If response is a requests.Response-like object with .json()
        try:
            j = resp.json()  # type: ignore
            err = j.get("error", {}) if isinstance(j, dict) else {}
            return err.get("failed_generation") or err.get("message") or str(j)
        except Exception:
            # Fallback to stringifying the exception/response
            return str(resp) if resp is not None else str(exc)
    except Exception:
        return str(exc)

def _parse_agent_response(response: Any, AIMessage: Any) -> str:
    """
    Convert whatever the agent returned into a single string.
    Expects 'response' to be an object/dict with 'messages' or similar structure.
    """
    try:
        if not response:
            return ""

        # Many agent frameworks return a dict with "messages" where each message
        # may be a LangChain message object or a plain dict with 'content'
        messages = response.get("messages", None) if isinstance(response, dict) else None

        if messages is None:
            # maybe the agent returned a plain string
            if isinstance(response, str):
                return response
            # try last resort
            return str(response)

        # collect contents from AIMessage instances or dicts
        ai_texts: List[str] = []
        for m in messages:
            # If m is an AIMessage-like object
            try:
                if isinstance(m, AIMessage):
                    ai_texts.append(m.content)
                    continue
            except Exception:
                pass
            # If m is a dict-like with 'content'
            if isinstance(m, dict) and "content" in m:
                ai_texts.append(m["content"])
            else:
                # fallback string conversion
                ai_texts.append(str(getattr(m, "content", m)))
        # prefer the last AI text
        if ai_texts:
            return ai_texts[-1]
        return ""
    except Exception:
        logger.exception("Failed while parsing agent response")
        return str(response)

def get_response_from_ai_agents(llm_id: str, query: Any, allow_search: bool, system_prompt: str) -> str:
    """
    Main entrypoint used by your API. Returns a single string response from the configured agent.
    Behavior:
    - Tries to call the agent with tools (if allow_search True).
    - If Groq tool call fails (BadRequestError / tool_use_failed), logs details and retries WITHOUT tools.
    - Raises ImportError if LLM/tool packages are not installed.
    - Raises other exceptions if both primary and fallback fail.
    """
    comps = _import_llm_components()
    ChatGroq = comps["ChatGroq"]
    create_react_agent = comps["create_react_agent"]
    AIMessage = comps["AIMessage"]
    HumanMessage = comps["HumanMessage"]
    ChatPromptTemplate = comps["ChatPromptTemplate"]

    # instantiate model
    try:
        llm = ChatGroq(model=llm_id)
    except Exception:
        logger.exception("Failed to instantiate ChatGroq model with id: %s", llm_id)
        raise

    # prepare prompt template (simple two-part prompt: system + placeholder for messages)
    try:
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt or settings.DEFAULT_SYSTEM_PROMPT),
            ("placeholder", "{messages}")
        ])
    except Exception:
        logger.exception("Failed to build ChatPromptTemplate")
        # fallback: proceed without template (some versions may not need it)
        prompt = None

    # create tools (may be [])
    tools = make_tools(allow_search)

    def _build_agent(tools_list: List[Any]):
        try:
            return create_react_agent(
                model=llm,
                tools=tools_list,
                prompt=prompt
            )
        except Exception:
            logger.exception("Failed to create react agent (tools count=%d)", len(tools_list))
            raise

    # Build agent with initial tool set
    agent = _build_agent(tools)

    # Normalize messages into list of HumanMessage
    if isinstance(query, str):
        query_msgs = [HumanMessage(content=query)]
    elif isinstance(query, list):
        query_msgs = [HumanMessage(content=q) if not isinstance(q, HumanMessage) else q for q in query]
    else:
        # best-effort convert to string
        query_msgs = [HumanMessage(content=str(query))]

    state = {"messages": query_msgs}

    # Try invoking agent (primary attempt)
    try:
        response = agent.invoke(state)
        # parse response to text
        return _parse_agent_response(response, AIMessage)
    except Exception as exc:
        # If it's a Groq tool failure and we have the Groq exception type, extract helpful info
        if GroqBadRequestError is not None and isinstance(exc, GroqBadRequestError):
            failed_info = _extract_failed_generation_from_groq(exc)
            logger.error("Groq BadRequestError during tool call. failed_generation: %s", failed_info, exc_info=True)

            # Attempt
