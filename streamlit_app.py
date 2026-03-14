import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# Seiteneinstellungen
st.set_page_config(page_title="Gym Progress Dark", page_icon="💪", layout="centered")

# CSS für PROFESSIONELLEN DARK MODE (Keine Farbüberlagerungen)
st.markdown("""
    <style>
    /* Hintergrund der gesamten App */
    .stApp {
        background-color: #0E1117 !important;
    }

    /* Tab-Design: Klar abgegrenzt */
    button[data-baseweb="tab"] {
        background-color: #1A1C24 !important;
        border: 1px solid #30363D !important;
        margin-right: 8px !important;
        border-radius: 8px 8px 0 0 !important;
        padding: 10px 20px !important;
    }
    button[data-baseweb="tab"] p {
        color: #AEB7C0 !important; /* Hellgrau für inaktive Tabs */
        font-weight: 600 !important;
    }
    button[data-baseweb="tab"][aria-selected="true"] {
        background-color: #FF4B4B !important; /* Akzentfarbe für aktiven Tab */
        border: 1px solid #FF4B4B !important;
    }
    button[data-baseweb="tab"][aria-selected="true"] p {
        color: #FFFFFF !important; /* Reinweiß für aktiven Tab */
        font-weight: 900 !important;
    }

    /* Übungskarten (Metrics): Starker Kontrast zum Hintergrund */
    [data-testid="stMetric"] {
        background-color: #1A1D23 !important;
        border: 1px solid #30363D !important;
        padding: 20px !important;
        border-radius: 12px !important;
        box-shadow: 0px 4px 10px rgba(0,0,0,0.3) !important;
        margin-bottom: 15px !important;
    }
    [data-testid="stMetricLabel"] {
        color: #FFFFFF !important; /* Reinweiß für Übungsnamen */
        font-size: 1.2rem !important;
        font-weight: 700 !important;
    }
    [data-testid="stMetricValue"] {
        color: #FF4B4B !important; /* Rote Akzentfarbe für das Gewicht */
        font-size: 2rem !important;
        font-weight: 900 !important;
    }
    /* Delta-Bereich (Sätze/Wdh) */
    [data-testid="stMetricDelta"] > div {
        color: #00FFC8 !important; /* Cyan für Infos (sehr gut lesbar auf Schwarz) */
        font-weight: 600 !important;
        background-color: rgba(0, 255, 200, 0.1) !important;
        padding: 4px 8px !important;
        border-radius: 6px !important;
    }

    /* Cardio Box */
    .cardio-box {
        background: linear-gradient(90deg, #1A1D23 0%, #0E1117 100%) !important;
        color: #FFFFFF !important;
        border-left: 5px solid #FF4B4B;
        padding: 15px;
        margin: 20px 0;
        border-radius: 4px;
        font-weight: 800;
        text-transform: uppercase;
        letter-spacing: 1px;
    }

    /* Sidebar Fixes */
    .css-1d391kg { background-color: #1A1C24 !important; }
    label { color: #FFFFFF !important; font-weight: 600 !important; }
    </style>
    """, unsafe_allow_html=True)

st.title("🏋️ Gym Plan: Nico & Jessie")

# --- VERBINDUNG ZU GOOGLE SHEETS ---
conn = st.connection("gsheets", type=GSheetsConnection)

# --- PERSONEN SETUP ---
col_n1, col_n2 = st.columns(2)
with col_n1:
    p1 = st.text_input("Person 1", "Nico")
with col_n2:
    p2 = st.text_input("Person 2", "Jessie")

user_choice = st.selectbox("Wer trainiert?", [p1, p2])

@st.cache_data(ttl=2)
def load_data(user):
    try:
        data = conn.read(worksheet=user)
        if not data.empty: return data.iloc[0].to_dict()
    except: return {}
    return {}

saved_values = load_data(user_choice)

# WOCHENAUSWAHL
st.write("### 📅 Woche wählen")
woche = st.radio("Fortschritt:", [1, 2, 3, 4, 5, 6], index=0, horizontal=True)

st.markdown("---")
ok_modus = st.radio("Oberkörper Fokus:", 
                    ["Ausdauer (55%)", "Muskelaufbau (75%+)"], horizontal=True)
is_heavy_ok = "Muskelaufbau" in ok_modus
st.markdown("---")

# --- BASIS DATEN ---
base_keys = ["BS", "HS", "BP", "BSS", "BB", "AD", "SS", "RE", "RB", "BR", "SH", "HSH", "TD", "BC", "HC", "HT", "RDL", "ABD", "KB", "KB45"]
default_names = {"BS": "Beinstrecker", "HS": "Hack Squat", "BP": "Beinpresse", "BSS": "Bulg. Split Squat", "BB": "Beinbeuger", "AD": "Adduktoren", "SS": "Sissy Squat", "RE": "Rudern Eng", "RB": "Rudern Breit", "BR": "Brustpresse", "SH": "Seitheben", "HSH": "Hint. Schulter", "TD": "Trizepsdrücken", "BC": "Incline Bizeps", "HC": "Hammer Curls", "HT": "Hipthrusts", "RDL": "RDL", "ABD": "Abduktoren", "KB": "Kickbacks", "KB45": "Kickbacks 45°"}

# --- SIDEBAR ---
st.sidebar.header("⚙️ Verwaltung")
with st.sidebar.expander("Kürzel-Liste"):
    st.table(pd.DataFrame([{"ID": k, "Übung": default_names[k]} for k in base_keys]))

def get_order(key, default):
    raw = saved_values.get(key, default)
    return [k.strip() for k in raw.split(",") if k.strip() in base_keys]

order_beine = st.sidebar.multiselect("Reihenfolge Beine", options=base_keys, default=get_order("ORDER_BEINE", "BS,HS,BP,BSS,BB,AD,SS"))
order_ok = st.sidebar.multiselect("Reihenfolge OK", options=base_keys, default=get_order("ORDER_OK", "RE,RB,BR,SH,HSH,TD,BC,HC"))
order_po = st.sidebar.multiselect("Reihenfolge Po", options=base_keys, default=get_order("ORDER_PO", "HT,RDL,ABD,KB,KB45"))

name_map = {k: st.sidebar.text_input(f"Name {k}", saved_values.get(f"NAME_{k}", default_names[k])) for k in base_keys}

extra_exercises = {}
for i in range(1, 6):
    ex_n = st.sidebar.text_input(f"Zusatz #{i} Name", saved_values.get(f"EX_N_{i}", ""))
    ex_d = st.sidebar.selectbox(f"Zusatz #{i} Tag", ["Keiner", "Mo: Beine", "Di: OK", "Mi: PO", "Do: OK", "Fr: Beine"], key=f"d_{i}")
    if ex_n: extra_exercises[f"EXTRA_{i}"] = {"name": ex_n, "day": ex_d}

rms = {k: st.sidebar.number_input(f"1RM {name_map[k]}", value=float(saved_values.get(k, 50.0)), step=2.5) for k in base_keys}
for k, info in extra_exercises.items():
    rms[k] = st.sidebar.number_input(f"1RM {info['name']}", value=float(saved_values.get(k, 50.0)), step=2.5)

if st.sidebar.button("💾 SPEICHERN & SYNCHRONISIEREN"):
    data = {**rms, **{f"NAME_{k}": v for k, v in name_map.items()}, "ORDER_BEINE": ",".join(order_beine), "ORDER_OK": ",".join(order_ok), "ORDER_PO": ",".join(order_po)}
    for i in range(1, 6):
        key = f"EXTRA_{i}"
        data[f"EX_N_{i}"] = extra_exercises[key]["name"] if key in extra_exercises else ""
        data[f"EX_D_{i}"] = extra_exercises[key]["day"] if key in extra_exercises else "Keiner"
    conn.update(worksheet=user_choice, data=pd.DataFrame([data]))
    st.sidebar.success("Daten erfolgreich in Cloud gespeichert!")
    st.cache_data.clear()

# --- RENDERING ---
def display_day(day_label, keys, is_heavy):
    st.markdown(f'<div class="cardio-box">🏃 CARDIO: 30 MIN (WAHLWEISE)</div>', unsafe_allow_html=True)
    wdh = "8-12 Wdh" if (is_heavy or is_heavy_ok) else "15-20 Wdh"
    sets = "3-4 Sätze" if is_heavy else "3 Sätze"
    for k in keys:
        if k in name_map:
            weight = round(rms[k] * ((0.75 + (0.05 * (woche - 1))) if (is_heavy or is_heavy_ok) else 0.55), 1)
            st.metric(label=name_map[k], value=f"{weight} kg", delta=f"{sets} | {wdh} | {k}")
    for k, info in extra_exercises.items():
        if info["day"] == day_label:
            w_extra = round(rms[k] * (0.75 + (0.05 * (woche - 1))), 1)
            st.metric(label=info["name"], value=f"{w_extra} kg", delta="3 Sätze | 10-15 Wdh")

tabs = st.tabs(["Mo: Beine", "Di: OK", "Mi: PO", "Do: OK", "Fr: Beine"])
with tabs[0]: display_day("Mo: Beine", order_beine, True)
with tabs[1]: display_day("Di: OK", order_ok, False)
with tabs[2]: display_day("Mi: PO", order_po, True)
with tabs[3]: display_day("Do: OK", order_ok, False)
with tabs[4]: display_day("Fr: Beine", order_beine, True)
