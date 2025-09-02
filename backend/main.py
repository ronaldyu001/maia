from fastapi import FastAPI
from backend.Maia.hood.engine_wrappers.ollama.wrapper_ollama import OllamaModel
from backend.routes import chat
from fastapi.middleware.cors import CORSMiddleware

from backend.startup import load_llama3


# ----- create FastAPI app -----
app = FastAPI()
model = OllamaModel( model_name="llama3" )


# ----- Allow your frontend origin(s) -----
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],   # <-- must allow OPTIONS
    allow_headers=["*"],   # <-- allow Content-Type: application/json, etc.
)


# ----- register routes -----
app.include_router( chat.router )


# ----- startup events -----
@app.on_event( event_type="startup" )
async def startup_events():
    """ startup events. """
    print( f"Performing startup events..." )
    await load_llama3()