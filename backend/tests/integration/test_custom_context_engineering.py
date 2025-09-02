import pytest

from backend.Maia.hood.context_engineering.contex_window.custom_context_window import generate_custom_context_window
from backend.Maia.hood.context_engineering.config import RULES, TOOL_CONTRACT
# Note: We need to update this path once we confirm where _conversation_history is moved to
from backend.Maia.hood.context_engineering.sections._conversation_history._conversation import generate_conversational_transcript


def test_custom_window():
    try:
        llm = "maia-llama3"
        session_id = "1ef6eec9-87aa-4591-9bc8-11df4108cd13"
        tkns = 8192
        CONVERSATIONAL_TRANSCRIPT_ratio = 0.4

        generate_custom_context_window(
            llm=llm,
            size=tkns,
            session_id=session_id,

            RULES=RULES,
            TOOL_CONTRACT=TOOL_CONTRACT,
            TASK_FRAMING="",
            PINNED_FACT="",
            GOALS="",
            LONGTERM_RECALL="",
            CONVERSATIONAL_TRANSCRIPT="",
            RULES_ratio=0.1,
            TOOL_CONTRACT_ratio=0.1,
            TASK_FRAMING_ratio=0,
            PINNED_FACT_ratio=0,
            GOALS_ratio=0,
            LONGTERM_RECALL_ratio=0,
            CONVERSATIONAL_TRANSCRIPT_ratio=CONVERSATIONAL_TRANSCRIPT_ratio
        )
        
    except Exception as err:
        pytest.fail( reason=err )