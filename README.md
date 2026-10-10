# Nexus Game Hub

A Streamlit frontend + FastAPI backend for PC game metadata and regional price comparison.

## What changed in this repair
- Replaced the default-looking UI with a responsive dark gaming dashboard and a small accent-colour selector.
- Fixed price provider mismatch: `services/itad.py` now uses the IsThereAnyDeal API rather than calling CheapShark while claiming to use ITAD.
- Requests ITAD prices for country `IN` and renders the currency returned by the provider. The app does **not** relabel USD values as INR or convert them without source data.
- Added proper HTTP timeouts, safer error handling, game title URL encoding, and a configurable frontend backend URL.
- Added IGDB cover image, genres and release date where available.


## Theme Studio
The frontend includes 15 selectable visual themes: Pure Light, Midnight Pro, Elden Ring — The Lands Between, Spider-Verse, Pixel Arcade, Cyberpunk 2077, Sakura Dreams, Kawaii Anime, Psyduck.exe, Samurai Ink, Nordic Frost, Pastel Dream, Minecraft World, Jujutsu Kaisen — Cursed Energy, and Gamer's Library. The Jujutsu Kaisen theme has Gojo/Infinity and Sukuna/Malevolent Shrine variants. Theme selections are encoded in the URL query parameters (`?theme=...&jjk=...`) so they survive refreshes and can be bookmarked.

The themes change the frontend's palettes, typography, borders, component surfaces and subtle decorative effects. They do not change API behavior or pricing data.

## Environment variables
Backend (`backend/.env` locally, or environment variables in deployment):

```env
TWITCH_CLIENT_ID=your_twitch_client_id
TWITCH_CLIENT_SECRET=your_twitch_client_secret
ITAD_API_KEY=your_isthereanydeal_api_key
```

At least `ITAD_API_KEY` is needed for price data. Twitch credentials are needed for IGDB metadata. Never commit `.env` or API keys.

Frontend (optional):

```env
BACKEND_API_URL=https://your-backend.onrender.com
```

## Run locally
From the project root, in separate terminals:

```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
uvicorn main:app --reload
```

```bash
cd frontend
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
streamlit run app.py
```

## Deploy
- Backend root directory: `backend`; start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`.
- Frontend root directory: `frontend`; start command: `streamlit run app.py --server.port $PORT --server.address 0.0.0.0`.
- Set the environment variables in each deployment service. Set `BACKEND_API_URL` on the frontend to the deployed backend URL.

## Important price note
The ITAD API accepts a two-letter region code. This app requests `IN`, but storefront coverage and the currency returned for individual offers depend on the provider. It displays the provider's actual currency; it does not pretend a USD amount is INR. If an offer comes back in a non-INR currency, it is explicitly shown as that currency.

Pricing data is provided by IsThereAnyDeal API. This project is independent and is not affiliated with IsThereAnyDeal or IGDB.
