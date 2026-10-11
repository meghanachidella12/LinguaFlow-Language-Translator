import json
import html
from datetime import datetime
from pathlib import Path

import requests
import streamlit as st
import streamlit.components.v1 as components
from deep_translator import GoogleTranslator
from deep_translator.exceptions import TooManyRequests
from langdetect import detect, LangDetectException


# =========================================================
# LinguaFlow — simple blue banner, readable themes, no phrasebook
# =========================================================

st.set_page_config(
    page_title="LinguaFlow | Language without limits",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="expanded",
)

APP_DIR = Path(__file__).resolve().parent
DATA_FILE = APP_DIR / "linguaflow_data.json"

LANGUAGES = {
    "English": "en",
    "Telugu": "te",
    "Hindi": "hi",
    "Tamil": "ta",
    "Kannada": "kn",
    "Malayalam": "ml",
    "Bengali": "bn",
    "Marathi": "mr",
    "Gujarati": "gu",
    "Punjabi": "pa",
    "Urdu": "ur",
    "Spanish": "es",
    "French": "fr",
    "German": "de",
    "Italian": "it",
    "Portuguese": "pt",
    "Russian": "ru",
    "Japanese": "ja",
    "Korean": "ko",
    "Chinese (Simplified)": "zh-CN",
    "Arabic": "ar",
    "Turkish": "tr",
    "Dutch": "nl",
    "Greek": "el",
    "Thai": "th",
    "Vietnamese": "vi",
    "Indonesian": "id",
    "Swahili": "sw",
    "Polish": "pl",
    "Ukrainian": "uk",
}

def load_data():
    default = {"history": [], "favorites": []}
    if not DATA_FILE.exists():
        return default
    try:
        with DATA_FILE.open("r", encoding="utf-8") as f:
            raw = json.load(f)
        return {
            "history": raw.get("history", []) if isinstance(raw.get("history", []), list) else [],
            "favorites": raw.get("favorites", []) if isinstance(raw.get("favorites", []), list) else [],
        }
    except (OSError, json.JSONDecodeError):
        return default

def save_data():
    try:
        with DATA_FILE.open("w", encoding="utf-8") as f:
            json.dump(st.session_state.data, f, ensure_ascii=False, indent=2)
    except OSError:
        st.warning("Could not save local data. Check folder permissions.")

if "data" not in st.session_state:
    st.session_state.data = load_data()
if "page" not in st.session_state:
    st.session_state.page = "Translator"
if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = False
if "result" not in st.session_state:
    st.session_state.result = ""
if "last_error" not in st.session_state:
    st.session_state.last_error = ""
if "provider_message" not in st.session_state:
    st.session_state.provider_message = ""
if "source_language" not in st.session_state:
    st.session_state.source_language = "Auto-detect"
if "target_language" not in st.session_state:
    st.session_state.target_language = "Telugu"
if "original_text" not in st.session_state:
    st.session_state.original_text = ""
if "swap_message" not in st.session_state:
    st.session_state.swap_message = ""


# ---------------- Translation providers ----------------

def get_source_code(text, selected_source):
    if selected_source != "Auto-detect":
        return LANGUAGES[selected_source]
    try:
        detected = detect(text)
        return detected
    except LangDetectException:
        return "en"

def translate_mymemory(text, source_code, target_code):
    response = requests.get(
        "https://api.mymemory.translated.net/get",
        params={"q": text, "langpair": f"{source_code}|{target_code}"},
        timeout=15,
        headers={"User-Agent": "LinguaFlow/1.0"},
    )
    response.raise_for_status()
    payload = response.json()
    if payload.get("responseStatus") != 200:
        raise RuntimeError(str(payload.get("responseDetails", "MyMemory is unavailable.")))
    translated = html.unescape(
        payload.get("responseData", {}).get("translatedText", "") or ""
    ).strip()
    if not translated or "<html" in translated.lower():
        raise RuntimeError("MyMemory returned an empty or invalid result.")
    return translated

def translate_google(text, source_code, target_code):
    return GoogleTranslator(source=source_code, target=target_code).translate(text)

def translate_text(text, source_name, target_name):
    text = text.strip()
    if not text:
        raise ValueError("Please enter some text before translating.")
    if len(text) > 4500:
        raise ValueError("Please keep the text under 4,500 characters.")

    source_code = get_source_code(text, source_name)
    target_code = LANGUAGES[target_name]
    if source_code.lower() == target_code.lower():
        return text, "The source and target languages are the same."

    errors = []
    try:
        result = translate_mymemory(text, source_code, target_code)
        return result, "Translated using MyMemory."
    except Exception as exc:
        errors.append(f"MyMemory: {exc}")

    try:
        result = translate_google(text, source_code, target_code)
        if result and result.strip():
            return result, "Translated using Google."
        raise RuntimeError("Google returned an empty result.")
    except TooManyRequests:
        errors.append("Google is temporarily rate-limiting requests.")
    except Exception as exc:
        errors.append(f"Google: {exc}")

    raise RuntimeError(
        "Both translation services are unavailable right now. Please wait and try again.\n\n"
        + "\n".join(errors)
    )


# ---------------- Callbacks: avoid widget state errors ----------------

def choose_quick_language(language):
    st.session_state.target_language = language
    st.session_state.page = "Translator"

def choose_language_from_list(language):
    st.session_state.target_language = language
    st.session_state.page = "Translator"

def swap_languages():
    source = st.session_state.get("source_language", "Auto-detect")
    target = st.session_state.get("target_language", "Telugu")
    if source == "Auto-detect":
        st.session_state.swap_message = "Choose a source language before swapping."
        return
    st.session_state.source_language = target
    st.session_state.target_language = source
    st.session_state.swap_message = ""


# ---------------- Theme CSS ----------------

if st.session_state.dark_mode:
    BG, PANEL, TEXT, MUTED, BORDER, FIELD, LABEL = (
        "#0d1426", "#17213a", "#f4f7ff", "#c0cbe4",
        "#30405f", "#111b31", "#c9d6ff"
    )
else:
    BG, PANEL, TEXT, MUTED, BORDER, FIELD, LABEL = (
        "#f4f7ff", "#ffffff", "#192440", "#66728d",
        "#dce4f4", "#ffffff", "#53617c"
    )

st.markdown(
    f"""
    <style>
    :root {{
      --lf-bg:{BG}; --lf-panel:{PANEL}; --lf-text:{TEXT};
      --lf-muted:{MUTED}; --lf-border:{BORDER}; --lf-field:{FIELD};
      --lf-label:{LABEL};
    }}
    html, body, [data-testid="stAppViewContainer"], .stApp {{
      background:var(--lf-bg) !important; color:var(--lf-text) !important;
    }}
    [data-testid="stHeader"] {{ background:transparent !important; }}
    .block-container {{ max-width:1220px; padding-top:1.5rem; padding-bottom:2.5rem; }}
    [data-testid="stSidebar"] {{
      background:var(--lf-panel) !important;
      border-right:1px solid var(--lf-border);
    }}
    [data-testid="stSidebar"] * {{ color:var(--lf-text); }}
    .lf-brand {{ display:flex; align-items:center; gap:10px; padding:7px 0 20px; }}
    .lf-brand-icon {{
      width:42px; height:42px; display:flex; align-items:center; justify-content:center;
      background:linear-gradient(135deg,#5548ed,#258de8); color:#fff;
      border-radius:13px; font-size:22px;
    }}
    .lf-brand-name {{ font-size:21px; font-weight:800; color:var(--lf-text); }}
    .lf-brand-sub {{ font-size:11px; color:var(--lf-muted); }}
    .lf-hero {{
      border-radius:20px; padding:28px 30px; margin-bottom:22px;
      color:white; background:linear-gradient(110deg,#5146e5 0%,#4964ed 55%,#258be8 100%);
      box-shadow:0 8px 22px rgba(65,82,220,.17);
    }}
    .lf-hero-name {{ font-size:14px; font-weight:750; letter-spacing:.5px; color:#e8eaff; margin-bottom:8px; }}
    .lf-hero h1 {{ color:#fff !important; font-size:clamp(26px,3vw,36px); font-weight:800; margin:0 0 10px; line-height:1.2; }}
    .lf-hero p {{ color:#f1f4ff !important; font-size:15px; line-height:1.65; margin:0; max-width:780px; }}
    .lf-metric {{
      background:var(--lf-panel); border:1px solid var(--lf-border);
      border-radius:15px; padding:17px 19px; min-height:94px;
    }}
    .lf-metric-label {{ color:var(--lf-muted); font-size:12px; margin-bottom:9px; }}
    .lf-metric-value {{ color:var(--lf-text); font-size:26px; font-weight:800; }}
    .lf-heading {{ color:var(--lf-text); font-size:20px; font-weight:800; margin:22px 0 13px; }}
    .lf-result {{
      background:var(--lf-panel); border:1px solid var(--lf-border);
      border-radius:16px; padding:18px 20px; min-height:145px;
      color:var(--lf-text); overflow-wrap:anywhere;
    }}
    .lf-result-label {{ color:var(--lf-muted); font-size:11px; font-weight:750; letter-spacing:1px; margin-bottom:12px; }}
    .lf-result-text {{ color:var(--lf-text); font-size:17px; line-height:1.8; white-space:pre-wrap; }}
    .stApp p, .stApp label, .stApp [data-testid="stWidgetLabel"],
    .stApp [data-testid="stWidgetLabel"] p,
    .stApp [data-testid="stMarkdownContainer"] p,
    .stApp [data-testid="stCaption"] {{ color:var(--lf-text); }}
    .stApp [data-testid="stWidgetLabel"] p, .stApp label {{ color:var(--lf-label) !important; }}
    .stApp input, .stApp textarea {{
      background:var(--lf-field) !important; color:var(--lf-text) !important;
      border-color:var(--lf-border) !important; border-radius:10px !important;
    }}
    .stApp input::placeholder, .stApp textarea::placeholder {{
      color:var(--lf-muted) !important; opacity:1 !important;
    }}
    div[data-baseweb="select"] > div {{
      background:var(--lf-field) !important; border-color:var(--lf-border) !important;
      border-radius:10px !important;
    }}
    div[data-baseweb="select"] *, [data-testid="stSelectbox"] * {{
      color:var(--lf-text) !important;
    }}
    [role="listbox"], [role="option"] {{
      background:var(--lf-panel) !important; color:var(--lf-text) !important;
    }}
    div.stButton > button {{
      background:var(--lf-panel); color:var(--lf-text);
      border:1px solid var(--lf-border); border-radius:10px;
      min-height:41px; font-weight:650;
    }}
    div.stButton > button[kind="primary"] {{
      background:linear-gradient(105deg,#5948ed,#258be8) !important;
      color:#fff !important; border:0 !important;
    }}
    div.stButton > button:hover {{ border-color:#7167ed; }}
    [data-testid="stAlert"] {{ border-radius:11px; }}
    hr {{ border-color:var(--lf-border); }}
    </style>
    """,
    unsafe_allow_html=True,
)


# ---------------- Sidebar navigation ----------------

with st.sidebar:
    st.markdown(
        """
        <div class="lf-brand">
          <div class="lf-brand-icon">🌐</div>
          <div>
            <div class="lf-brand-name">LinguaFlow</div>
            <div class="lf-brand-sub">Language without limits</div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.caption("WORKSPACE")
    for label, page in [
        ("🌐  Translator", "Translator"),
        ("🕘  History", "History"),
        ("⭐  Favorites", "Favorites"),
        ("🗺️  Languages", "Languages"),
        ("⚙️  Settings", "Settings"),
    ]:
        if st.button(
            label, key=f"nav_{page}", use_container_width=True,
            type="primary" if st.session_state.page == page else "secondary",
        ):
            st.session_state.page = page
            st.rerun()

    st.divider()
    st.caption("APPEARANCE")
    st.toggle("Dark mode", key="dark_mode")
    st.markdown(
        '<div style="font-size:12px;color:var(--lf-muted);margin-top:12px;">'
        'Online translation requires an internet connection.</div>',
        unsafe_allow_html=True,
    )


# ---------------- Simple blue banner ----------------

st.markdown(
    """
    <div class="lf-hero">
      <div class="lf-hero-name">LinguaFlow 🌐</div>
      <h1>Every Language. One World.</h1>
      <p>Translate words, share ideas, and connect with people around the world.
      Break language barriers with simple, seamless translations.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

history = st.session_state.data["history"]
favorites = st.session_state.data["favorites"]

col1, col2, col3 = st.columns(3)
with col1:
    st.markdown(
        f'<div class="lf-metric"><div class="lf-metric-label">Translation history</div>'
        f'<div class="lf-metric-value">{len(history)}</div></div>',
        unsafe_allow_html=True,
    )
with col2:
    st.markdown(
        f'<div class="lf-metric"><div class="lf-metric-label">Favorite translations</div>'
        f'<div class="lf-metric-value">{len(favorites)}</div></div>',
        unsafe_allow_html=True,
    )
with col3:
    st.markdown(
        f'<div class="lf-metric"><div class="lf-metric-label">Available languages</div>'
        f'<div class="lf-metric-value">{len(LANGUAGES)}+</div></div>',
        unsafe_allow_html=True,
    )


# =========================================================
# TRANSLATOR PAGE
# =========================================================

if st.session_state.page == "Translator":
    st.markdown('<div class="lf-heading">Translate anything</div>', unsafe_allow_html=True)

    source_col, swap_col, target_col = st.columns([5, 0.8, 5])
    with source_col:
        st.selectbox(
            "Translate from",
            ["Auto-detect"] + list(LANGUAGES.keys()),
            key="source_language",
        )
    with swap_col:
        st.markdown("<div style='height:27px'></div>", unsafe_allow_html=True)
        st.button(
            "⇄", key="swap_button", help="Swap source and target",
            on_click=swap_languages, use_container_width=True,
        )
    with target_col:
        st.selectbox("Translate to", list(LANGUAGES.keys()), key="target_language")

    if st.session_state.swap_message:
        st.info(st.session_state.swap_message)

    original = st.text_area(
        "📝 Original text",
        placeholder="Type or paste the text you want to translate...",
        height=155,
        max_chars=4500,
        key="original_text",
    )
    st.caption(f"{len(original)} / 4,500 characters")

    if st.button("✨  Translate now", type="primary", use_container_width=True):
        st.session_state.result = ""
        st.session_state.last_error = ""
        st.session_state.provider_message = ""
        if not original.strip():
            st.session_state.last_error = "Please enter some text before translating."
        else:
            with st.spinner("Translating your text..."):
                try:
                    translated, provider = translate_text(
                        original,
                        st.session_state.source_language,
                        st.session_state.target_language,
                    )
                    st.session_state.result = translated
                    st.session_state.provider_message = provider
                    entry = {
                        "source": st.session_state.source_language,
                        "target": st.session_state.target_language,
                        "original": original.strip(),
                        "translated": translated,
                        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    }
                    st.session_state.data["history"].insert(0, entry)
                    st.session_state.data["history"] = st.session_state.data["history"][:100]
                    save_data()
                except Exception as exc:
                    st.session_state.last_error = str(exc)

    if st.session_state.last_error:
        st.error(st.session_state.last_error)

    st.markdown('<div class="lf-heading">✨ Translation</div>', unsafe_allow_html=True)
    if st.session_state.result:
        st.markdown(
            f'<div class="lf-result"><div class="lf-result-label">'
            f'{html.escape(st.session_state.target_language.upper())}</div>'
            f'<div class="lf-result-text">{html.escape(st.session_state.result)}</div></div>',
            unsafe_allow_html=True,
        )
        st.caption(st.session_state.provider_message or "Translation complete.")

        copy_col, listen_col, fav_col = st.columns(3)
        with copy_col:
            if st.button("📋 Copy translation", use_container_width=True):
                st.code(st.session_state.result)
                st.info("Select the text above and press Ctrl+C to copy.")
        with listen_col:
            if st.button("🔊 Listen", use_container_width=True):
                components.html(
                    f"""
                    <script>
                    const phrase = {json.dumps(st.session_state.result, ensure_ascii=False)};
                    const language = {json.dumps(LANGUAGES[st.session_state.target_language])};
                    const utterance = new SpeechSynthesisUtterance(phrase);
                    utterance.lang = language;
                    window.speechSynthesis.cancel();
                    window.speechSynthesis.speak(utterance);
                    </script>
                    """,
                    height=0,
                )
                st.caption("Speech playback requested in your browser.")
        with fav_col:
            exists = any(
                item.get("original") == original.strip()
                and item.get("translated") == st.session_state.result
                for item in st.session_state.data["favorites"]
            )
            if st.button(
                "⭐ Added to favorites" if exists else "☆ Add favorite",
                disabled=exists, use_container_width=True,
            ):
                st.session_state.data["favorites"].insert(
                    0,
                    {
                        "source": st.session_state.source_language,
                        "target": st.session_state.target_language,
                        "original": original.strip(),
                        "translated": st.session_state.result,
                        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    },
                )
                save_data()
                st.rerun()
    else:
        st.markdown(
            '<div class="lf-result"><div class="lf-result-label">TRANSLATED TEXT</div>'
            '<div class="lf-result-text" style="color:var(--lf-muted);">'
            'Your translated text will appear here.</div></div>',
            unsafe_allow_html=True,
        )

    st.markdown('<div class="lf-heading">Quick languages</div>', unsafe_allow_html=True)
    quick_cols = st.columns(4)
    for col, language in zip(quick_cols, ["English", "Telugu", "Hindi", "Spanish"]):
        with col:
            st.button(
                f"🌍 {language}", key=f"quick_{language}",
                use_container_width=True,
                on_click=choose_quick_language, args=(language,),
            )


# =========================================================
# HISTORY PAGE
# =========================================================

elif st.session_state.page == "History":
    st.markdown('<div class="lf-heading">🕘 Translation history</div>', unsafe_allow_html=True)
    if st.button("🗑️ Clear history"):
        st.session_state.data["history"] = []
        save_data()
        st.rerun()
    if not history:
        st.info("Your translations will appear here.")
    else:
        for i, item in enumerate(history):
            with st.container(border=True):
                st.caption(f"{item.get('time', '')} · {item.get('source', '')} → {item.get('target', '')}")
                st.markdown(f"**Original:** {item.get('original', '')}")
                st.markdown(f"**Translation:** {item.get('translated', '')}")
                if st.button("⭐ Add to favorites", key=f"history_fav_{i}"):
                    duplicate = any(
                        fav.get("original") == item.get("original")
                        and fav.get("translated") == item.get("translated")
                        for fav in st.session_state.data["favorites"]
                    )
                    if not duplicate:
                        st.session_state.data["favorites"].insert(0, item.copy())
                        save_data()
                    st.rerun()


# =========================================================
# FAVORITES PAGE
# =========================================================

elif st.session_state.page == "Favorites":
    st.markdown('<div class="lf-heading">⭐ Favorite translations</div>', unsafe_allow_html=True)
    if not favorites:
        st.info("Your saved translations will appear here.")
    else:
        for i, item in enumerate(favorites):
            with st.container(border=True):
                st.caption(f"{item.get('source', '')} → {item.get('target', '')}")
                st.markdown(f"**Original:** {item.get('original', '')}")
                st.markdown(f"**Translation:** {item.get('translated', '')}")
                if st.button("Remove favorite", key=f"remove_fav_{i}"):
                    st.session_state.data["favorites"].pop(i)
                    save_data()
                    st.rerun()


# =========================================================
# LANGUAGES PAGE
# =========================================================

elif st.session_state.page == "Languages":
    st.markdown('<div class="lf-heading">🗺️ Available languages</div>', unsafe_allow_html=True)
    st.write(f"Choose from {len(LANGUAGES)} language options.")
    search = st.text_input("🔎 Search languages", placeholder="Type a language name...")
    matches = [(name, code) for name, code in LANGUAGES.items() if search.lower() in name.lower()]
    if not matches:
        st.info("No languages match your search.")
    else:
        cols = st.columns(3)
        for i, (name, code) in enumerate(matches):
            with cols[i % 3]:
                with st.container(border=True):
                    st.markdown(f"**🌐 {name}**")
                    st.caption(f"Language code: {code}")
                    st.button(
                        f"Translate to {name}",
                        key=f"language_pick_{code}",
                        on_click=choose_language_from_list,
                        args=(name,),
                        use_container_width=True,
                    )


# =========================================================
# SETTINGS PAGE
# =========================================================

elif st.session_state.page == "Settings":
    st.markdown('<div class="lf-heading">⚙️ Settings</div>', unsafe_allow_html=True)
    st.write("**Appearance**")
    st.caption("Use the Dark mode switch in the left sidebar to change the theme.")
    st.write(f"Current theme: **{'Dark' if st.session_state.dark_mode else 'Light'}**")
    st.write("**Local data**")
    st.caption("History and favorites are stored in `linguaflow_data.json` beside this app.")
    st.caption("Translation needs an internet connection. Provider availability and limits may vary.")
    if st.button("🗑️ Delete all history and favorites"):
        st.session_state.data = {"history": [], "favorites": []}
        st.session_state.result = ""
        st.session_state.last_error = ""
        save_data()
        st.success("History and favorites cleared.")
        st.rerun()


st.divider()
st.markdown(
    '<div style="text-align:center;color:var(--lf-muted);font-size:12px;padding:8px;">'
    'LinguaFlow · Every Language. One World.</div>',
    unsafe_allow_html=True,
)
