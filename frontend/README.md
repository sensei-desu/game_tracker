# Nexus Game Hub — Split Frontend

This frontend is plain HTML, CSS and JavaScript (no Streamlit). It calls the existing FastAPI endpoint `GET /api/game/{game_name}` and preserves the IGDB + IsThereAnyDeal response shape.

## Files
- `index.html` — semantic page layout and controls
- `styles.css` — layout, responsive styling and theme effects
- `themes.js` — theme palette/visual definitions
- `app.js` — theme selection, backend connection, search and result rendering
- `assets/themes/` — local image assets currently bundled for Elden Ring, Spider-Verse and Minecraft World

## Run locally
Use any static server from the `frontend` directory, for example:

```bash
python -m http.server 5500
```

Open `http://localhost:5500`. Use the ⚙ button to set the URL for your running FastAPI backend. Do not open `index.html` directly as a `file://` URL.

## Deploy
Deploy the `frontend` directory as a static site (Render Static Site works). The backend stays a separate Render Web Service running FastAPI. Configure the backend URL in the page's settings button. Configure `ITAD_API_KEY` and/or `TWITCH_CLIENT_ID` + `TWITCH_CLIENT_SECRET` on the backend service, not in frontend JavaScript.

## Theme artwork note
All 15 themes have distinct palettes and theme-specific visual treatments. The current ZIP includes individual bundled artwork for 3 themes; the remaining 12 currently use their own CSS visual treatments and need separate custom background image assets for full photographic/artwork coverage.
