import os
from urllib.parse import quote
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from services.igdb import fetch_igdb_data, get_twitch_token
from services.itad import fetch_itad_data

load_dotenv()
app = FastAPI(title="Nexus Game Hub API", version="1.1")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_credentials=False,
    allow_methods=["GET", "OPTIONS"], allow_headers=["*"],
)
CLIENT_ID = os.getenv("TWITCH_CLIENT_ID")
CLIENT_SECRET = os.getenv("TWITCH_CLIENT_SECRET")
ITAD_API_KEY = os.getenv("ITAD_API_KEY")

@app.get("/")
def root():
    return {"status": "online", "app": "Nexus Game Hub API", "region": "IN"}

@app.get("/api/game/{game_name:path}")
def get_game_data(game_name: str):
    game_name = game_name.strip()
    if not game_name:
        raise HTTPException(status_code=400, detail="Enter a game title.")
    token = get_twitch_token(CLIENT_ID, CLIENT_SECRET) if CLIENT_ID and CLIENT_SECRET else None
    igdb_data = fetch_igdb_data(game_name, CLIENT_ID, token) if token else None
    prices, history, itad_game = fetch_itad_data(game_name, ITAD_API_KEY) if ITAD_API_KEY else (None, None, None)
    if not igdb_data and not prices and not itad_game:
        if not ITAD_API_KEY and not (CLIENT_ID and CLIENT_SECRET):
            raise HTTPException(status_code=503, detail="Configure ITAD_API_KEY and/or Twitch IGDB credentials in the backend environment.")
        raise HTTPException(status_code=404, detail="No matching game found. Try the official game title.")
    return {"igdb": igdb_data, "prices": prices, "history": history, "itad_game": itad_game, "region": "IN"}
