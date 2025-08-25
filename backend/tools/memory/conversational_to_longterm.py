import json
from pathlib import Path

from backend.tools.maia.copy_file import copy_file



def conversational_to_longterm( session_id: str ) -> bool:
    """
    Saves short term transcript to long term memory.\n
    Returns true if successful.\n
    Does not delete the short term memory.
    """
    CONVERSATION = Path( f"backend/memory/raw/short_term/conversations/{session_id}.json" )
    LONG_TERM = Path( f"backend/memory/raw/long_term/conversations" )
    
    try:
        # ----- if conversational memory DNE, do nothing -----
        if not CONVERSATION.exists():
            raise Exception( f"{session_id}.json does not exist in short term memory" )

        # ----- move conversation to long term -----
        else:
            if not copy_file( from_path=CONVERSATION, to_path=LONG_TERM ):
                raise Exception( f"failed to move {session_id}.json" )
            
        return True

    except Exception as err:
        return False