import html
import os
from datetime import datetime
from urllib.parse import urlparse

import requests
import streamlit as st

st.set_page_config(page_title="Nexus Game Hub", page_icon="🎮", layout="wide", initial_sidebar_state="collapsed")

# ---- Design system ----
ACCENTS = {
    "Violet": ("#A78BFA", "#7C3AED"),
    "Electric blue": ("#60A5FA", "#2563EB"),
    "Neon green": ("#A3E635", "#65A30D"),
}
with st.sidebar:
    st.markdown("## ⚙️ Preferences")
    accent_name = st.selectbox("Accent colour", list(ACCENTS.keys()), index=0)
    backend_url = st.text_input(
        "Backend URL",
        value=os.getenv("BACKEND_API_URL", "http://127.0.0.1:8000"),
        help="For deployment, set BACKEND_API_URL in the frontend environment.",
    ).strip().rstrip("/")
    st.caption("Nexus Game Hub · India region")

accent, accent_deep = ACCENTS[accent_name]
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Space+Grotesk:wght@400;500;600;700&display=swap');
:root {{ --nx-accent:{accent}; --nx-deep:{accent_deep}; --nx-bg:#090B12; --nx-panel:#111521; --nx-line:#242A3B; --nx-muted:#9AA4B8; }}
html, body, [class*="css"] {{ font-family:'DM Sans',sans-serif; }}
.stApp {{ background:radial-gradient(ellipse at 15% -10%, color-mix(in srgb, var(--nx-accent) 15%, transparent), transparent 35%), #090B12; color:#F4F6FC; }}
.block-container {{ max-width:1250px; padding-top:1.35rem; padding-bottom:3rem; }}
[data-testid="stHeader"] {{ background:transparent; }}
[data-testid="stSidebar"] {{ background:#0D1019; border-right:1px solid var(--nx-line); }}
h1,h2,h3 {{ font-family:'Space Grotesk',sans-serif !important; letter-spacing:-.035em; }}
.nx-topline {{ display:flex; align-items:center; gap:9px; color:#B6BED0; font-size:.78rem; font-weight:700; letter-spacing:.17em; text-transform:uppercase; margin-bottom:1.2rem; }}
.nx-dot {{ width:8px;height:8px;border-radius:50%;background:var(--nx-accent);box-shadow:0 0 14px var(--nx-accent);display:inline-block; }}
.nx-hero {{ padding:2.25rem 2.1rem 1.9rem; border:1px solid #2A3043; border-radius:24px; background:linear-gradient(125deg,rgba(20,25,40,.98),rgba(14,16,27,.92)); position:relative; overflow:hidden; margin-bottom:1.5rem; }}
.nx-hero:after {{ content:'N'; position:absolute; right:3%; top:-55px; font-family:'Space Grotesk'; font-size:19rem; line-height:1; font-weight:700; color:rgba(255,255,255,.025); pointer-events:none; }}
.nx-kicker {{ color:var(--nx-accent); font-size:.76rem; letter-spacing:.14em; text-transform:uppercase; font-weight:700; margin-bottom:.75rem; }}
.nx-title {{ font-family:'Space Grotesk',sans-serif; font-size:clamp(2.2rem,5vw,4.1rem); font-weight:700; line-height:1.03; letter-spacing:-.06em; margin:0 0 .9rem; color:#F7F8FC; }}
.nx-title span {{ color:var(--nx-accent); }}
.nx-subtitle {{ max-width:650px; color:#AAB3C6; font-size:1rem; line-height:1.65; }}
.nx-badges {{ display:flex;flex-wrap:wrap;gap:8px;margin-top:1.25rem; }}
.nx-badge {{ border:1px solid #343B50; background:#171C2B; border-radius:999px; padding:6px 11px; color:#D4D9E5; font-size:.75rem; }}
.stTextInput input {{ background:#111521 !important; border:1px solid #30374A !important; border-radius:12px !important; color:#F5F7FC !important; min-height:3.1rem; }}
.stTextInput input:focus {{ border-color:var(--nx-accent) !important; box-shadow:0 0 0 1px var(--nx-accent) !important; }}
.stButton>button, .stFormSubmitButton>button {{ border-radius:12px; border:1px solid var(--nx-accent); background:var(--nx-accent); color:#0A0B10; font-weight:800; min-height:3rem; transition:transform .15s ease, filter .15s ease; }}
.stButton>button:hover, .stFormSubmitButton>button:hover {{ filter:brightness(1.08); transform:translateY(-1px); color:#090B12; border-color:var(--nx-accent); }}
.nx-section {{ font-family:'Space Grotesk',sans-serif; font-size:1.4rem; font-weight:700; margin:1.65rem 0 .85rem; color:#F4F6FC; }}
.nx-muted {{ color:var(--nx-muted); font-size:.9rem; }}
.nx-panel {{ background:linear-gradient(145deg,#141927,#10131D); border:1px solid var(--nx-line); border-radius:18px; padding:1.15rem; height:100%; }}
.nx-price {{ font-family:'Space Grotesk',sans-serif; font-size:1.9rem; font-weight:700; letter-spacing:-.04em; color:#F8FAFF; }}
.nx-label {{ color:#98A2B7; text-transform:uppercase; font-size:.7rem; letter-spacing:.12em; font-weight:700; }}
.nx-store {{ background:#121725; border:1px solid #293044; border-radius:14px; padding:15px 16px; margin:9px 0; display:flex; align-items:center; gap:14px; }}
.nx-store-name {{ font-weight:700; color:#F0F3FA; }}
.nx-store-sub {{ color:#939DB2; font-size:.78rem; margin-top:3px; }}
.nx-store-price {{ margin-left:auto; text-align:right; white-space:nowrap; font-family:'Space Grotesk',sans-serif; font-size:1.15rem; font-weight:700; }}
.nx-buy-btn {{ display:inline-flex; align-items:center; justify-content:center; gap:6px; margin-top:9px; padding:8px 12px; border-radius:9px; background:var(--nx-accent); color:#090B12 !important; font-family:'DM Sans',sans-serif; font-size:.78rem; font-weight:800; text-decoration:none !important; border:1px solid var(--nx-accent); transition:transform .15s ease,filter .15s ease; }}
.nx-buy-btn:hover {{ filter:brightness(1.1); transform:translateY(-1px); }}
.nx-no-link {{ display:inline-block; margin-top:9px; color:#7F899D; font-family:'DM Sans',sans-serif; font-size:.72rem; }}
.nx-discount {{ display:inline-block; background:rgba(163,230,53,.12); color:#B7F36A; border:1px solid rgba(163,230,53,.25); padding:3px 7px; border-radius:7px; font-size:.72rem; margin-top:5px; }}
.nx-game-title {{ font-family:'Space Grotesk',sans-serif; font-size:2rem; font-weight:700; line-height:1.1; letter-spacing:-.04em; }}
.nx-cover {{ width:100%; border-radius:14px; border:1px solid #2B3144; object-fit:cover; max-height:320px; }}
.nx-chip {{ display:inline-block; border:1px solid #343B50; color:#C4CCDC; background:#171C2B; border-radius:8px; padding:5px 9px; margin:3px 5px 3px 0; font-size:.78rem; }}
hr {{ border-color:#252B3A !important; }}
footer {{ visibility:hidden; }}
@media(max-width:700px) {{ .nx-hero {{padding:1.4rem 1.2rem}} .nx-store {{align-items:flex-start}} .nx-store-price {{font-size:1rem}} }}
</style>
""", unsafe_allow_html=True)

st.markdown(f"""
<div class="nx-topline"><span class="nx-dot"></span> NEXUS / GAME INTELLIGENCE</div>
<section class="nx-hero">
  <div class="nx-kicker">Your next game. Your best price.</div>
  <div class="nx-title">Play more.<br><span>Pay less.</span></div>
  <div class="nx-subtitle">Compare PC game deals, check historical lows, and discover the best available offer. Built for players in India.</div>
  <div class="nx-badges"><span class="nx-badge">◈ India region</span><span class="nx-badge">↗ Multi-store comparison</span><span class="nx-badge">⌁ Historical lows</span></div>
</section>
""", unsafe_allow_html=True)

with st.form("game_search", clear_on_submit=False):
    c1, c2 = st.columns([5, 1.25], vertical_alignment="bottom", gap="small")
    with c1:
        game_query = st.text_input("SEARCH THE LIBRARY", placeholder="Try Elden Ring, Cyberpunk 2077, Hades II…", label_visibility="collapsed")
    with c2:
        submitted = st.form_submit_button("⌕  Find a game", use_container_width=True)

if submitted:
    if not game_query.strip():
        st.warning("Enter a game title to start searching.")
    else:
        try:
            with st.spinner("Searching game databases and Indian-region prices…"):
                response = requests.get(f"{backend_url}/api/game/{requests.utils.quote(game_query.strip(), safe='')}", timeout=25)
                if response.ok:
                    st.session_state["nexus_result"] = response.json()
                    st.session_state["nexus_query"] = game_query.strip()
                    st.session_state.pop("nexus_error", None)
                else:
                    try: detail = response.json().get("detail", "")
                    except ValueError: detail = ""
                    st.session_state.pop("nexus_result", None)
                    st.session_state["nexus_error"] = f"{detail or 'Search failed.'} (HTTP {response.status_code})"
        except requests.RequestException as exc:
            st.session_state["nexus_error"] = f"Could not reach the backend at {backend_url}. Check that FastAPI is running and the URL is correct."
            st.session_state.pop("nexus_result", None)

if st.session_state.get("nexus_error"):
    st.error(st.session_state["nexus_error"])


def money(value, currency=""):
    if value is None or value == "": return "Unavailable"
    try: amount = float(value)
    except (TypeError, ValueError): return "Unavailable"
    currency = (currency or "").upper()
    if currency == "INR": return f"₹{amount:,.2f}".rstrip("0").rstrip(".")
    if currency == "USD": return f"${amount:,.2f}"
    if currency == "EUR": return f"€{amount:,.2f}"
    if currency == "GBP": return f"£{amount:,.2f}"
    return f"{amount:,.2f} {currency}".strip()


def safe(value): return html.escape(str(value or ""))

result = st.session_state.get("nexus_result")
if result:
    igdb = result.get("igdb") or {}
    prices = result.get("prices") or {}
    history = result.get("history") or {}
    itad_game = result.get("itad_game") or {}
    deals = prices.get("deals") or []
    title = igdb.get("name") or itad_game.get("title") or st.session_state.get("nexus_query", "Game details")
    summary = (igdb.get("summary") or "Game description is not available from the metadata provider.").strip()
    platforms = [p.get("name") for p in (igdb.get("platforms") or []) if p.get("name")]
    genres = [g.get("name") for g in (igdb.get("genres") or []) if g.get("name")]
    release = igdb.get("first_release_date")
    release_year = datetime.fromtimestamp(release).year if isinstance(release, (int, float)) else None
    cover = igdb.get("cover_url") or (itad_game.get("assets") or {}).get("banner400") or (itad_game.get("assets") or {}).get("boxart")

    st.markdown('<div class="nx-section">Game overview</div>', unsafe_allow_html=True)
    left, right = st.columns([1, 2.4], gap="large")
    with left:
        if cover:
            st.markdown(f'<img class="nx-cover" src="{safe(cover)}" alt="{safe(title)} cover">', unsafe_allow_html=True)
        else:
            st.markdown('<div class="nx-panel" style="text-align:center;padding:3rem 1rem;font-size:4rem">🎮</div>', unsafe_allow_html=True)
    with right:
        st.markdown(f'<div class="nx-game-title">{safe(title)}</div>', unsafe_allow_html=True)
        metadata = []
        if release_year: metadata.append(f"Released {release_year}")
        if genres: metadata.extend(genres[:3])
        if metadata:
            st.markdown(''.join(f'<span class="nx-chip">{safe(x)}</span>' for x in metadata), unsafe_allow_html=True)
        st.markdown(f'<p style="color:#AAB3C6;line-height:1.75;margin-top:1rem">{safe(summary[:850])}{"…" if len(summary)>850 else ""}</p>', unsafe_allow_html=True)
        if platforms:
            st.markdown('<div class="nx-label" style="margin-top:.8rem">Supported platforms</div>', unsafe_allow_html=True)
            st.markdown(''.join(f'<span class="nx-chip">{safe(p)}</span>' for p in platforms), unsafe_allow_html=True)
        if itad_game.get("itad_url"):
            st.markdown(f'<p style="margin-top:1rem"><a href="{safe(itad_game["itad_url"])}" target="_blank" style="color:{accent};text-decoration:none;font-weight:700">View on IsThereAnyDeal ↗</a></p>', unsafe_allow_html=True)

    st.markdown('<div class="nx-section">Price intelligence <span style="font-size:.8rem;color:#929CB1;font-family:DM Sans;font-weight:400">/ India region</span></div>', unsafe_allow_html=True)
    low = (history.get("low") or {})
    low_amount = low.get("amount")
    low_currency = low.get("currency", "")
    cheapest = deals[0] if deals else None
    metric1, metric2, metric3 = st.columns(3, gap="medium")
    with metric1:
        st.markdown(f'<div class="nx-panel"><div class="nx-label">Best current price</div><div class="nx-price" style="color:{accent}">{money((cheapest or {}).get("price",{}).get("amount"),(cheapest or {}).get("price",{}).get("currency")) if cheapest else "—"}</div><div class="nx-muted">{safe((cheapest or {}).get("shop",{}).get("name","No deal found"))}</div></div>', unsafe_allow_html=True)
    with metric2:
        st.markdown(f'<div class="nx-panel"><div class="nx-label">All-time low</div><div class="nx-price">{money(low_amount,low_currency)}</div><div class="nx-muted">{safe(low.get("shop",{}).get("name","Across tracked stores")) if low_amount is not None else "No history available"}</div></div>', unsafe_allow_html=True)
    with metric3:
        st.markdown(f'<div class="nx-panel"><div class="nx-label">Stores compared</div><div class="nx-price">{len(deals)}</div><div class="nx-muted">Live offers returned by provider</div></div>', unsafe_allow_html=True)

    if deals:
        st.markdown('<div class="nx-section">Available offers</div>', unsafe_allow_html=True)
        for idx, deal in enumerate(deals):
            shop = (deal.get("shop") or {}).get("name", "Store")
            price = deal.get("price") or {}
            regular = deal.get("regular") or {}
            currency = price.get("currency", "")
            discount = int(deal.get("cut") or 0)
            url = deal.get("url")
            parsed_url = urlparse(str(url)) if url else None
            buy_url = url if parsed_url and parsed_url.scheme in ("https", "http") and parsed_url.netloc else None
            # Prices are not converted or relabelled; show the exact currency supplied by ITAD.
            deal_html = f'<div class="nx-store"><div style="font-size:1.45rem;width:34px;text-align:center">{"🏆" if idx==0 else "🛒"}</div><div><div class="nx-store-name">{safe(shop)}</div><div class="nx-store-sub">'
            if regular.get("amount") not in (None, "") and float(regular.get("amount") or 0) > float(price.get("amount") or 0):
                deal_html += f'Regular {money(regular.get("amount"),regular.get("currency",currency))} · Save {discount}%'
            else:
                deal_html += ('Current listed price' if discount == 0 else f'{discount}% off')
            deal_html += '</div>'
            if discount > 0: deal_html += f'<span class="nx-discount">-{discount}%</span>'
            deal_html += f'</div><div class="nx-store-price">{money(price.get("amount"),currency)}'
            if buy_url:
                deal_html += f'<div><a class="nx-buy-btn" href="{safe(buy_url)}" target="_blank" rel="noopener noreferrer">Buy at {safe(shop)} ↗</a></div>'
            else:
                deal_html += '<div class="nx-no-link">Purchase link unavailable</div>'
            deal_html += '</div></div>'
            st.markdown(deal_html, unsafe_allow_html=True)
        st.caption("Prices and currency codes are shown as returned by the provider for the India region. Store availability and regional pricing can vary.")
    else:
        st.info("No price offers were returned for India for this title. Try another title or check the provider's regional coverage.")

    if not igdb:
        st.info("Detailed game metadata was unavailable. Price information may still be available from the pricing provider.")
    st.markdown("<hr>", unsafe_allow_html=True)
    st.caption("Pricing by IsThereAnyDeal API · Game metadata by IGDB. Nexus Game Hub is an independent project and is not affiliated with these services.")
else:
    st.markdown('<div class="nx-panel" style="margin-top:1rem;padding:1.35rem"><div class="nx-label">HOW IT WORKS</div><div style="font-family:Space Grotesk;font-size:1.15rem;font-weight:700;margin:.65rem 0">Search once. Compare smarter.</div><div class="nx-muted" style="line-height:1.7">Enter a PC game title above to load metadata, compare supported storefront offers for India, and see the historical low when available. We never turn a dollar amount into a rupee amount without a real regional price.</div></div>', unsafe_allow_html=True)
    a,b,c = st.columns(3, gap="medium")
    with a:
        st.markdown('<div class="nx-panel" style="margin-top:1rem"><div style="font-size:1.5rem">⌕</div><b>Find the game</b><p class="nx-muted">Search by the official game title.</p></div>', unsafe_allow_html=True)
    with b:
        st.markdown('<div class="nx-panel" style="margin-top:1rem"><div style="font-size:1.5rem">₹</div><b>Compare offers</b><p class="nx-muted">See prices in the currency actually returned for India.</p></div>', unsafe_allow_html=True)
    with c:
        st.markdown('<div class="nx-panel" style="margin-top:1rem"><div style="font-size:1.5rem">⌁</div><b>Check the low</b><p class="nx-muted">Compare today’s offer with historical lows.</p></div>', unsafe_allow_html=True)
