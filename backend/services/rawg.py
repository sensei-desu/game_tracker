
import os
import time
import requests
from difflib import SequenceMatcher
from threading import Lock

RAWG_API_KEY = os.getenv("RAWG_API_KEY")
RAWG_BASE_URL = "https://api.rawg.io/api"
CACHE_TTL = 24 * 60 * 60

_cache = {}
_cache_lock = Lock()


def normalize_game_name(name: str) -> str:
    """Normalize a game name for flexible comparison."""
    return "".join(char for char in name.casefold() if char.isalnum())


def find_best_match(game_name: str, results: list):
    """Choose the most relevant RAWG search result."""
    if not results:
        return None

    target = normalize_game_name(game_name)

    def score(game):
        candidate = normalize_game_name(game.get("name", ""))

        if candidate == target:
            return 1.0
        if candidate.startswith(target) or target.startswith(candidate):
            return 0.95

        return SequenceMatcher(None, target, candidate).ratio()

    return max(results, key=score)


def fetch_rawg_requirements(game_name: str):
    """Fetch PC system requirements from RAWG, using a 24-hour cache."""
    if not RAWG_API_KEY:
        return {
            "game": game_name,
            "requirements": [],
            "message": "RAWG API key is not configured.",
        }

    game_name = game_name.strip()

    if not game_name or len(game_name) > 150:
        return {
            "game": game_name,
            "requirements": [],
            "message": "Enter a valid game name.",
        }

    cache_key = game_name.casefold()
    now = time.time()

    with _cache_lock:
        cached = _cache.get(cache_key)
        if cached and now - cached["time"] < CACHE_TTL:
            return cached["data"]

    try:
        response = requests.get(
            f"{RAWG_BASE_URL}/games",
            params={
                "key": RAWG_API_KEY,
                "search": game_name,
                "page_size": 10,
            },
            timeout=10,
        )
        response.raise_for_status()
        results = response.json().get("results", [])

        match = find_best_match(game_name, results)

        if not match or not match.get("id"):
            data = {
                "game": game_name,
                "requirements": [],
                "message": "No matching game found in RAWG.",
            }
        else:
            detail_response = requests.get(
                f"{RAWG_BASE_URL}/games/{match['id']}",
                params={"key": RAWG_API_KEY},
                timeout=10,
            )
            detail_response.raise_for_status()
            details = detail_response.json()

            requirements = []

            for item in details.get("platforms") or []:
                platform = item.get("platform") or {}
                req = item.get("requirements") or {}

                if platform.get("slug") != "pc":
                    continue

                minimum = req.get("minimum")
                recommended = req.get("recommended")

                if minimum or recommended:
                    requirements.append({
                        "platform": platform.get("name", "PC"),
                        "minimum": minimum,
                        "recommended": recommended,
                    })

            data = {
                "game": details.get("name", game_name),
                "rawg_id": match["id"],
                "rawg_url": (
                    f"https://rawg.io/games/{details.get('slug', '')}"
                ),
                "requirements": requirements,
                "message": (
                    None if requirements
                    else "PC requirements are unavailable for this game."
                ),
            }

        with _cache_lock:
            _cache[cache_key] = {
                "time": time.time(),
                "data": data,
            }

        return data

    except requests.HTTPError as exc:
        if exc.response is not None and exc.response.status_code == 429:
            return {
                "game": game_name,
                "requirements": [],
                "message": "RAWG request limit reached. Try again later.",
            }

        return {
            "game": game_name,
            "requirements": [],
            "message": "RAWG returned an API error. Try again later.",
        }

    except requests.RequestException:
        return {
            "game": game_name,
            "requirements": [],
            "message": "RAWG is temporarily unavailable.",
        }

    except (ValueError, TypeError, KeyError, AttributeError):
        return {
            "game": game_name,
            "requirements": [],
            "message": "RAWG returned an unexpected response.",
        }
```
