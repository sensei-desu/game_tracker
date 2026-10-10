import requests


def get_twitch_token(client_id, client_secret):
    try:
        response = requests.post(
            "https://id.twitch.tv/oauth2/token",
            params={"client_id": client_id, "client_secret": client_secret, "grant_type": "client_credentials"},
            timeout=12,
        )
        response.raise_for_status()
        return response.json().get("access_token")
    except (requests.RequestException, ValueError):
        return None


def fetch_igdb_data(game_name, client_id, access_token):
    if not client_id or not access_token:
        return None
    headers = {"Client-ID": client_id, "Authorization": f"Bearer {access_token}"}
    body = f'search "{game_name.replace(chr(34), "")}"; fields name,summary,first_release_date,genres.name,platforms.name,cover.image_id,websites.url; limit 1;'
    try:
        response = requests.post("https://api.igdb.com/v4/games", headers=headers, data=body, timeout=12)
        response.raise_for_status()
        results = response.json()
        if not results:
            return None
        game = results[0]
        cover_id = (game.get("cover") or {}).get("image_id")
        if cover_id:
            game["cover_url"] = f"https://images.igdb.com/igdb/image/upload/t_cover_big/{cover_id}.jpg"
        return game
    except (requests.RequestException, ValueError):
        return None
