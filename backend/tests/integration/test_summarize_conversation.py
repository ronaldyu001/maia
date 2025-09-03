import pytest
import asyncio

from Maia.tools.maia.nested_tools.maia_summarize import async_maia_summarize_conversation


@pytest.mark.asyncio
async def test_summarize_conversation():
    try:
        print("testing.")

        result = await async_maia_summarize_conversation(
            llm="maia-llama3", 
            ctx_wdw_size=8192, 
            session_id="1ef6eec9-87aa-4591-9bc8-11df4108cd13", 
            memory_type="short_term" )
        
        print(result)
    except Exception as err:
        pytest.fail()