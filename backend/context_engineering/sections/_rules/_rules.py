from backend.context_engineering.variables import RULES
from backend.context_engineering.helpers.token_counter import token_counter
from backend.context_engineering.helpers.generic_trimmer import generic_trimmer


def generate_rules( llm: str, size: int, session_id: str, rules=RULES ) -> list[dict] | None:
    """
    This supports the following llms (must enter exactly as spelled in ""). \n
    - "maia-llama3"

    llm must be specified for precise token allotment.\n
    returns a lhm ist with a dict
    """
    rules += f"The current session id is: {session_id}"
    try:
        # ----- if rules is within token allotment, return rules -----
        if token_counter( llm=llm ,text=rules ) <= size:
            return [{ "role":"system", "content":rules }]
        
        # ----- if rules too big, trim down to desired size and return -----
        else:
            TRIMMED_RULES, error = generic_trimmer( text=rules, llm=llm, desired_tokens=size )
            return [{ "role":"system", "content":TRIMMED_RULES }]
        
    except Exception as err:
        return None
