from math import ceil


def generic_trimmer( text: str, llm: str, desired_tokens: int ) -> tuple[ str, str|None ]:
    """
    Generically trims text to desired number of tokens.
    """
    try:
        # ----- generic trim -----
        trimmed_text = text.encode( encoding="utf-8" )[ :ceil(desired_tokens*4) ]
        return str(trimmed_text.decode(encoding="utf-8")), None

    except Exception as err:
        return "Data unsuccessfuly trimmed.", f"{type(err).__name__: {err}}"
