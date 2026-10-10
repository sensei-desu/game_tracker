import html
import os
from datetime import datetime
from urllib.parse import urlparse

import requests
import streamlit as st

st.set_page_config(page_title="Nexus Game Hub", page_icon="🎮", layout="wide", initial_sidebar_state="collapsed")

# ---- Theme Studio: 15 complete visual themes ----
THEMES = {
    "Pure Light": {
        "bg": "#F5F7FC", "panel": "#FFFFFF", "panel2": "#EDF1F8", "text": "#182033", "muted": "#5D687D", "line": "#D9DFEA",
        "accent": "#2563EB", "deep": "#1D4ED8", "button_text": "#FFFFFF", "badge": "#E9EFFB", "chip": "#EDF2FC", "radius": "18px",
        "app_bg": "radial-gradient(ellipse at 8% 0%, rgba(37,99,235,.10), transparent 32%), #F5F7FC",
        "hero_bg": "linear-gradient(120deg, rgba(255,255,255,.98), rgba(237,242,252,.98))", "deco": "✦", "deco_color": "rgba(37,99,235,.07)", "font": "DM Sans", "mode": "light",
        "tagline": "A brighter way to find your next game."
    },
    "Midnight Pro": {
        "bg": "#090B12", "panel": "#141927", "panel2": "#10131D", "text": "#F4F6FC", "muted": "#A3ADC0", "line": "#2A3042",
        "accent": "#A78BFA", "deep": "#7C3AED", "button_text": "#100B1B", "badge": "#1B2030", "chip": "#191F2E", "radius": "20px",
        "app_bg": "radial-gradient(ellipse at 8% 0%, rgba(124,58,237,.19), transparent 29%), radial-gradient(ellipse at 95% 15%, rgba(14,165,233,.09), transparent 24%), #090B12",
        "hero_bg": "linear-gradient(115deg, rgba(22,25,43,.99), rgba(12,15,26,.98) 68%, rgba(21,18,39,.98))", "deco": "N", "deco_color": "rgba(167,139,250,.04)", "font": "DM Sans", "mode": "dark",
        "tagline": "Your next game. Your best price."
    },
    "Elden Ring — The Lands Between": {
        "bg": "#100F0C", "panel": "#1B1913", "panel2": "#15140F", "text": "#EDE4CF", "muted": "#B7AC91", "line": "#4A4028",
        "accent": "#C6A65C", "deep": "#8B6D32", "button_text": "#171208", "badge": "#292419", "chip": "#242016", "radius": "10px",
        "app_bg": "radial-gradient(ellipse at 75% 0%, rgba(198,166,92,.17), transparent 32%), radial-gradient(ellipse at 10% 60%, rgba(96,73,30,.12), transparent 38%), #100F0C",
        "hero_bg": "linear-gradient(115deg, rgba(34,29,19,.98), rgba(16,15,12,.98)), repeating-linear-gradient(45deg, transparent 0 18px, rgba(198,166,92,.025) 18px 19px)", "deco": "✧", "deco_color": "rgba(198,166,92,.07)", "font": "Cinzel", "mode": "dark",
        "tagline": "A tarnished guide to better game prices."
    },
    "Spider-Verse": {
        "bg": "#101014", "panel": "#1B171C", "panel2": "#15151C", "text": "#F7F4FA", "muted": "#B8ACBD", "line": "#45303A",
        "accent": "#F02D3A", "deep": "#B91C2B", "button_text": "#FFFFFF", "badge": "#28191F", "chip": "#211A21", "radius": "8px",
        "app_bg": "radial-gradient(ellipse at 100% 0%, rgba(22,139,255,.16), transparent 27%), radial-gradient(ellipse at 0% 10%, rgba(230,36,41,.18), transparent 30%), #101014",
        "hero_bg": "linear-gradient(115deg, rgba(37,18,25,.98), rgba(16,16,20,.97) 65%, rgba(12,26,39,.96))", "deco": "SP//", "deco_color": "rgba(240,45,58,.06)", "font": "Space Grotesk", "mode": "dark",
        "tagline": "Into the deals-verse. Find your best price."
    },
    "Pixel Arcade": {
        "bg": "#11112B", "panel": "#1B1B3D", "panel2": "#151530", "text": "#F5F0FF", "muted": "#B9B4D8", "line": "#45416F",
        "accent": "#35F2A0", "deep": "#13B981", "button_text": "#101326", "badge": "#25234B", "chip": "#211F43", "radius": "2px",
        "app_bg": "linear-gradient(rgba(53,242,160,.025) 1px, transparent 1px), linear-gradient(90deg, rgba(53,242,160,.025) 1px, transparent 1px), radial-gradient(ellipse at 50% 0%, rgba(255,79,216,.12), transparent 36%), #11112B",
        "hero_bg": "linear-gradient(135deg, #22214A, #171733)", "deco": "▣", "deco_color": "rgba(53,242,160,.06)", "font": "DM Sans", "mode": "dark",
        "tagline": "PLAYER ONE: your next great deal awaits."
    },
    "Cyberpunk 2077": {
        "bg": "#090B10", "panel": "#171A21", "panel2": "#11141B", "text": "#F4F4F4", "muted": "#B3B8C4", "line": "#41434A",
        "accent": "#FCEE0A", "deep": "#D4C900", "button_text": "#171707", "badge": "#24251D", "chip": "#20211A", "radius": "7px",
        "app_bg": "radial-gradient(ellipse at 95% 0%, rgba(0,229,255,.10), transparent 28%), radial-gradient(ellipse at 5% 15%, rgba(252,238,10,.10), transparent 28%), #090B10",
        "hero_bg": "linear-gradient(115deg, rgba(34,35,26,.98), rgba(14,16,21,.98) 70%)", "deco": "2077", "deco_color": "rgba(252,238,10,.06)", "font": "Space Grotesk", "mode": "dark",
        "tagline": "Wake up, samurai. There's a deal to catch."
    },
    "Sakura Dreams": {
        "bg": "#FFF5F8", "panel": "#FFFFFF", "panel2": "#FDEAF1", "text": "#422838", "muted": "#866A7A", "line": "#F1C9D9",
        "accent": "#D94F86", "deep": "#B83268", "button_text": "#FFFFFF", "badge": "#FCE5EE", "chip": "#FFF0F5", "radius": "22px",
        "app_bg": "radial-gradient(ellipse at 8% 0%, rgba(255,183,205,.42), transparent 32%), radial-gradient(ellipse at 92% 10%, rgba(255,220,230,.65), transparent 26%), #FFF5F8",
        "hero_bg": "linear-gradient(120deg, rgba(255,255,255,.97), rgba(255,231,240,.96))", "deco": "✿", "deco_color": "rgba(217,79,134,.10)", "font": "DM Sans", "mode": "light",
        "tagline": "Soft petals. Smart prices. Your next adventure."
    },
    "Kawaii Anime": {
        "bg": "#FBF5FF", "panel": "#FFFFFF", "panel2": "#F5EAFE", "text": "#332344", "muted": "#806A93", "line": "#E4D0F5",
        "accent": "#B36BE8", "deep": "#9650CC", "button_text": "#FFFFFF", "badge": "#F2E5FC", "chip": "#F9F0FF", "radius": "24px",
        "app_bg": "radial-gradient(ellipse at 0% 0%, rgba(255,191,220,.42), transparent 30%), radial-gradient(ellipse at 100% 5%, rgba(190,179,255,.42), transparent 32%), radial-gradient(ellipse at 50% 100%, rgba(178,245,224,.20), transparent 35%), #FBF5FF",
        "hero_bg": "linear-gradient(125deg, rgba(255,255,255,.98), rgba(246,232,255,.98))", "deco": "♡ ✦", "deco_color": "rgba(179,107,232,.09)", "font": "DM Sans", "mode": "light",
        "tagline": "Cute games, cuter vibes, smarter prices."
    },
    "Psyduck.exe": {
        "bg": "#F2FAFF", "panel": "#FFFFFF", "panel2": "#E5F5FF", "text": "#20364A", "muted": "#5C7C92", "line": "#B9DFF3",
        "accent": "#E9AE25", "deep": "#C98A10", "button_text": "#302207", "badge": "#FFF4CF", "chip": "#EAF7FF", "radius": "20px",
        "app_bg": "radial-gradient(ellipse at 10% 0%, rgba(255,222,117,.35), transparent 28%), radial-gradient(ellipse at 90% 5%, rgba(122,213,255,.30), transparent 30%), #F2FAFF",
        "hero_bg": "linear-gradient(120deg, rgba(255,255,255,.98), rgba(224,245,255,.98))", "deco": "???", "deco_color": "rgba(233,174,37,.10)", "font": "DM Sans", "mode": "light",
        "tagline": "Wait... is this the cheapest deal? Psy-y-y?"
    },
    "Samurai Ink": {
        "bg": "#111110", "panel": "#1C1B19", "panel2": "#151514", "text": "#F0E8D8", "muted": "#B8AD9D", "line": "#413B35",
        "accent": "#B62E32", "deep": "#8C2027", "button_text": "#FFFFFF", "badge": "#28201F", "chip": "#241D1B", "radius": "9px",
        "app_bg": "radial-gradient(ellipse at 95% 0%, rgba(182,46,50,.15), transparent 28%), #111110",
        "hero_bg": "linear-gradient(115deg, rgba(34,29,27,.98), rgba(17,17,16,.98))", "deco": "筆", "deco_color": "rgba(182,46,50,.07)", "font": "Noto Sans JP", "mode": "dark",
        "tagline": "Precision in every search. Discipline in every deal."
    },
    "Nordic Frost": {
        "bg": "#0B121B", "panel": "#16212D", "panel2": "#101A25", "text": "#E5F1F7", "muted": "#A7BFCD", "line": "#304653",
        "accent": "#9BDDF4", "deep": "#5EB7D7", "button_text": "#10202A", "badge": "#1D303C", "chip": "#192B37", "radius": "13px",
        "app_bg": "radial-gradient(ellipse at 50% 0%, rgba(155,221,244,.15), transparent 35%), #0B121B",
        "hero_bg": "linear-gradient(120deg, rgba(25,42,55,.98), rgba(11,18,27,.98))", "deco": "❄", "deco_color": "rgba(155,221,244,.07)", "font": "Space Grotesk", "mode": "dark",
        "tagline": "Chill out. Find your next adventure for less."
    },
    "Pastel Dream": {
        "bg": "#F7F3FF", "panel": "#FFFFFF", "panel2": "#F0EAFE", "text": "#302A40", "muted": "#786D8E", "line": "#DDD2F3",
        "accent": "#8D73D6", "deep": "#7157BB", "button_text": "#FFFFFF", "badge": "#EDE5FC", "chip": "#F4EEFF", "radius": "22px",
        "app_bg": "radial-gradient(ellipse at 0% 0%, rgba(220,206,255,.48), transparent 32%), radial-gradient(ellipse at 100% 10%, rgba(168,230,207,.28), transparent 30%), #F7F3FF",
        "hero_bg": "linear-gradient(120deg, rgba(255,255,255,.98), rgba(238,232,255,.98))", "deco": "☁", "deco_color": "rgba(141,115,214,.08)", "font": "DM Sans", "mode": "light",
        "tagline": "A cozy corner of the internet for game deals."
    },
    "Minecraft World": {
        "bg": "#121B13", "panel": "#1B2B1C", "panel2": "#152218", "text": "#E7F1DF", "muted": "#B1C6A8", "line": "#405A3C",
        "accent": "#72D34B", "deep": "#429A35", "button_text": "#10200E", "badge": "#263D25", "chip": "#21351F", "radius": "3px",
        "app_bg": "linear-gradient(rgba(114,211,75,.035) 2px, transparent 2px), linear-gradient(90deg, rgba(114,211,75,.035) 2px, transparent 2px), radial-gradient(ellipse at 50% 0%, rgba(76,175,80,.14), transparent 36%), #121B13",
        "hero_bg": "linear-gradient(120deg, rgba(37,60,35,.98), rgba(19,34,21,.98))", "deco": "▧", "deco_color": "rgba(114,211,75,.07)", "font": "DM Sans", "mode": "dark",
        "tagline": "Craft your library. Mine the best prices."
    },
    "Jujutsu Kaisen — Cursed Energy": {
        "bg": "#0D0B14", "panel": "#1A1525", "panel2": "#130F1D", "text": "#F1EBFF", "muted": "#B7A9D0", "line": "#45305D",
        "accent": "#A78BFA", "deep": "#6D28D9", "button_text": "#FFFFFF", "badge": "#251B35", "chip": "#20182D", "radius": "12px",
        "app_bg": "radial-gradient(ellipse at 8% 0%, rgba(124,58,237,.24), transparent 30%), radial-gradient(ellipse at 94% 8%, rgba(37,99,235,.17), transparent 29%), #0D0B14",
        "hero_bg": "linear-gradient(120deg, rgba(35,22,54,.98), rgba(14,12,23,.98) 70%)", "deco": "呪", "deco_color": "rgba(167,139,250,.08)", "font": "Noto Sans JP", "mode": "dark",
        "tagline": "Compare prices with cursed-energy precision."
    },
    "Gamer's Library": {
        "bg": "#171A1E", "panel": "#22272D", "panel2": "#1C2126", "text": "#E8EBEF", "muted": "#A9B1BB", "line": "#3A424B",
        "accent": "#A4D037", "deep": "#7CA321", "button_text": "#1A210B", "badge": "#2C3523", "chip": "#272F22", "radius": "14px",
        "app_bg": "radial-gradient(ellipse at 85% 0%, rgba(164,208,55,.12), transparent 30%), #171A1E",
        "hero_bg": "linear-gradient(120deg, rgba(39,46,47,.98), rgba(24,28,31,.98))", "deco": "▤", "deco_color": "rgba(164,208,55,.06)", "font": "DM Sans", "mode": "dark",
        "tagline": "Your library, your prices, your next play."
    },
}

THEME_NAMES = list(THEMES.keys())

# Theme preferences are encoded in the URL so the selection survives refreshes and can be bookmarked.
def _sync_theme_query():
    st.query_params["theme"] = st.session_state.theme_choice

def _sync_jjk_query():
    st.query_params["jjk"] = st.session_state.jjk_choice

query_theme = st.query_params.get("theme", "Midnight Pro")
if query_theme not in THEMES:
    query_theme = "Midnight Pro"
query_jjk = st.query_params.get("jjk", "Gojo — Infinity")
if query_jjk not in ("Gojo — Infinity", "Sukuna — Malevolent Shrine"):
    query_jjk = "Gojo — Infinity"

# Initialize widget state from query params only on first render of the session.
if "theme_choice" not in st.session_state:
    st.session_state.theme_choice = query_theme
if "jjk_choice" not in st.session_state:
    st.session_state.jjk_choice = query_jjk

with st.sidebar:
    st.markdown("## ⚙️ Preferences")
    backend_url = st.text_input(
        "Backend URL",
        value=os.getenv("BACKEND_API_URL", "http://127.0.0.1:8000"),
        help="For deployment, set BACKEND_API_URL in the frontend environment.",
    ).strip().rstrip("/")
    st.caption("Nexus Game Hub · India region")
    st.caption("Theme selection is saved in the page URL so you can bookmark your preferred look.")

# Theme Studio is visible on the page instead of being hidden in the sidebar.
control_cols = st.columns([1.35, 1, 2.1], vertical_alignment="bottom", gap="medium")
with control_cols[0]:
    st.markdown("<div style='font-size:.72rem;letter-spacing:.15em;font-weight:800;opacity:.75;margin-bottom:.35rem'>THEME STUDIO</div>", unsafe_allow_html=True)
    st.selectbox("Choose your world", THEME_NAMES, key="theme_choice", on_change=_sync_theme_query, label_visibility="collapsed")
with control_cols[1]:
    if st.session_state.theme_choice == "Jujutsu Kaisen — Cursed Energy":
        st.selectbox("Cursed technique", ["Gojo — Infinity", "Sukuna — Malevolent Shrine"], key="jjk_choice", on_change=_sync_jjk_query, label_visibility="collapsed")
    else:
        st.markdown("<div style='padding:.65rem 0;color:var(--nx-muted);font-size:.85rem'>✦ 15 visual worlds</div>", unsafe_allow_html=True)
with control_cols[2]:
    st.markdown("<div style='padding:.65rem 0;color:var(--nx-muted);font-size:.85rem'>Switch themes anytime — your search and price data stay intact.</div>", unsafe_allow_html=True)

active_theme_name = st.session_state.theme_choice
active_theme = dict(THEMES[active_theme_name])
if active_theme_name == "Jujutsu Kaisen — Cursed Energy":
    if st.session_state.jjk_choice == "Sukuna — Malevolent Shrine":
        active_theme.update({
            "bg": "#10090D", "panel": "#211218", "panel2": "#170D12", "text": "#FFF0F1", "muted": "#D1AAB0", "line": "#5C2735",
            "accent": "#F04452", "deep": "#B91C35", "button_text": "#FFFFFF", "badge": "#321722", "chip": "#29141C",
            "app_bg": "radial-gradient(ellipse at 10% 0%, rgba(240,68,82,.24), transparent 30%), radial-gradient(ellipse at 95% 10%, rgba(127,29,29,.22), transparent 30%), #10090D",
            "hero_bg": "linear-gradient(120deg, rgba(55,19,29,.98), rgba(17,9,14,.98) 70%)", "deco": "両面", "deco_color": "rgba(240,68,82,.09)",
            "tagline": "Enter the shrine. Find the deal."
        })
    else:
        active_theme.update({
            "bg": "#080D18", "panel": "#111A2C", "panel2": "#0D1422", "text": "#EDF6FF", "muted": "#A9C3E0", "line": "#263F68",
            "accent": "#54B8FF", "deep": "#6D4AFF", "button_text": "#081321", "badge": "#172943", "chip": "#142239",
            "app_bg": "radial-gradient(ellipse at 10% 0%, rgba(84,184,255,.23), transparent 30%), radial-gradient(ellipse at 95% 8%, rgba(109,74,255,.22), transparent 30%), #080D18",
            "hero_bg": "linear-gradient(120deg, rgba(17,37,68,.98), rgba(8,13,24,.98) 70%)", "deco": "無量空処", "deco_color": "rgba(84,184,255,.09)",
            "tagline": "Limitless style. Unlimited game deals."
        })

with st.sidebar:
    st.markdown(f"### {active_theme_name}")
    if active_theme_name == "Jujutsu Kaisen — Cursed Energy":
        st.caption("Gojo's Infinity" if st.session_state.jjk_choice.startswith("Gojo") else "Sukuna's Malevolent Shrine")
    st.markdown("**Theme preview**")
    swatches = "".join(
        f"<span style='width:23px;height:23px;border-radius:7px;background:{color};border:1px solid {active_theme['line']};display:inline-block'></span>"
        for color in [active_theme["bg"], active_theme["panel"], active_theme["accent"], active_theme["text"]]
    )
    st.markdown(f"<div style='display:flex;gap:7px;margin:.3rem 0 1rem'>{swatches}</div>", unsafe_allow_html=True)

accent = active_theme["accent"]
accent_deep = active_theme["deep"]
font = active_theme["font"]
font_imports = "DM+Sans:wght@400;500;600;700;800&family=Space+Grotesk:wght@400;500;600;700&family=Cinzel:wght@400;500;600;700&family=Press+Start+2P&family=Noto+Sans+JP:wght@400;500;700"
if active_theme_name == "Jujutsu Kaisen — Cursed Energy":
    hero_kicker = "CURSED ENERGY / PRICE INTELLIGENCE"
elif active_theme_name == "Psyduck.exe":
    hero_kicker = "CONFUSED? LET'S FIND THAT DEAL."
elif active_theme_name == "Sakura Dreams":
    hero_kicker = "SAKURA SEASON / SMART GAME SHOPPING"
else:
    hero_kicker = "YOUR NEXT GAME / YOUR BEST PRICE"

pattern_css = ""
if active_theme_name == "Sakura Dreams":
    pattern_css = '.nx-hero:before{content:"✿　·　✧　✿";position:absolute;right:5%;bottom:8%;font-size:1.2rem;letter-spacing:.5rem;color:rgba(217,79,134,.28);pointer-events:none;}'
elif active_theme_name == "Psyduck.exe":
    pattern_css = '.nx-hero:before{content:"?　?　?";position:absolute;right:5%;bottom:9%;font-size:1.1rem;font-weight:900;letter-spacing:.4rem;color:rgba(201,138,16,.35);transform:rotate(-8deg);pointer-events:none;}'
elif active_theme_name == "Minecraft World":
    pattern_css = '.nx-panel,.nx-store{box-shadow:inset 0 0 0 2px rgba(114,211,75,.035),4px 4px 0 rgba(0,0,0,.13);}.nx-kicker,.nx-label{font-family:"Press Start 2P",monospace;font-size:.52rem;line-height:1.8;}'
elif active_theme_name == "Pixel Arcade":
    pattern_css = '.nx-panel,.nx-store,.nx-hero{box-shadow:4px 4px 0 rgba(0,0,0,.24);}.nx-kicker,.nx-label{font-family:"Press Start 2P",monospace;font-size:.52rem;line-height:1.8;}'
elif active_theme_name == "Jujutsu Kaisen — Cursed Energy":
    pattern_css = '.nx-hero:before{content:"◈　✧　◈";position:absolute;right:5%;bottom:8%;font-size:1.1rem;letter-spacing:.7rem;color:var(--nx-accent);opacity:.28;pointer-events:none;}'

# Distinct backgrounds and component styling are driven by the selected theme tokens.
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family={font_imports.replace(' ', '+')}&display=swap');
:root {{
 --nx-bg:{active_theme['bg']}; --nx-panel:{active_theme['panel']}; --nx-panel2:{active_theme['panel2']};
 --nx-text:{active_theme['text']}; --nx-muted:{active_theme['muted']}; --nx-line:{active_theme['line']};
 --nx-accent:{accent}; --nx-deep:{accent_deep}; --nx-button-text:{active_theme['button_text']};
 --nx-badge:{active_theme['badge']}; --nx-chip:{active_theme['chip']}; --nx-radius:{active_theme['radius']};
 --nx-font:'{font}', 'DM Sans', sans-serif;
}}
html, body, [class*="css"] {{ font-family:var(--nx-font); }}
.stApp {{ background:{active_theme['app_bg']}; color:var(--nx-text); transition:background .25s ease,color .25s ease; }}
.block-container {{ max-width:1320px; padding-top:1.15rem; padding-bottom:3rem; }}
[data-testid="stHeader"] {{ background:transparent; }}
[data-testid="stSidebar"] {{ background:var(--nx-bg); border-right:1px solid var(--nx-line); }}
[data-testid="stSidebar"] * {{ color:var(--nx-text); }}
h1,h2,h3 {{ font-family:var(--nx-font) !important; letter-spacing:-.035em; color:var(--nx-text); }}
.nx-topline {{ display:flex;align-items:center;gap:9px;color:var(--nx-muted);font-size:.72rem;font-weight:800;letter-spacing:.19em;text-transform:uppercase;margin:0 0 1rem; }}
.nx-dot {{ width:8px;height:8px;border-radius:50%;background:var(--nx-accent);box-shadow:0 0 14px var(--nx-accent);display:inline-block; }}
.nx-hero {{ display:grid;grid-template-columns:minmax(0,1.5fr) minmax(220px,.8fr);gap:1.5rem;align-items:center;padding:clamp(1.4rem,3.5vw,3rem);border:1px solid var(--nx-line);border-radius:calc(var(--nx-radius) + 8px);background:{active_theme['hero_bg']};position:relative;overflow:hidden;margin-bottom:1.5rem;box-shadow:0 24px 70px rgba(0,0,0,.13); }}
.nx-hero:after {{ content:"{active_theme['deco']}";position:absolute;right:2%;top:-4.6rem;font-family:var(--nx-font);font-size:clamp(7rem,18vw,15rem);line-height:1;font-weight:800;color:{active_theme['deco_color']};pointer-events:none;white-space:nowrap; }}
.nx-kicker {{ color:var(--nx-accent);font-size:.76rem;letter-spacing:.14em;text-transform:uppercase;font-weight:800;margin-bottom:.75rem;position:relative;z-index:1; }}
.nx-title {{ font-family:var(--nx-font);font-size:clamp(2.5rem,6vw,5rem);font-weight:800;line-height:.99;letter-spacing:-.06em;margin:0 0 1rem;color:var(--nx-text);position:relative;z-index:1; }}
.nx-title span {{ color:var(--nx-accent); }}
.nx-subtitle {{ max-width:610px;color:var(--nx-muted);font-size:1.02rem;line-height:1.7;position:relative;z-index:1; }}
.nx-badges {{ display:flex;flex-wrap:wrap;gap:8px;margin-top:1.25rem;position:relative;z-index:1; }}
.nx-badge {{ border:1px solid var(--nx-line);background:var(--nx-badge);border-radius:999px;padding:7px 12px;color:var(--nx-text);font-size:.75rem; }}
.nx-hero-side {{ border:1px solid var(--nx-line);background:color-mix(in srgb,var(--nx-panel) 78%,transparent);border-radius:var(--nx-radius);padding:1.25rem;min-height:205px;display:flex;flex-direction:column;justify-content:space-between;position:relative;z-index:1; }}
.nx-orbit {{ width:72px;height:72px;border-radius:var(--nx-radius);display:grid;place-items:center;background:linear-gradient(135deg,var(--nx-accent),var(--nx-deep));color:var(--nx-button-text);font-size:2rem;box-shadow:0 12px 35px color-mix(in srgb,var(--nx-accent) 24%,transparent); }}
.nx-side-caption {{ color:var(--nx-muted);text-transform:uppercase;font-size:.68rem;letter-spacing:.15em;font-weight:800; }}
.nx-side-title {{ font-family:var(--nx-font);font-size:1.4rem;font-weight:800;line-height:1.2;margin-top:.4rem;color:var(--nx-text); }}
.nx-muted {{ color:var(--nx-muted);font-size:.9rem; }}
.nx-section {{ font-family:var(--nx-font);font-size:1.4rem;font-weight:800;margin:1.65rem 0 .85rem;color:var(--nx-text); }}
.nx-panel {{ background:linear-gradient(145deg,var(--nx-panel),var(--nx-panel2));border:1px solid var(--nx-line);border-radius:var(--nx-radius);padding:1.15rem;height:100%;box-shadow:0 12px 35px rgba(0,0,0,.07); }}
.nx-price {{ font-family:var(--nx-font);font-size:clamp(1.45rem,2.5vw,2rem);font-weight:800;letter-spacing:-.04em;color:var(--nx-text); }}
.nx-label {{ color:var(--nx-muted);text-transform:uppercase;font-size:.7rem;letter-spacing:.12em;font-weight:800; }}
.nx-store {{ background:linear-gradient(105deg,var(--nx-panel),var(--nx-panel2));border:1px solid var(--nx-line);border-radius:var(--nx-radius);padding:17px 18px;margin:9px 0;display:flex;align-items:center;gap:14px;transition:transform .18s ease,border-color .18s ease; }}
.nx-store:hover {{ transform:translateY(-2px);border-color:var(--nx-accent); }}
.nx-store-name {{ font-weight:800;color:var(--nx-text); }}
.nx-store-sub {{ color:var(--nx-muted);font-size:.78rem;margin-top:3px; }}
.nx-store-price {{ margin-left:auto;text-align:right;white-space:nowrap;font-family:var(--nx-font);font-size:1.15rem;font-weight:800;color:var(--nx-text); }}
.nx-buy-btn {{ display:inline-flex;align-items:center;justify-content:center;gap:6px;margin-top:9px;padding:9px 13px;border-radius:calc(var(--nx-radius) * .6);background:var(--nx-accent);color:var(--nx-button-text) !important;font-family:var(--nx-font);font-size:.78rem;font-weight:800;text-decoration:none !important;border:1px solid var(--nx-accent);transition:transform .15s ease,filter .15s ease; }}
.nx-buy-btn:hover {{ filter:brightness(1.08);transform:translateY(-1px); }}
.nx-no-link {{ display:inline-block;margin-top:9px;color:var(--nx-muted);font-family:var(--nx-font);font-size:.72rem; }}
.nx-discount {{ display:inline-block;background:rgba(90,190,90,.14);color:{'#226B2D' if active_theme['mode']=='light' else '#A9ED9D'};border:1px solid rgba(90,190,90,.28);padding:3px 7px;border-radius:7px;font-size:.72rem;margin-top:5px; }}
.nx-game-title {{ font-family:var(--nx-font);font-size:2rem;font-weight:800;line-height:1.1;letter-spacing:-.04em;color:var(--nx-text); }}
.nx-cover {{ width:100%;border-radius:var(--nx-radius);border:1px solid var(--nx-line);object-fit:cover;max-height:320px; }}
.nx-chip {{ display:inline-block;border:1px solid var(--nx-line);color:var(--nx-text);background:var(--nx-chip);border-radius:calc(var(--nx-radius) * .55);padding:5px 9px;margin:3px 5px 3px 0;font-size:.78rem; }}
.stTextInput input {{ background:var(--nx-panel) !important;border:1px solid var(--nx-line) !important;border-radius:var(--nx-radius) !important;color:var(--nx-text) !important;min-height:3.35rem;font-size:1rem; }}
.stTextInput input:focus {{ border-color:var(--nx-accent) !important;box-shadow:0 0 0 1px var(--nx-accent) !important; }}
.stSelectbox div[data-baseweb="select"] > div {{ background:var(--nx-panel) !important;border-color:var(--nx-line) !important;border-radius:12px !important;color:var(--nx-text) !important; }}
.stSelectbox div[data-baseweb="select"] * {{ color:var(--nx-text) !important; }}
.stButton>button,.stFormSubmitButton>button {{ border-radius:var(--nx-radius);border:1px solid var(--nx-accent);background:var(--nx-accent);color:var(--nx-button-text);font-weight:800;min-height:3.35rem;box-shadow:0 7px 22px color-mix(in srgb,var(--nx-accent) 15%,transparent);transition:transform .15s ease,filter .15s ease; }}
.stButton>button:hover,.stFormSubmitButton>button:hover {{ filter:brightness(1.08);transform:translateY(-1px);color:var(--nx-button-text);border-color:var(--nx-accent); }}
[data-testid="stMetric"] {{ background:var(--nx-panel);border:1px solid var(--nx-line);border-radius:var(--nx-radius);padding:1rem; }}
[data-testid="stMetricLabel"],[data-testid="stMetricValue"],[data-testid="stMetricDelta"] {{ color:var(--nx-text); }}
[data-testid="stAlert"] {{ border-radius:var(--nx-radius); }}
.stMarkdown p,.stMarkdown li,[data-testid="stWidgetLabel"],.stCaption {{ color:var(--nx-text); }}
[data-testid="stCaptionContainer"] p {{ color:var(--nx-muted) !important; }}
hr {{ border-color:var(--nx-line) !important; }}
footer {{ visibility:hidden; }}
{pattern_css}
/* Theme-specific texture accents */

@media(max-width:800px){{.nx-hero{{display:block;padding:1.4rem 1.2rem}}.nx-hero-side{{display:none}}.nx-store{{align-items:flex-start;flex-wrap:wrap}}.nx-store-price{{font-size:1rem}}.nx-title{{font-size:clamp(2.4rem,11vw,4rem)}}}}
@media(prefers-reduced-motion:reduce){{*,*::before,*::after{{transition:none !important;animation:none !important}}}}
</style>
""", unsafe_allow_html=True)

st.markdown(f"""
<div class="nx-topline"><span class="nx-dot"></span> NEXUS / GAME INTELLIGENCE</div>
<section class="nx-hero">
  <div>
    <div class="nx-kicker">{safe(hero_kicker)}</div>
    <div class="nx-title">Play more.<br><span>Pay less.</span></div>
    <div class="nx-subtitle">A smarter way to shop for PC games. Compare storefront offers, check historical lows, and jump straight to the store — all in one place.</div>
    <div class="nx-badges"><span class="nx-badge">◈ India region</span><span class="nx-badge">↗ Multi-store comparison</span><span class="nx-badge">⌁ Historical lows</span></div>
  </div>
  <div class="nx-hero-side">
    <div class="nx-orbit">{"🦆" if active_theme_name == "Psyduck.exe" else "🌸" if active_theme_name == "Sakura Dreams" else "♡" if active_theme_name == "Kawaii Anime" else "⛏" if active_theme_name == "Minecraft World" else "呪" if active_theme_name == "Jujutsu Kaisen — Cursed Energy" else "✦"}</div>
    <div><div class="nx-side-caption">{safe(active_theme_name)}</div><div class="nx-side-title">{safe(active_theme["tagline"])}</div><div class="nx-muted" style="margin-top:.55rem">Search once. Compare smarter.</div></div>
  </div>
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
        st.markdown(f'<p style="color:var(--nx-muted);line-height:1.75;margin-top:1rem">{safe(summary[:850])}{"…" if len(summary)>850 else ""}</p>', unsafe_allow_html=True)
        if platforms:
            st.markdown('<div class="nx-label" style="margin-top:.8rem">Supported platforms</div>', unsafe_allow_html=True)
            st.markdown(''.join(f'<span class="nx-chip">{safe(p)}</span>' for p in platforms), unsafe_allow_html=True)
        if itad_game.get("itad_url"):
            st.markdown(f'<p style="margin-top:1rem"><a href="{safe(itad_game["itad_url"])}" target="_blank" style="color:{accent};text-decoration:none;font-weight:700">View on IsThereAnyDeal ↗</a></p>', unsafe_allow_html=True)

    st.markdown('<div class="nx-section">Price intelligence <span style="font-size:.8rem;color:var(--nx-muted);font-family:DM Sans;font-weight:400">/ India region</span></div>', unsafe_allow_html=True)
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
    st.markdown('<div class="nx-panel" style="margin-top:1.25rem;padding:1.6rem"><div class="nx-label">BUILT FOR SMARTER GAME SHOPPING</div><div style="font-family:var(--nx-font);font-size:1.45rem;font-weight:700;margin:.7rem 0 .45rem;color:var(--nx-text)">One search. The full picture.</div><div class="nx-muted" style="line-height:1.8;max-width:820px">Look up a PC game to see its details, compare available storefront offers, check historical lows, and follow a verified purchase link. Regional prices are shown in the currency the provider actually returns — never converted or relabelled deceptively.</div></div>', unsafe_allow_html=True)
    a,b,c = st.columns(3, gap="medium")
    with a:
        st.markdown('<div class="nx-panel" style="margin-top:1rem"><div style="font-size:1.5rem">⌕</div><b>Find the game</b><p class="nx-muted">Search by the official game title.</p></div>', unsafe_allow_html=True)
    with b:
        st.markdown('<div class="nx-panel" style="margin-top:1rem"><div style="font-size:1.5rem">₹</div><b>Compare offers</b><p class="nx-muted">See prices in the currency actually returned for India.</p></div>', unsafe_allow_html=True)
    with c:
        st.markdown('<div class="nx-panel" style="margin-top:1rem"><div style="font-size:1.5rem">⌁</div><b>Check the low</b><p class="nx-muted">Compare today’s offer with historical lows.</p></div>', unsafe_allow_html=True)
