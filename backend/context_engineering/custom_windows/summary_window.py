from math import ceil, floor

from backend.context_engineering.sections._rules._rules import generate_rules
from backend.context_engineering.sections._tool_contract._tool_contract import generate_tool_contract
from backend.context_engineering.sections._conversation_history._conversation import generate_conversational_transcript
from backend.context_engineering.sections._task._task import generate_task
from backend.context_engineering.helpers.transcript import create_transcript, trim_transcript


def generate_summarize_context_window( 
    llm: str, 
    size: int, 
    session_id: str,
    # context
    RULES="",
    TOOL_CONTRACT="",
    TASK_FRAMING="",
    PINNED_FACTS="",
    GOALS="",
    LONGTERM_RECALL="",
    CONVERSATIONAL_TRANSCRIPT="",
    # percent of context window
    RULES_ratio=0,
    TOOL_CONTRACT_ratio=0.0,
    TASK_FRAMING_ratio=0.0,
    PINNED_FACTS_ratio=0.0,
    GOALS_ratio=0.0,
    LONGTERM_RECALL_ratio=0.0,
    CONVERSATIONAL_TRANSCRIPT_ratio=0.0
) -> list[dict] | bool:
    """
    Returns
    - context window as a list[dict]

    Arguments
    - llm: the llm model to use
    

    Default context available for
    - RULES
    - TOOL_CONTRACT
    - TASK_FRAMING
    - CONVERSATION_HISTORY (based on given session id)\n

    Default size set to 0 for all context groups.

    This supports the following llms (must enter exactly as spelled in ""). \n
    - "maia-llama3"
    """
    CONTENT = [ "RULES", "TOOL_CONTRACT", "TASK_FRAMING", "PINNED_FACTS", "GOALS", "LONGTERM_RECALL", "CONVERSATIONAL_HISTORY" ]
    RATIOS = [ RULES_ratio, TOOL_CONTRACT_ratio, TASK_FRAMING_ratio, PINNED_FACTS_ratio, GOALS_ratio, LONGTERM_RECALL_ratio, CONVERSATIONAL_TRANSCRIPT_ratio ]
    
    try:
        # ----- make sure ratios add to 1 -----
        if not sum( RATIOS ) <= 1:
            raise Exception( f"Sum of given ratios can't exceed 1." )

        # ----- calculate size of each section of context window -----
        # leave 30% of window for Maia's reply -----
        CONTEXT_WINDOW_tkns = ceil( size * 0.7 )
        CONTENT_tkns = {}
        for entry, ratio in zip( CONTENT, RATIOS ):
            CONTENT_tkns[ entry ] = floor( CONTEXT_WINDOW_tkns * ratio )

        # ----- generate content -----
        RULES = generate_rules( llm=llm, size=CONTENT_tkns["RULES"], session_id=session_id )
        TOOL_CONTRACT = generate_tool_contract( llm=llm, size=CONTENT_tkns["TOOL_CONTRACT"] )
        TASK = generate_task( llm=llm, size=CONTENT_tkns["TASK_FRAMING"], task=TASK_FRAMING )
        conversation_list_str = create_transcript(generate_conversational_transcript( llm=llm, session_id=session_id, size=CONTENT_tkns["CONVERSATIONAL_HISTORY"] ))
        conversation_str = trim_transcript( transcript=conversation_list_str, num_turns=len(conversation_list_str) )
        CONVERSATIONAL_HISTORY = [{
            "role": "system",
            "content": conversation_str
            }]

        # ----- Context Window -----
        CONTENT = [ RULES, TOOL_CONTRACT, TASK, PINNED_FACTS, GOALS, LONGTERM_RECALL, CONVERSATIONAL_HISTORY ]
        CONTEXT_WINDOW = []
        for section in CONTENT:
            if isinstance( section, list ):
                CONTEXT_WINDOW += section

        print( CONTEXT_WINDOW )

        # ----- Summary -----
        print( f"Sizes:" )
        print( f"\nRules: ~{ceil(len(str(RULES))/4)} tokens\n" )
        print( f"Tool Contract: ~{ceil(len(str(TOOL_CONTRACT))/4)} tokens\n" )
        print( f"Conversational Transcript: ~{ceil(len(str(CONVERSATIONAL_HISTORY))/4)} tokens\n" )

    except Exception as err:
        return False

    return CONTEXT_WINDOW