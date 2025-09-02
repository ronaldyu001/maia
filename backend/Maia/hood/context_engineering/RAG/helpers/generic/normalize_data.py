def normalize_embed_input( query: list[str] | str ) -> list[str]:
    """
    - If query is str: query = list[str]
    - Else: query = list(data)
    - If no data: raise error
    """
    print(f"    - Normalizing inputs...")
    data = [query] if isinstance(query, str) else list(query)

    if query: return query
    else: raise ValueError("No texts to embed.")


def normalize_meta_input(metadata: list[dict] | str, data: list[str]) -> list[dict]:
    """
    - If metadata is None: return empty list[dict]
    - If metadata length does not match data length: raise error
    """
    print(f"    - Aligning metadata...")
    if metadata is None:
        return [{} for _ in data]
    if len(metadata) != len(data):
        raise ValueError("metadata length must match texts length.")