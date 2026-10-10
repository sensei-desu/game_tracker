import html
import os
from datetime import datetime
from urllib.parse import urlparse

import requests
import streamlit as st


def safe(value):
    return html.escape(str(value or ""))


st.set_page_config(
    page_title="Nexus Game Hub",
    page_icon="🎮",
    layout="wide",
    initial_sidebar_state="collapsed",
)

THEMES = {
    "Pure Light": {
        "bg": "#F5F7FC", "panel": "#FFFFFF", "panel2": "#EDF1F8",
        "text": "#182033", "muted": "#5D687D", "line": "#D9DFEA",
        "accent": "#2563EB", "deep": "#1D4ED8", "button_text": "#FFFFFF",
        "badge": "#E9EFFB", "chip": "#EDF2FC", "radius": "18px",
        "app_bg": "radial-gradient(ellipse at 8% 0%, rgba(37,99,235,.10), transparent 32%), #F5F7FC",
        "hero_bg": "linear-gradient(120deg, #FFFFFF, #EDF2FC)",
        "deco": "✦", "deco_color": "rgba(37,99,235,.07)",
        "font": "DM Sans", "mode": "light",
        "tagline": "A brighter way to find your next game.",
    },
    "Midnight Pro": {
        "bg": "#090B12", "panel": "#141927", "panel2": "#10131D",
        "text": "#F4F6FC", "muted": "#A3ADC0", "line": "#2A3042",
        "accent": "#A78BFA", "deep": "#7C3AED", "button_text": "#100B1B",
        "badge": "#1B2030", "chip": "#191F2E", "radius": "20px",
        "app_bg": "radial-gradient(ellipse at 8% 0%, rgba(124,58,237,.19), transparent 29%), #090B12",
        "hero_bg": "linear-gradient(115deg, #16192B, #0C0F1A)",
        "deco": "N", "deco_color": "rgba(167,139,250,.04)",
        "font": "DM Sans", "mode": "dark",
        "tagline": "Your next game. Your best price.",
    },
    "Elden Ring — The Lands Between": {
        "bg": "#100F0C", "panel": "#1B1913", "panel2": "#15140F",
        "text": "#EDE4CF", "muted": "#B7AC91", "line": "#4A4028",
        "accent": "#C6A65C", "deep": "#8B6D32", "button_text": "#171208",
        "badge": "#292419", "chip": "#242016", "radius": "10px",
        "app_bg": "radial-gradient(ellipse at 75% 0%, rgba(198,166,92,.17), transparent 32%), #100F0C",
        "hero_bg": "linear-gradient(115deg, #221D13, #100F0C)",
        "deco": "✧", "deco_color": "rgba(198,166,92,.07)",
        "font": "Cinzel", "mode": "dark",
        "tagline": "A tarnished guide to better game prices.",
    },
    "Spider-Verse": {
        "bg": "#101014", "panel": "#1B171C", "panel2": "#15151C",
        "text": "#F7F4FA", "muted": "#B8ACBD", "line": "#45303A",
        "accent": "#F02D3A", "deep": "#B91C2B", "button_text": "#FFFFFF",
        "badge": "#28191F", "chip": "#211A21", "radius": "8px",
        "app_bg": "radial-gradient(ellipse at 100% 0%, rgba(22,139,255,.16), transparent 27%), #101014",
        "hero_bg": "linear-gradient(115deg, #251219, #101014)",
        "deco": "SP//", "deco_color": "rgba(240,45,58,.06)",
        "font": "Space Grotesk", "mode": "dark",
        "tagline": "Into the deals-verse. Find your best price.",
    },
    "Pixel Arcade": {
        "bg": "#11112B", "panel": "#1B1B3D", "panel2": "#151530",
        "text": "#F5F0FF", "muted": "#B9B4D8", "line": "#45416F",
        "accent": "#35F2A0", "deep": "#13B981", "button_text": "#101326",
        "badge": "#25234B", "chip": "#211F43", "radius": "2px",
        "app_bg": "linear-gradient(rgba(53,242,160,.025) 1px, transparent 1px), linear-gradient(90deg, rgba(53,242,160,.025) 1px, transparent 1px), #11112B",
        "hero_bg": "linear-gradient(135deg, #22214A, #171733)",
        "deco": "▣", "deco_color": "rgba(53,242,160,.06)",
        "font": "DM Sans", "mode": "dark",
        "tagline": "PLAYER ONE: your next great deal awaits.",
    },
    "Cyberpunk 2077": {
        "bg": "#090B10", "panel": "#171A21", "panel2": "#11141B",
        "text": "#F4F4F4", "muted": "#B3B8C4", "line": "#41434A",
        "accent": "#FCEE0A", "deep": "#D4C900", "button_text": "#171707",
        "badge": "#24251D", "chip": "#20211A", "radius": "7px",
        "app_bg": "radial-gradient(ellipse at 95% 0%, rgba(0,229,255,.10), transparent 28%), #090B10",
        "hero_bg": "linear-gradient(115deg, #22231A, #0E1015)",
        "deco": "2077", "deco_color": "rgba(252,238,10,.06)",
        "font": "Space Grotesk", "mode": "dark",
        "tagline": "Wake up, samurai. There's a deal to catch.",
    },
    "Sakura Dreams": {
        "bg": "#FFF5F8", "panel": "#FFFFFF", "panel2": "#FDEAF1",
        "text": "#422838", "muted": "#866A7A", "line": "#F1C9D9",
        "accent": "#D94F86", "deep": "#B83268", "button_text": "#FFFFFF",
        "badge": "#FCE5EE", "chip": "#FFF0F5", "radius": "22px",
        "app_bg": "radial-gradient(ellipse at 8% 0%, rgba(255,183,205,.42), transparent 32%), #FFF5F8",
        "hero_bg": "linear-gradient(120deg, #FFFFFF, #FFE7F0)",
        "deco": "✿", "deco_color": "rgba(217,79,134,.10)",
        "font": "DM Sans", "mode": "light",
        "tagline": "Soft petals. Smart prices. Your next adventure.",
    },
    "Kawaii Anime": {
        "bg": "#FBF5FF", "panel": "#FFFFFF", "panel2": "#F5EAFE",
        "text": "#332344", "muted": "#806A93", "line": "#E4D0F5",
        "accent": "#B36BE8", "deep": "#9650CC", "button_text": "#FFFFFF",
        "badge": "#F2E5FC", "chip": "#F9F0FF", "radius": "24px",
        "app_bg": "radial-gradient(ellipse at 0% 0%, rgba(255,191,220,.42), transparent 30%), radial-gradient(ellipse at 100% 5%, rgba(190,179,255,.42), transparent 32%), #FBF5FF",
        "hero_bg": "linear-gradient(125deg, #FFFFFF, #F6E8FF)",
        "deco": "♡ ✦", "deco_color": "rgba(179,107,232,.09)",
        "font": "DM Sans", "mode": "light",
        "tagline": "Cute games, cuter vibes, smarter prices.",
    },
    "Psyduck.exe": {
        "bg": "#F2FAFF", "panel": "#FFFFFF", "panel2": "#E5F5FF",
        "text": "#20364A", "muted": "#5C7C92", "line": "#B9DFF3",
        "accent": "#E9AE25", "deep": "#C98A10", "button_text": "#302207",
        "badge": "#FFF4CF", "chip": "#EAF7FF", "radius": "20px",
        "app_bg": "radial-gradient(ellipse at 10% 0%, rgba(255,222,117,.35), transparent 28%), #F2FAFF",
        "hero_bg": "linear-gradient(120deg, #FFFFFF, #E0F5FF)",
        "deco": "???", "deco_color": "rgba(233,174,37,.10)",
        "font": "DM Sans", "mode": "light",
        "tagline": "Wait... is this the cheapest deal? Psy-y-y?",
    },
    "Samurai Ink": {
        "bg": "#111110", "panel": "#1C1B19", "panel2": "#151514",
        "text": "#F0E8D8", "muted": "#B8AD9D", "line": "#413B35",
        "accent": "#B62E32", "deep": "#8C2027", "button_text": "#FFFFFF",
        "badge": "#28201F", "chip": "#241D1B", "radius": "9px",
        "app_bg": "radial-gradient(ellipse at 95% 0%, rgba(182,46,50,.15), transparent 28%), #111110",
        "hero_bg": "linear-gradient(115deg, #221D1B, #111110)",
        "deco": "筆", "deco_color": "rgba(182,46,50,.07)",
        "font": "Noto Sans JP", "mode": "dark",
        "tagline": "Precision in every search. Discipline in every deal.",
    },
    "Nordic Frost": {
        "bg": "#0B121B", "panel": "#16212D", "panel2": "#101A25",
        "text": "#E5F1F7", "muted": "#A7BFCD", "line": "#304653",
        "accent": "#9BDDF4", "deep": "#5EB7D7", "button_text": "#10202A",
        "badge": "#1D303C", "chip": "#192B37", "radius": "13px",
        "app_bg": "radial-gradient(ellipse at 50% 0%, rgba(155,221,244,.15), transparent 35%), #0B121B",
        "hero_bg": "linear-gradient(120deg, #192A37, #0B121B)",
        "deco": "❄", "deco_color": "rgba(155,221,244,.07)",
        "font": "Space Grotesk", "mode": "dark",
        "tagline": "Chill out. Find your next adventure for less.",
    },
    "Pastel Dream": {
        "bg": "#F7F3FF", "panel": "#FFFFFF", "panel2": "#F0EAFE",
        "text": "#302A40", "muted": "#786D8E", "line": "#DDD2F3",
        "accent": "#8D73D6", "deep": "#7157BB", "button_text": "#FFFFFF",
        "badge": "#EDE5FC", "chip": "#F4EEFF", "radius": "22px",
        "app_bg": "radial-gradient(ellipse at 0% 0%, rgba(220,206,255,.48), transparent 32%), #F7F3FF",
        "hero_bg": "linear-gradient(120deg, #FFFFFF, #EEE8FF)",
        "deco": "☁", "deco_color": "rgba(141,115,214,.08)",
        "font": "DM Sans", "mode": "light",
        "tagline": "A cozy corner of the internet for game deals.",
    },
    "Minecraft World": {
        "bg": "#121B13", "panel": "#1B2B1C", "panel2": "#152218",
        "text": "#E7F1DF", "muted": "#B1C6A8", "line": "#405A3C",
        "accent": "#72D34B", "deep": "#429A35", "button_text": "#10200E",
        "badge": "#263D25", "chip": "#21351F", "radius": "3px",
        "app_bg": "linear-gradient(rgba(114,211,75,.035) 2px, transparent 2px), linear-gradient(90deg, rgba(114,211,75,.035) 2px, transparent 2px), #121B13",
        "hero_bg": "linear-gradient(120deg, #253C23, #132215)",
        "deco": "▧", "deco_color": "rgba(114,211,75,.07)",
        "font": "DM Sans", "mode": "dark",
        "tagline": "Craft your library. Mine the best prices.",
    },
    "Jujutsu Kaisen — Cursed Energy": {
        "bg": "#0D0B14", "panel": "#1A1525", "panel2": "#130F1D",
        "text": "#F1EBFF", "muted": "#B7A9D0", "line": "#45305D",
        "accent": "#A78BFA", "deep": "#6D28D9", "button_text": "#FFFFFF",
        "badge": "#251B35", "chip": "#20182D", "radius": "12px",
        "app_bg": "radial-gradient(ellipse at 8% 0%, rgba(124,58,237,.24), transparent 30%), #0D0B14",
        "hero_bg": "linear-gradient(120deg, #231636, #0E0C17)",
        "deco": "呪", "deco_color": "rgba(167,139,250,.08)",
        "font": "Noto Sans JP", "mode": "dark",
        "tagline": "Compare prices with cursed-energy precision.",
    },
    "Gamer's Library": {
        "bg": "#171A1E", "panel": "#22272D", "panel2": "#1C2126",
        "text": "#E8EBEF", "muted": "#A9B1BB", "line": "#3A424B",
        "accent": "#A4D037", "deep": "#7CA321", "button_text": "#1A210B",
        "badge": "#2C3523", "chip": "#272F22", "radius": "14px",
        "app_bg": "radial-gradient(ellipse at 85% 0%, rgba(164,208,55,.12), transparent 30%), #171A1E",
        "hero_bg": "linear-gradient(120deg, #272E2F, #181C1F)",
        "deco": "▤", "deco_color": "rgba(164,208,55,.06)",
        "font": "DM Sans", "mode": "dark",
        "tagline": "Your library, your prices, your next play.",
    },
}

THEME_NAMES = list(THEMES.keys())

# Read theme choices from URL so refreshes/bookmarks preserve the selection.
query_theme = st.query_params.get("theme", "Midnight Pro")
if query_theme not in THEMES:
    query_theme = "Midnight Pro"

query_jjk = st.query_params.get("jjk", "Gojo — Infinity")
if query_jjk not in ("Gojo — Infinity", "Sukuna — Malevolent Shrine"):
    query_jjk = "Gojo — Infinity"

if "theme_choice" not in st.session_state:
    st.session_state.theme_choice = query_theme
if "jjk_choice" not in st.session_state:
    st.session_state.jjk_choice = query_jjk


def sync_theme_query():
    st.query_params["theme"] = st.session_state.theme_choice


def sync_jjk_query():
    st.query_params["jjk"] = st.session_state.jjk_choice


with st.sidebar:
    st.markdown("## ⚙️ Preferences")
    backend_url = st.text_input(
        "Backend URL",
        value=os.getenv("BACKEND_API_URL", "http://127.0.0.1:8000"),
        help="Set BACKEND_API_URL in the frontend environment on Render.",
    ).strip().rstrip("/")
    st.caption("Nexus Game Hub · India region")
    st.caption("Your theme choice is saved in the page URL.")

controls = st.columns([1.35, 1, 2.1], vertical_alignment="bottom", gap="medium")

with controls[0]:
    st.markdown(
        '<div style="font-size:.72rem;letter-spacing:.15em;font-weight:800;'
        'opacity:.75;margin-bottom:.35rem">THEME STUDIO</div>',
        unsafe_allow_html=True,
    )
    st.selectbox(
        "Choose your world",
        THEME_NAMES,
        key="theme_choice",
        on_change=sync_theme_query,
        label_visibility="collapsed",
    )

with controls[1]:
    if st.session_state.theme_choice == "Jujutsu Kaisen — Cursed Energy":
        st.selectbox(
            "Cursed technique",
            ["Gojo — Infinity", "Sukuna — Malevolent Shrine"],
            key="jjk_choice",
            on_change=sync_jjk_query,
            label_visibility="collapsed",
        )
    else:
        st.markdown(
            '<div style="padding:.65rem 0;color:#A3ADC0;font-size:.85rem">'
            '✦ 15 visual worlds</div>',
            unsafe_allow_html=True,
        )

with controls[2]:
    st.markdown(
        '<div style="padding:.65rem 0;color:#A3ADC0;font-size:.85rem">'
        'Switch themes anytime — search and price data stay intact.</div>',
        unsafe_allow_html=True,
    )

active_theme_name = st.session_state.theme_choice
active_theme = dict(THEMES[active_theme_name])

if active_theme_name == "Jujutsu Kaisen — Cursed Energy":
    if st.session_state.jjk_choice == "Sukuna — Malevolent Shrine":
        active_theme.update({
            "bg": "#10090D", "panel": "#211218", "panel2": "#170D12",
            "text": "#FFF0F1", "muted": "#D1AAB0", "line": "#5C2735",
            "accent": "#F04452", "deep": "#B91C35",
            "button_text": "#FFFFFF", "badge": "#321722", "chip": "#29141C",
            "app_bg": "radial-gradient(ellipse at 10% 0%, rgba(240,68,82,.24), transparent 30%), #10090D",
            "hero_bg": "linear-gradient(120deg, #37131D, #11090E)",
            "deco": "両面", "deco_color": "rgba(240,68,82,.09)",
            "tagline": "Enter the shrine. Find the deal.",
        })
    else:
        active_theme.update({
            "bg": "#080D18", "panel": "#111A2C", "panel2": "#0D1422",
            "text": "#EDF6FF", "muted": "#A9C3E0", "line": "#263F68",
            "accent": "#54B8FF", "deep": "#6D4AFF",
            "button_text": "#081321", "badge": "#172943", "chip": "#142239",
            "app_bg": "radial-gradient(ellipse at 10% 0%, rgba(84,184,255,.23), transparent 30%), #080D18",
            "hero_bg": "linear-gradient(120deg, #112544, #080D18)",
            "deco": "無量空処", "deco_color": "rgba(84,184,255,.09)",
            "tagline": "Limitless style. Unlimited game deals.",
        })

with st.sidebar:
    st.markdown(f"### {safe(active_theme_name)}")
    if active_theme_name == "Jujutsu Kaisen — Cursed Energy":
        st.caption(
            "Gojo's Infinity"
            if st.session_state.jjk_choice.startswith("Gojo")
            else "Sukuna's Malevolent Shrine"
        )
    st.markdown("**Theme preview**")
    swatches = "".join(
        f'<span style="width:23px;height:23px;border-radius:7px;'
        f'background:{color};border:1px solid {active_theme["line"]};'
        'display:inline-block"></span>'
        for color in [
            active_theme["bg"],
            active_theme["panel"],
            active_theme["accent"],
            active_theme["text"],
        ]
    )
    st.markdown(
        f'<div style="display:flex;gap:7px;margin:.3rem 0 1rem">{swatches}</div>',
        unsafe_allow_html=True,
    )

font_imports = (
    "DM+Sans:wght@400;500;600;700;800"
    "&family=Space+Grotesk:wght@400;500;600;700"
    "&family=Cinzel:wght@400;500;600;700"
    "&family=Noto+Sans+JP:wght@400;500;700"
)

hero_kicker = "YOUR NEXT GAME / YOUR BEST PRICE"
if active_theme_name == "Jujutsu Kaisen — Cursed Energy":
    hero_kicker = "CURSED ENERGY / PRICE INTELLIGENCE"
elif active_theme_name == "Psyduck.exe":
    hero_kicker = "CONFUSED? LET'S FIND THAT DEAL."
elif active_theme_name == "Sakura Dreams":
    hero_kicker = "SAKURA SEASON / SMART GAME SHOPPING"

# CSS is assembled without an f-string. This avoids the unmatched-brace
# SyntaxError that was breaking the previous deployment.
css = """
@import url('https://fonts.googleapis.com/css2?family=FONT_IMPORTS&display=swap');
:root {
 --nx-bg:BG; --nx-panel:PANEL; --nx-panel2:PANEL2; --nx-text:TEXT;
 --nx-muted:MUTED; --nx-line:LINE; --nx-accent:ACCENT; --nx-deep:DEEP;
 --nx-button-text:BUTTON_TEXT; --nx-badge:BADGE; --nx-chip:CHIP;
 --nx-radius:RADIUS; --nx-deco:DECO_COLOR; --nx-font:'FONT',sans-serif;
}
.stApp {background:APP_BG;color:var(--nx-text);}
[data-testid="stHeader"] {background:transparent;}
.block-container {max-width:1160px;padding-top:1.5rem;padding-bottom:4rem;}
.nx-topline {display:flex;align-items:center;gap:9px;color:var(--nx-muted);font-size:.7rem;letter-spacing:.18em;font-weight:800;margin-bottom:1rem;}
.nx-dot {width:7px;height:7px;border-radius:50%;background:var(--nx-accent);box-shadow:0 0 14px var(--nx-accent);}
.nx-hero {position:relative;overflow:hidden;border:1px solid var(--nx-line);border-radius:var(--nx-radius);background:HERO_BG;padding:clamp(1.5rem,4vw,3.5rem);display:grid;grid-template-columns:minmax(0,1.5fr) minmax(220px,.7fr);gap:2rem;align-items:center;margin-bottom:1.25rem;}
.nx-hero:before {content:"DECO";position:absolute;right:3%;top:-18%;font-size:clamp(9rem,20vw,17rem);font-weight:900;line-height:1;color:var(--nx-deco);pointer-events:none;white-space:nowrap;}
.nx-kicker {color:var(--nx-accent);font-size:.76rem;letter-spacing:.14em;text-transform:uppercase;font-weight:800;margin-bottom:.75rem;position:relative;z-index:1;}
.nx-title {font-family:var(--nx-font);font-size:clamp(2.5rem,6vw,5rem);font-weight:800;line-height:.99;letter-spacing:-.06em;margin:0 0 1rem;color:var(--nx-text);position:relative;z-index:1;}
.nx-title span {color:var(--nx-accent);}
.nx-subtitle {max-width:610px;color:var(--nx-muted);font-size:1.02rem;line-height:1.7;position:relative;z-index:1;}
.nx-badges {display:flex;flex-wrap:wrap;gap:8px;margin-top:1.25rem;position:relative;z-index:1;}
.nx-badge {border:1px solid var(--nx-line);background:var(--nx-badge);border-radius:999px;padding:7px 12px;color:var(--nx-text);font-size:.75rem;}
.nx-hero-side {border:1px solid var(--nx-line);background:var(--nx-panel2);border-radius:var(--nx-radius);padding:1.25rem;min-height:205px;display:flex;flex-direction:column;justify-content:space-between;position:relative;z-index:1;}
.nx-orbit {width:72px;height:72px;border-radius:var(--nx-radius);display:grid;place-items:center;background:linear-gradient(135deg,var(--nx-accent),var(--nx-deep));color:var(--nx-button-text);font-size:2rem;}
.nx-side-caption {color:var(--nx-muted);text-transform:uppercase;font-size:.68rem;letter-spacing:.15em;font-weight:800;}
.nx-side-title {font-family:var(--nx-font);font-size:1.4rem;font-weight:800;line-height:1.2;margin-top:.4rem;color:var(--nx-text);}
.nx-muted {color:var(--nx-muted);font-size:.9rem;}
.nx-section {font-family:var(--nx-font);font-size:1.4rem;font-weight:800;margin:1.65rem 0 .85rem;color:var(--nx-text);}
.nx-panel {background:linear-gradient(145deg,var(--nx-panel),var(--nx-panel2));border:1px solid var(--nx-line);border-radius:var(--nx-radius);padding:1.15rem;height:100%;}
.nx-price {font-family:var(--nx-font);font-size:clamp(1.45rem,2.5vw,2rem);font-weight:800;letter-spacing:-.04em;color:var(--nx-text);}
.nx-label {color:var(--nx-muted);text-transform:uppercase;font-size:.7rem;letter-spacing:.12em;font-weight:800;}
.nx-store {background:linear-gradient(105deg,var(--nx-panel),var(--nx-panel2));border:1px solid var(--nx-line);border-radius:var(--nx-radius);padding:17px 18px;margin:9px 0;display:flex;align-items:center;gap:14px;transition:transform .18s ease,border-color .18s ease;}
.nx-store:hover {transform:translateY(-2px);border-color:var(--nx-accent);}
.nx-store-name {font-weight:800;color:var(--nx-text);}
.nx-store-sub {color:var(--nx-muted);font-size:.78rem;margin-top:3px;}
.nx-store-price {margin-left:auto;text-align:right;white-space:nowrap;font-family:var(--nx-font);font-size:1.15rem;font-weight:800;color:var(--nx-text);}
.nx-buy-btn {display:inline-flex;align-items:center;justify-content:center;margin-top:9px;padding:9px 13px;border-radius:10px;background:var(--nx-accent);color:var(--nx-button-text)!important;font-size:.78rem;font-weight:800;text-decoration:none!important;border:1px solid var(--nx-accent);}
.nx-buy-btn:hover {filter:brightness(1.08);}
.nx-no-link {display:inline-block;margin-top:9px;color:var(--nx-muted);font-size:.72rem;}
.nx-discount {display:inline-block;background:rgba(90,190,90,.14);color:DISCOUNT_COLOR;border:1px solid rgba(90,190,90,.28);padding:3px 7px;border-radius:7px;font-size:.72rem;margin-top:5px;}
.nx-game-title {font-family:var(--nx-font);font-size:2rem;font-weight:800;line-height:1.1;letter-spacing:-.04em;color:var(--nx-text);}
.nx-cover {width:100%;border-radius:var(--nx-radius);border:1px solid var(--nx-line);object-fit:cover;max-height:320px;}
.nx-chip {display:inline-block;border:1px solid var(--nx-line);color:var(--nx-text);background:var(--nx-chip);border-radius:8px;padding:5px 9px;margin:3px 5px 3px 0;font-size:.78rem;}
.stTextInput input {background:var(--nx-panel)!important;border:1px solid var(--nx-line)!important;border-radius:var(--nx-radius)!important;color:var(--nx-text)!important;min-height:3.35rem;font-size:1rem;}
.stTextInput input:focus {border-color:var(--nx-accent)!important;box-shadow:0 0 0 1px var(--nx-accent)!important;}
.stSelectbox div[data-baseweb="select"]>div {background:var(--nx-panel)!important;border-color:var(--nx-line)!important;border-radius:12px!important;color:var(--nx-text)!important;}
.stButton>button,.stFormSubmitButton>button {border-radius:var(--nx-radius);border:1px solid var(--nx-accent);background:var(--nx-accent);color:var(--nx-button-text);font-weight:800;min-height:3.35rem;}
[data-testid="stMetric"] {background:var(--nx-panel);border:1px solid var(--nx-line);border-radius:var(--nx-radius);padding:1rem;}
[data-testid="stMetricLabel"],[data-testid="stMetricValue"] {color:var(--nx-text);}
hr {border-color:var(--nx-line)!important;}
footer {visibility:hidden;}
@media(max-width:800px) {
 .nx-hero {display:block;padding:1.4rem 1.2rem;}
 .nx-hero-side {display:none;}
 .nx-store {align-items:flex-start;flex-wrap:wrap;}
 .nx-store-price {font-size:1rem;}
 .nx-title {font-size:clamp(2.4rem,11vw,4rem);}
}
@media(prefers-reduced-motion:reduce) {
 *,*::before,*::after {transition:none!important;animation:none!important;}
}
"""

replacements = {
    "FONT_IMPORTS": font_imports,
    "BG": active_theme["bg"],
    "PANEL": active_theme["panel"],
    "PANEL2": active_theme["panel2"],
    "TEXT": active_theme["text"],
    "MUTED": active_theme["muted"],
    "LINE": active_theme["line"],
    "ACCENT": active_theme["accent"],
    "DEEP": active_theme["deep"],
    "BUTTON_TEXT": active_theme["button_text"],
    "BADGE": active_theme["badge"],
    "CHIP": active_theme["chip"],
    "RADIUS": active_theme["radius"],
    "DECO_COLOR": active_theme["deco_color"],
    "FONT": active_theme["font"],
    "APP_BG": active_theme["app_bg"],
    "HERO_BG": active_theme["hero_bg"],
    "DECO": active_theme["deco"],
    "DISCOUNT_COLOR": "#226B2D" if active_theme["mode"] == "light" else "#A9ED9D",
}

for placeholder, value in replacements.items():
    css = css.replace(placeholder, value)

st.markdown("<style>" + css + "</style>", unsafe_allow_html=True)

st.markdown(
    '<div class="nx-topline"><span class="nx-dot"></span>'
    'NEXUS / GAME INTELLIGENCE</div>'
    '<section class="nx-hero"><div>'
    '<div class="nx-kicker">' + safe(hero_kicker) + '</div>'
    '<div class="nx-title">Play more.<br><span>Pay less.</span></div>'
    '<div class="nx-subtitle">A smarter way to shop for PC games. '
    'Compare storefront offers, check historical lows, and jump straight '
    'to the store — all in one place.</div>'
    '<div class="nx-badges"><span class="nx-badge">◈ India region</span>'
    '<span class="nx-badge">↗ Multi-store comparison</span>'
    '<span class="nx-badge">⌁ Historical lows</span></div></div>'
    '<div class="nx-hero-side"><div class="nx-orbit">'
    + ("🦆" if active_theme_name == "Psyduck.exe"
       else "🌸" if active_theme_name == "Sakura Dreams"
       else "♡" if active_theme_name == "Kawaii Anime"
       else "⛏" if active_theme_name == "Minecraft World"
       else "呪" if active_theme_name == "Jujutsu Kaisen — Cursed Energy"
       else "✦")
    + '</div><div><div class="nx-side-caption">' + safe(active_theme_name)
    + '</div><div class="nx-side-title">' + safe(active_theme["tagline"])
    + '</div><div class="nx-muted" style="margin-top:.55rem">'
    'Search once. Compare smarter.</div></div></div></section>',
    unsafe_allow_html=True,
)

with st.form("game_search", clear_on_submit=False):
    c1, c2 = st.columns([5, 1.25], vertical_alignment="bottom", gap="small")
    with c1:
        game_query = st.text_input(
            "SEARCH THE LIBRARY",
            placeholder="Try Elden Ring, Cyberpunk 2077, Hades II…",
            label_visibility="collapsed",
        )
    with c2:
        submitted = st.form_submit_button("⌕  Find a game", use_container_width=True)

if submitted:
    if not game_query.strip():
        st.warning("Enter a game title to start searching.")
    else:
        try:
            with st.spinner("Searching game databases and regional prices…"):
                response = requests.get(
                    f"{backend_url}/api/game/"
                    f"{requests.utils.quote(game_query.strip(), safe='')}",
                    timeout=25,
                )
            if response.ok:
                st.session_state["nexus_result"] = response.json()
                st.session_state["nexus_query"] = game_query.strip()
                st.session_state.pop("nexus_error", None)
            else:
                try:
                    detail = response.json().get("detail", "")
                except ValueError:
                    detail = ""
                st.session_state.pop("nexus_result", None)
                st.session_state["nexus_error"] = (
                    f"{detail or 'Search failed.'} (HTTP {response.status_code})"
                )
        except requests.RequestException:
            st.session_state["nexus_error"] = (
                f"Could not reach the backend at {backend_url}. "
                "Check that FastAPI is running and the URL is correct."
            )
            st.session_state.pop("nexus_result", None)

if st.session_state.get("nexus_error"):
    st.error(st.session_state["nexus_error"])


def money(value, currency=""):
    if value is None or value == "":
        return "Unavailable"
    try:
        amount = float(value)
    except (TypeError, ValueError):
        return "Unavailable"

    currency = (currency or "").upper()
    if currency == "INR":
        return f"₹{amount:,.2f}".rstrip("0").rstrip(".")
    if currency == "USD":
        return f"${amount:,.2f}"
    if currency == "EUR":
        return f"€{amount:,.2f}"
    if currency == "GBP":
        return f"£{amount:,.2f}"
    return f"{amount:,.2f} {currency}".strip()


result = st.session_state.get("nexus_result")

if result:
    igdb = result.get("igdb") or {}
    prices = result.get("prices") or {}
    history = result.get("history") or {}
    itad_game = result.get("itad_game") or {}
    deals = prices.get("deals") or []

    game_title = (
        igdb.get("name")
        or itad_game.get("title")
        or st.session_state.get("nexus_query", "Game details")
    )
    summary = (
        igdb.get("summary")
        or "Game description is not available from the metadata provider."
    ).strip()

    platform_data = igdb.get("platforms") or []
    platforms = [
        p.get("name") if isinstance(p, dict) else str(p)
        for p in platform_data
    ]
    genres_data = igdb.get("genres") or []
    genres = [
        g.get("name") if isinstance(g, dict) else str(g)
        for g in genres_data
    ]

    release = igdb.get("first_release_date")
    release_year = (
        datetime.fromtimestamp(release).year
        if isinstance(release, (int, float))
        else None
    )

    assets = itad_game.get("assets") or {}
    cover = (
        igdb.get("cover_url")
        or assets.get("banner400")
        or assets.get("boxart")
    )

    st.markdown(
        '<div class="nx-section">Game overview</div>',
        unsafe_allow_html=True,
    )
    left, right = st.columns([1, 2.4], gap="large")

    with left:
        if cover and urlparse(str(cover)).scheme in ("http", "https"):
            st.markdown(
                f'<img class="nx-cover" src="{safe(cover)}" '
                f'alt="{safe(game_title)} cover">',
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                '<div class="nx-panel" style="text-align:center;'
                'padding:3rem 1rem;font-size:4rem">🎮</div>',
                unsafe_allow_html=True,
            )

    with right:
        st.markdown(
            f'<div class="nx-game-title">{safe(game_title)}</div>',
            unsafe_allow_html=True,
        )

        metadata = []
        if release_year:
            metadata.append(f"Released {release_year}")
        if genres:
            metadata.extend(genres[:3])

        if metadata:
            st.markdown(
                "".join(
                    f'<span class="nx-chip">{safe(item)}</span>'
                    for item in metadata
                ),
                unsafe_allow_html=True,
            )

        st.markdown(
            '<p style="color:var(--nx-muted);line-height:1.75;'
            'margin-top:1rem">'
            + safe(summary[:850])
            + ("…" if len(summary) > 850 else "")
            + "</p>",
            unsafe_allow_html=True,
        )

        if platforms:
            st.markdown(
                '<div class="nx-label" style="margin-top:.8rem">'
                'Supported platforms</div>',
                unsafe_allow_html=True,
            )
            st.markdown(
                "".join(
                    f'<span class="nx-chip">{safe(platform)}</span>'
                    for platform in platforms
                ),
                unsafe_allow_html=True,
            )

        itad_url = itad_game.get("itad_url")
        if itad_url and urlparse(str(itad_url)).scheme in ("http", "https"):
            st.markdown(
                f'<p style="margin-top:1rem"><a href="{safe(itad_url)}" '
                f'target="_blank" rel="noopener noreferrer" '
                f'style="color:{active_theme["accent"]};'
                'text-decoration:none;font-weight:700">'
                'View on IsThereAnyDeal ↗</a></p>',
                unsafe_allow_html=True,
            )

    st.markdown(
        '<div class="nx-section">Price intelligence '
        '<span style="font-size:.8rem;color:var(--nx-muted);'
        'font-family:DM Sans;font-weight:400">/ India region</span></div>',
        unsafe_allow_html=True,
    )

    low = history.get("low") or {}
    low_amount = low.get("amount")
    low_currency = low.get("currency", "")
    cheapest = deals[0] if deals else None

    metric1, metric2, metric3 = st.columns(3, gap="medium")

    with metric1:
        cheapest_price = (cheapest or {}).get("price") or {}
        cheapest_shop = (cheapest or {}).get("shop") or {}
        st.markdown(
            '<div class="nx-panel"><div class="nx-label">'
            'Best current price</div><div class="nx-price" '
            'style="color:' + active_theme["accent"] + '">'
            + money(cheapest_price.get("amount"), cheapest_price.get("currency"))
            + '</div><div class="nx-muted">'
            + safe(cheapest_shop.get("name", "No deal found"))
            + "</div></div>",
            unsafe_allow_html=True,
        )

    with metric2:
        low_shop = low.get("shop") or {}
        st.markdown(
            '<div class="nx-panel"><div class="nx-label">All-time low</div>'
            '<div class="nx-price">'
            + money(low_amount, low_currency)
            + '</div><div class="nx-muted">'
            + safe(
                low_shop.get("name", "Across tracked stores")
                if low_amount is not None
                else "No history available"
            )
            + "</div></div>",
            unsafe_allow_html=True,
        )

    with metric3:
        st.markdown(
            '<div class="nx-panel"><div class="nx-label">Stores compared</div>'
            '<div class="nx-price">' + str(len(deals))
            + '</div><div class="nx-muted">'
            'Live offers returned by provider</div></div>',
            unsafe_allow_html=True,
        )

    if deals:
        st.markdown(
            '<div class="nx-section">Available offers</div>',
            unsafe_allow_html=True,
        )

        for index, deal in enumerate(deals):
            shop_data = deal.get("shop") or {}
            shop = shop_data.get("name", "Store")
            price = deal.get("price") or {}
            regular = deal.get("regular") or {}
            currency = price.get("currency", "")

            try:
                discount = int(deal.get("cut") or 0)
            except (TypeError, ValueError):
                discount = 0

            url = deal.get("url")
            parsed = urlparse(str(url)) if url else None
            valid_url = bool(
                parsed
                and parsed.scheme in ("http", "https")
                and parsed.netloc
            )

            deal_html = (
                '<div class="nx-store"><div style="font-size:1.45rem;'
                'width:34px;text-align:center">'
                + ("🏆" if index == 0 else "🛒")
                + '</div><div style="flex:1"><div class="nx-store-name">'
                + safe(shop)
                + '</div><div class="nx-store-sub">'
            )

            try:
                regular_amount = float(regular.get("amount") or 0)
                current_amount = float(price.get("amount") or 0)
            except (TypeError, ValueError):
                regular_amount = current_amount = 0

            if regular_amount > current_amount:
                deal_html += (
                    "Regular "
                    + safe(money(regular_amount, regular.get("currency", currency)))
                    + f" · Save {discount}%"
                )
            else:
                deal_html += (
                    "Current listed price"
                    if discount == 0
                    else f"{discount}% off"
                )

            deal_html += "</div>"

            if discount > 0:
                deal_html += (
                    f'<span class="nx-discount">-{discount}%</span>'
                )

            deal_html += "</div><div class=\"nx-store-price\">"
            deal_html += safe(money(price.get("amount"), currency))

            if valid_url:
                deal_html += (
                    '<div><a class="nx-buy-btn" href="'
                    + safe(url)
                    + '" target="_blank" rel="noopener noreferrer">'
                    + "Buy at " + safe(shop) + " ↗</a></div>"
                )
            else:
                deal_html += (
                    '<div class="nx-no-link">Purchase link unavailable</div>'
                )

            deal_html += "</div></div>"
            st.markdown(deal_html, unsafe_allow_html=True)

        st.caption(
            "Prices and currency codes are shown as returned by the provider "
            "for the India region. Store availability and regional pricing vary."
        )
    else:
        st.info(
            "No price offers were returned for India for this title. "
            "Try another title or check the provider's regional coverage."
        )

    if not igdb:
        st.info(
            "Detailed game metadata was unavailable. "
            "Price information may still be available from the pricing provider."
        )

    st.markdown("<hr>", unsafe_allow_html=True)
    st.caption(
        "Pricing by IsThereAnyDeal API · Game metadata by IGDB. "
        "Nexus Game Hub is an independent project."
    )

else:
    st.markdown(
        '<div class="nx-panel" style="margin-top:1.25rem;padding:1.6rem">'
        '<div class="nx-label">BUILT FOR SMARTER GAME SHOPPING</div>'
        '<div style="font-family:var(--nx-font);font-size:1.45rem;'
        'font-weight:700;margin:.7rem 0 .45rem;color:var(--nx-text)">'
        'One search. The full picture.</div>'
        '<div class="nx-muted" style="line-height:1.8;max-width:820px">'
        'Look up a PC game to see its details, compare storefront offers, '
        'check historical lows, and follow a purchase link. Regional prices '
        'are shown in the currency returned by the provider.</div></div>',
        unsafe_allow_html=True,
    )

    col1, col2, col3 = st.columns(3, gap="medium")

    with col1:
        st.markdown(
            '<div class="nx-panel" style="margin-top:1rem">'
            '<div style="font-size:1.5rem">⌕</div><b>Find the game</b>'
            '<p class="nx-muted">Search by the official game title.</p></div>',
            unsafe_allow_html=True,
        )

    with col2:
        st.markdown(
            '<div class="nx-panel" style="margin-top:1rem">'
            '<div style="font-size:1.5rem">₹</div><b>Compare offers</b>'
            '<p class="nx-muted">See the currency actually returned for India.</p></div>',
            unsafe_allow_html=True,
        )

    with col3:
        st.markdown(
            '<div class="nx-panel" style="margin-top:1rem">'
            '<div style="font-size:1.5rem">⌁</div><b>Check the low</b>'
            '<p class="nx-muted">Compare current offers with historical lows.</p></div>',
            unsafe_allow_html=True,
        )

st.markdown(
    '<div style="text-align:center;color:var(--nx-muted);'
    'font-size:.75rem;margin-top:3rem">'
    'NEXUS GAME HUB · Compare prices, then buy directly from the store'
    '</div>',
    unsafe_allow_html=True,
)
