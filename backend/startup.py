from Maia.hood.llm_managers.maia_llama3 import Maia_llama3_Manager


"""
startup events.
"""


async def load_llama3():
    """ load llama3 llm """
    Maia_llama3_Manager.get_llm()
