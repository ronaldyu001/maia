from math import ceil

from backend.context_engineering.helpers.token_counter import token_counter
from backend.context_engineering.sections._rules._rules import generate_rules
from backend.context_engineering.sections._tool_contract._tool_contract import generate_tool_contract
from backend.context_engineering.sections._conversation_history._conversation import generate_conversational_transcript
from backend.context_engineering.sections._task._task import generate_task

def generate_context_window( llm: str, size: int, session_id: str ) -> list[dict]:
    """
    Generates the context window for Maia.\n
    This supports the following llms (must enter exactly as spelled in ""). \n
    - "maia-llama3"
    """
    # ----- calculate size of each section of context window -----
    # leave 30% of window for Maia's reply -----
    size_TOTAL = ceil( size * 0.7 )

    size_RULES = ceil( size_TOTAL * 0.075 )
    size_TOOL_CONTRACT = ceil( size_TOTAL * 0.1 )
    size_TASK_FRAMING = ceil( size_TOTAL * 0.1 )
    size_PINNED_FACTS = ceil( size_TOTAL * 0.075 )
    size_LONGTERM_RECALL = ceil( size_TOTAL * 0.25 )
    size_CONVERSATIONAL_TRANSCRIPT = ceil( size_TOTAL * 0.4 )


    # ----- Rules [ 5% ] -----
    RULES = generate_rules( llm=llm, size=size_RULES, session_id=session_id )

    # ----- Tool contract [ 5% ] -----
    TOOL_CONTRACT = generate_tool_contract( llm=llm, size=size_TOOL_CONTRACT )

    # ----- Task Framing [ 5% ] -----
    TASK = generate_task( llm=llm, size=size_TASK_FRAMING )

    # ----- Pinned Facts [ 10% ] -----
    PINNED_FACTS = False

    # ----- Goals [ 10% ] -----
    GOALS = False
    
    # ----- Longterm Recall [ 25% ] -----
    LONGTERM_RECALL = False

    # ----- Conversational History [ 40% ] -----
    CONVERSATIONAL_HISTORY = generate_conversational_transcript( llm=llm, session_id=session_id, size=size_CONVERSATIONAL_TRANSCRIPT )

    # ----- Context Window -----
    CONTENT = [ RULES, TOOL_CONTRACT, TASK, PINNED_FACTS, GOALS, LONGTERM_RECALL, CONVERSATIONAL_HISTORY ]
    CONTEXT_WINDOW = []
    for section in CONTENT:
        if isinstance( section, list ):
            CONTEXT_WINDOW += section

    print( CONTEXT_WINDOW )

    # ----- Summary -----
    print( f"Sizes:\n" )
    print( f"Rules: ~{ceil(len(str(RULES))/4)} tokens\n" )
    print( f"Tool Contract: ~{ceil(len(str(TOOL_CONTRACT))/4)} tokens\n" )
    print( f"Conversational Transcript: ~{ceil(len(str(CONVERSATIONAL_HISTORY))/4)} tokens\n" )

    return CONTEXT_WINDOW