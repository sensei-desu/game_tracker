# Nexus Game Hub — Static Frontend

This is a static HTML/CSS/JavaScript frontend for Render Static Site hosting. It includes 15 selectable visual themes, theme-specific pointer cursors, and a preconfigured FastAPI base URL.

## Deploy on Render
- Root Directory: `frontend` (if this folder is at repository root/frontend)
- Build Command: leave empty
- Publish Directory: `.`

Backend URL: `https://game-tracker-19sp.onrender.com`
Frontend URL expected: `https://fronttt-h5fz.onrender.com`

The theme backgrounds use three bundled local artworks (Elden Ring, Spider-Verse, Minecraft) and remote Unsplash photographs for the other themes; an internet connection is needed for those remote backgrounds.

Ensure the FastAPI backend allows the exact frontend origin through CORS. Keep the existing backend routes unchanged. The search uses `/api/game/{game_name}`; if your backend uses a different route, update that path in `app.js`.
