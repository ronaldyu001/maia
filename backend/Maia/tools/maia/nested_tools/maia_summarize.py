from pathlib import Path

from backend.context_engineering.sections._task.variables import SUMMARIZE_CONVERSATION
from backend.context_engineering.custom_windows.summary_window import generate_summarize_context_window
from backend.engine_wrappers.ollama.wrapper_ollama import OllamaModel
from backend.context_engineering.helpers.transcript import create_transcript, trim_transcript
from backend.tools.memory.short_term import load_conversation


async def async_maia_summarize_conversation( llm: str, ctx_wdw_size: int, session_id: str, task=SUMMARIZE_CONVERSATION, memory_type=["short_term", "long_term"] ) -> str:
    """
    Returns
    - a dict with the summary if successful: {"response": summary}.
    - error message if unsuccessful.

    Args
    - llm: the llm name to use.
    - ctx_wdw_size: number of tokens in context window.
    - session_id: session id of conversation to summarize.
    - task: rules for how to summarize conversation. defaults to generic summary.
    - memory_type: specifies whether saving a short term or long term conversation.
    """

    Maia = OllamaModel()


    try:
        # ----- determine memory type and set target path -----
        if memory_type == "short_term":
            TARGET = Path( f"backend/memory/raw/short_term/conversations" ) / f"{session_id}.json"
        elif memory_type == "long_term":
            TARGET = Path( f"backend/memory/raw/long_term/conversations" ) / f"{session_id}.json"
        else:
            raise Exception( f"Invalid memory type given." )
        
        # ----- create context window -----
        window = generate_summarize_context_window(
            llm=llm,
            size=ctx_wdw_size,
            session_id=session_id,
            TASK_FRAMING=SUMMARIZE_CONVERSATION,
            RULES_ratio=0.1,
            TASK_FRAMING_ratio=0.1,
            CONVERSATIONAL_TRANSCRIPT_ratio=0.5
        )

        # ----- get summary from Maia -----
        summary = await Maia.async_chat( prompt=window )
        return summary

    except Exception as err:
        return {"response": f"{type(err).__name__}: {err}"}

