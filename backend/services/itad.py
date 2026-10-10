"""IsThereAnyDeal pricing service, requested in the Indian region (INR where available)."""
import requests
from difflib import SequenceMatcher

BASE = "https://api.isthereanydeal.com"
TIMEOUT = 12


def _headers(api_key):
    return {"ITAD-API-Key": api_key, "Accept": "application/json", "User-Agent": "NexusGameHub/1.0"}


def _get(url, api_key, params=None):
    response = requests.get(url, headers=_headers(api_key), params=params or {}, timeout=TIMEOUT)
    response.raise_for_status()
    return response.json()


def _post(url, api_key, params=None, payload=None):
    response = requests.post(url, headers={**_headers(api_key), "Content-Type": "application/json"}, params=params or {}, json=payload, timeout=TIMEOUT)
    response.raise_for_status()
    return response.json()


def fetch_itad_data(game_name, api_key=None):
    """Return normalized prices/history from ITAD's India-region endpoints.

    Never converts a foreign-currency amount into INR and labels it as a local price.
    The requested region is IN; each returned price retains the currency supplied by ITAD.
    """
    if not api_key:
        return None, None, None
    try:
        search = _get(f"{BASE}/games/search/v1", api_key, {"title": game_name, "results": 10})
        if not search:
            return None, None, None
        # Prefer exact/near-exact base game matches and avoid selecting DLC when possible.
        query = game_name.strip().casefold()
        candidates = sorted(search, key=lambda item: (
            0 if str(item.get("type", "game")).lower() == "game" else 1,
            -SequenceMatcher(None, query, str(item.get("title", "")).casefold()).ratio()
        ))
        chosen = candidates[0]
        game_id = chosen.get("id")
        if not game_id:
            return None, None, None

        # The prices endpoint returns the full store list; overview is useful for the
        # best-current/lowest summary but only returns a single offer per game.
        price_rows = _post(f"{BASE}/games/prices/v3", api_key, {"country": "IN"}, [game_id])
        entry = next((x for x in price_rows if x.get("id") == game_id), None)
        info = _get(f"{BASE}/games/info/v2", api_key, {"id": game_id})
        deals = []
        history = None
        if entry:
            for item in entry.get("deals", []):
                current = item.get("price") or {}
                regular = item.get("regular") or {}
                deals.append({
                    "shop": {"name": (item.get("shop") or {}).get("name", "Store")},
                    "price": {"amount": current.get("amount"), "currency": current.get("currency", "")},
                    "regular": {"amount": regular.get("amount"), "currency": regular.get("currency", "")},
                    "cut": item.get("cut", 0),
                    "url": item.get("url"),
                    "store_low": item.get("storeLow"),
                    "history_low": item.get("historyLow"),
                })
            deals.sort(key=lambda x: float(x.get("price", {}).get("amount") or 1e15))
            all_time = (entry.get("historyLow") or {}).get("all")
            lowest_deal = min(deals, key=lambda x: float(x.get("price", {}).get("amount") or 1e15)) if deals else {}
            history = {
                "low": {
                    "amount": all_time.get("amount") if all_time else None,
                    "currency": all_time.get("currency", "") if all_time else "",
                    "shop": {"name": (lowest_deal.get("shop") or {}).get("name", "Across tracked stores")},
                }
            }
        prices = {"deals": deals, "currency_note": "Prices are requested for India; each amount displays the currency returned by the provider."}
        return prices, history, {"id": game_id, "title": chosen.get("title"), "assets": info.get("assets", {}), "itad_url": (info.get("urls") or {}).get("game")}
    except requests.HTTPError as exc:
        status = exc.response.status_code if exc.response is not None else "unknown"
        print(f"ITAD API HTTP error ({status}): {exc}")
        return None, None, None
    except (requests.RequestException, ValueError, TypeError, KeyError) as exc:
        print(f"ITAD pricing error: {exc}")
        return None, None, None
