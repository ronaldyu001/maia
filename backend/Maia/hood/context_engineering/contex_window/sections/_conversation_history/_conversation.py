from backend.tools.memory.short_term import load_conversation
from backend.context_engineering.helpers.transcript import create_transcript, trim_transcript, autosize_transcript
from backend.context_engineering.helpers.token_counter import token_counter


def generate_conversational_transcript( llm: str, session_id: str, size: int ) -> list[dict]:
    """
    Generates the conversational transcript for the context window.
    - Target should be current conversation.
    - Size is in tokens.
    """
    try:
        # ----- get conversational history -----
        # get the conversational history as a list of dicts
        history_json_list = load_conversation( session_id=session_id )
        # turn the history to a transcript as a list of strings
        history_str_list = create_transcript( turns=history_json_list )
        # converts from list of strings to a string, does not trim in this case
        ready_transcript = history_json_list
        ready_transcript_str = trim_transcript(  transcript=history_str_list, num_turns=len(history_str_list) )
        
        # ----- if transcript too large, autosize -----
        if token_counter( llm="maia-llama3", text=ready_transcript_str ) > size:
            print( f"trimming..." )
            ready_transcript = autosize_transcript( transcript=history_json_list, size=size, llm=llm )

        return ready_transcript
    
    except Exception as err:
        return False