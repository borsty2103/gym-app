import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
from datetime import datetime

# Seiteneinstellungen
st.set_page_config(page_title="Gym Progress Dark", page_icon="💪", layout="centered")

# CSS für PROFESSIONELLEN DARK MODE & PAUSEN-STYLING
st.markdown("""
    <style>
    .stApp { background-color: #0E1117 !important; }
    [data-testid="stMetric"] {
        background-color: #1A1D23 !important;
        border: 1px solid #30363D !important;
        padding: 20px !important;
        border-radius: 12px !important;
        margin-bottom: 0px !important;
    }
    .cardio-box {
        background-color: #000000 !important;
        color: #FFFFFF !important;
        border-left: 5px solid #FF4B4B;
        padding: 15px;
        margin: 20px 0;
        font-weight: 800;
        text-transform: uppercase;
        border: 1px solid #30363D;
    }
    .pause-text {
        color: #FF4B4B;
        font-size: 0.9rem;
        font-weight: 600;
        margin-top: 5px;
        margin-bottom: 20px;
        padding-left: 5px;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🏋️ Gym Plan: Nico & Jessie")

# --- VERBINDUNG ---
conn = st.connection("gsheets", type=GSheetsConnection)

# --- PERSONEN ---
col_n1, col_n2 = st.columns(2)
with col_n1: p1 = st.text_input("Person 1", "Nico")
with col_n2: p2 = st.text_input("Person 2", "Jessie")

user_choice = st.selectbox("Wer trainiert gerade?", [p1, p2])

@st.cache_data(ttl=2)
def load_data(user):
    try:
        data = conn.read(worksheet=user)
        if not data.empty: return data.iloc[-1].to_dict()
    except: return {}
    return {}

saved_values = load_data(user_choice)

# --- BASIS EINSTELLUNGEN ---
st.write("### 📅 Trainingseinstellungen")
woche = st.radio("Woche wählen:", [1, 2, 3, 4, 5, 6], index=0, horizontal=True)
ok_modus = st.radio("Oberkörper Fokus:", ["Ausdauer (55% | 15-20 Wdh)", "Muskelaufbau (75% | 8-12 Wdh)"], horizontal=True)
is_heavy_ok = "Muskelaufbau" in ok_modus

# --- ÜBUNGS-DEFINITIONEN ---
base_keys = ["BS", "HS", "BP", "BSS", "BB", "AD", "SS", "RE", "RB", "BR", "SH", "HSH", "TD", "BC", "HC", "HT", "RDL", "ABD", "KB", "KB45"]
default_names = {"BS": "Beinstrecker", "HS": "Hack Squat", "BP": "Beinpresse", "BSS": "Bulg. Split Squat", "BB": "Beinbeuger", "AD": "Adduktoren", "SS": "Sissy Squat", "RE": "Rudern Eng", "RB": "Rudern Breit", "BR": "Brustpresse", "SH": "Seitheben", "HSH": "Hint. Schulter", "TD": "Trizepsdrücken", "BC": "Bizeps Curls", "HC": "Hammer Curls", "HT": "Hip Thrust", "RDL": "RDL", "ABD": "Abduktoren", "KB": "Kickbacks", "KB45": "Kickbacks 45°"}

# --- SIDEBAR (GEWICHTE) ---
st.sidebar.header("⚙️ 1RM Gewichte")
name_map = {k: st.sidebar.text_input(f"Name {k}", saved_values.get(f"NAME_{k}", default_names[k])) for k in base_keys}
rms = {k: st.sidebar.number_input(f"1RM {name_map[k]} (kg)", value=float(saved_values.get(k, 50.0)), step=2.5) for k in base_keys}

# --- SPEICHER-LOGIK ---
if st.sidebar.button("💾 ALLES SPEICHERN"):
    new_entry = {"Datum": datetime.now().strftime("%d.%m.%Y"), "Woche": woche, "Modus": ok_modus}
    for k in base_keys:
        new_entry[k] = rms[k]
        new_entry[f"NAME_{k}"] = name_map[k]
    try:
        try: df_existing = conn.read(worksheet=user_choice)
        except: df_existing = pd.DataFrame()
        df_new_row = pd.DataFrame([new_entry])
        if df_existing.empty: 
            df_final = df_new_row
        else:
            for col in df_new_row.columns:
                if col not in df_existing.columns: df_existing[col] = None
            df_final = pd.concat([df_existing, df_new_row], ignore_index=True)
        conn.update(worksheet=user_choice, data=df_final)
        st.sidebar.success("✅ Erfogreich im Sheet gespeichert!")
        st.cache_data.clear()
        st.rerun()
    except Exception as e:
        st.sidebar.error(f"Fehler: {e}")

# --- ANZEIGE FUNKTION (MIT SÄTZEN & PAUSEN) ---
def display_day(keys, is_heavy_day):
    st.markdown('<div class="cardio-box">🏃 CARDIO: 30 MIN</div>', unsafe_allow_html=True)
    
    # Bestimmung von Sätzen, Wdh und Pausen
    wdh = "8-12 Wdh" if (is_heavy_day or is_heavy_ok) else "15-20 Wdh"
    sets = "3-4 Sätze" if is_heavy_day else "3 Sätze"
    pause = "120s Pause" if is_heavy_day else "90s Pause"
    
    for k in keys:
        factor = (0.75 + (0.05 * (woche - 1))) if (is_heavy_day or is_heavy_ok) else 0.55
        weight = round(rms[k] * factor, 1)
        
        # Metric Block
        st.metric(label=name_map[k], value=f"{weight} kg", delta=f"{sets} | {wdh}")
        # Pausen-Zeile direkt darunter
        st.markdown(f'<div class="pause-text">⏱️ {pause} | Code: {k}</div>', unsafe_allow_html=True)

# --- TABS ---
tabs = st.tabs(["Mo: Beine", "Di: OK", "Mi: PO", "Do: OK", "Fr: Beine"])
with tabs[0]: display_day(["BS", "HS", "BP", "BSS", "BB", "AD", "SS"], True)
with tabs[1]: display_day(["RE", "RB", "BR", "SH", "HSH", "TD", "BC", "HC"], False)
with tabs[2]: display_day(["HT", "RDL", "ABD", "KB", "KB45"], True)
with tabs[3]: display_day(["RE", "RB", "BR", "SH", "HSH", "TD", "BC", "HC"], False)
with tabs[4]: display_day(["BS", "HS", "BP", "BSS", "BB", "AD", "SS"], True)
