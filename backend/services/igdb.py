
import re
from difflib import SequenceMatcher

import requests


def get_twitch_token(client_id, client_secret):
    try:
        response = requests.post(
            "https://id.twitch.tv/oauth2/token",
            params={
                "client_id": client_id,
                "client_secret": client_secret,
                "grant_type": "client_credentials",
            },
            timeout=12,
        )
        response.raise_for_status()
        return response.json().get("access_token")
    except (requests.RequestException, ValueError):
        return None


def normalize_title(title):
    """Normalize titles for case- and punctuation-insensitive matching."""
    return re.sub(r"[^a-z0-9]+", " ", title.lower()).strip()


def fetch_igdb_data(game_name, client_id, access_token):
    if not client_id or not access_token:
        return None

    headers = {
        "Client-ID": client_id,
        "Authorization": f"Bearer {access_token}",
    }

    # Remove double quotes so the search query cannot be broken.
    safe_name = game_name.replace('"', "").strip()
    if not safe_name:
        return None

    body = (
        f'search "{safe_name}"; '
        "fields id,name,summary,first_release_date,"
        "genres.name,platforms.name,cover.image_id,websites.url; "
        "limit 10;"
    )

    try:
        response = requests.post(
            "https://api.igdb.com/v4/games",
            headers=headers,
            data=body,
            timeout=12,
        )
        response.raise_for_status()
        results = response.json()

        if not results:
            return None

        query = normalize_title(safe_name)

        def rank_game(game):
            title = normalize_title(game.get("name", ""))

            # Exact title matches always rank above related titles.
            if title == query:
                return (0, 0)

            # Prefer titles beginning with the requested title.
            if title.startswith(query + " "):
                return (1, len(title) - len(query))

            # Then prefer other close title matches.
            similarity = SequenceMatcher(
                None, query, title
            ).ratio()

            return (2, -similarity)

        results.sort(key=rank_game)
        game = results[0]

        cover_id = (game.get("cover") or {}).get("image_id")
        if cover_id:
            game["cover_url"] = (
                "https://images.igdb.com/igdb/image/upload/"
                f"t_cover_big/{cover_id}.jpg"
            )

        return game

    except (requests.RequestException, ValueError):
        return None
