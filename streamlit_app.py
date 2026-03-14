import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# Seiteneinstellungen
st.set_page_config(page_title="Gym Progress Ultimate", page_icon="💪", layout="centered")

# CSS für MAXIMALEN Kontrast - Erzwingt helle Lesbarkeit auch im Dark Mode
st.markdown("""
    <style>
    /* Globaler Hintergrund-Fix für die App-Container */
    .stApp {
        background-color: #ffffff !important;
    }

    /* Tab-Überschriften (Das Hauptproblem im Screenshot) */
    button[data-baseweb="tab"] {
        background-color: #f0f2f6 !important;
        border: 1px solid #000000 !important;
        margin-right: 5px !important;
        border-radius: 5px 5px 0 0 !important;
    }
    button[data-baseweb="tab"] p {
        color: #000000 !important; /* Erzwingt schwarze Schrift auf den Tabs */
        font-weight: 900 !important;
        font-size: 14px !important;
    }
    button[data-baseweb="tab"][aria-selected="true"] {
        background-color: #000000 !important;
    }
    button[data-baseweb="tab"][aria-selected="true"] p {
        color: #ffffff !important; /* Weißer Text auf schwarzem aktiven Tab */
    }

    /* Übungskarten (Metrics) */
    [data-testid="stMetric"] {
        background-color: #ffffff !important;
        border: 3px solid #000000 !important;
        padding: 15px !important;
        border-radius: 10px !important;
        box-shadow: 5px 5px 0px #000000 !important;
        margin-bottom: 15px !important;
    }
    [data-testid="stMetricLabel"], [data-testid="stMetricValue"] {
        color: #000000 !important;
    }
    [data-testid="stMetricDelta"] > div {
        color: #000000 !important;
        font-weight: bold !important;
        background-color: #eeeeee !important;
        padding: 2px 5px !important;
        border-radius: 5px !important;
    }

    /* Cardio Box */
    .cardio-box {
        background-color: #000000 !important;
        color: #ffffff !important;
        padding: 20px;
        margin: 10px 0 20px 0;
        border-radius: 10px;
        font-weight: 800;
        text-align: center;
        font-size: 1.2rem;
        text-transform: uppercase;
    }

    /* Input Felder Lesbarkeit */
    label, p, .stMarkdown {
        color: #000000 !important;
        font-weight: 600 !important;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🏋️ Gym Plan: Nico & Jessi")

# --- VERBINDUNG ZU GOOGLE SHEETS ---
conn = st.connection("gsheets", type=GSheetsConnection)

# --- PERSONEN SETUP ---
col_n1, col_n2 = st.columns(2)
with col_n1:
    p1 = st.text_input("Person 1", "Nico")
with col_n2:
    p2 = st.text_input("Person 2", "Jessi")

user_choice = st.selectbox("Wer trainiert?", [p1, p2])

@st.cache_data(ttl=2)
def load_data(user):
    try:
        data = conn.read(worksheet=user)
        if not data.empty: return data.iloc[0].to_dict()
    except: return {}
    return {}

saved_values = load_data(user_choice)

# WOCHENAUSWAHL (Mobil-optimiert)
st.write("### 📅 Woche wählen")
woche = st.radio("Steigerung:", [1, 2, 3, 4, 5, 6], index=0, horizontal=True)

st.markdown("---")
ok_modus = st.radio("Oberkörper Modus:", 
                    ["Ausdauer (55% | 15-20 Wdh)", "Muskelaufbau (75% | 8-12 Wdh)"], horizontal=True)
is_heavy_ok = "Muskelaufbau" in ok_modus
st.markdown("---")

# --- BASIS DATEN ---
base_keys = ["BS", "HS", "BP", "BSS", "BB", "AD", "SS", "RE", "RB", "BR", "SH", "HSH", "TD", "BC", "HC", "HT", "RDL", "ABD", "KB", "KB45"]
default_names = {"BS": "Beinstrecker", "HS": "Hack Squat", "BP": "Beinpresse", "BSS": "Bulg. Split Squat", "BB": "Beinbeuger", "AD": "Adduktoren", "SS": "Sissy Squat", "RE": "Rudern Eng", "RB": "Rudern Breit", "BR": "Brustpresse", "SH": "Seitheben", "HSH": "Hint. Schulter", "TD": "Trizepsdrücken", "BC": "Incline Bizeps", "HC": "Hammer Curls", "HT": "Hipthrusts", "RDL": "RDL", "ABD": "Abduktoren", "KB": "Kickbacks", "KB45": "Kickbacks 45°"}

# --- SIDEBAR MANAGEMENT ---
st.sidebar.header("⚙️ Einstellungen")
with st.sidebar.expander("Abkürzungen"):
    st.table(pd.DataFrame([{"Kürzel": k, "Übung": default_names[k]} for k in base_keys]))

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
    ex_d = st.sidebar.selectbox(f"Zusatz #{i} Tag", ["Keiner", "Mo: Beine", "Di: OK", "Mi: PO", "Do: OK", "Fr: Beine"], index=0)
    if ex_n: extra_exercises[f"EXTRA_{i}"] = {"name": ex_n, "day": ex_d}

rms = {k: st.sidebar.number_input(f"1RM {name_map[k]}", value=float(saved_values.get(k, 50.0)), step=2.5) for k in base_keys}
for k, info in extra_exercises.items():
    rms[k] = st.sidebar.number_input(f"1RM {info['name']}", value=float(saved_values.get(k, 50.0)), step=2.5)

if st.sidebar.button("💾 SPEICHERN"):
    data = {**rms, **{f"NAME_{k}": v for k, v in name_map.items()}, "ORDER_BEINE": ",".join(order_beine), "ORDER_OK": ",".join(order_ok), "ORDER_PO": ",".join(order_po)}
    for i in range(1, 6):
        key = f"EXTRA_{i}"
        data[f"EX_N_{i}"] = extra_exercises[key]["name"] if key in extra_exercises else ""
        data[f"EX_D_{i}"] = extra_exercises[key]["day"] if key in extra_exercises else "Keiner"
    conn.update(worksheet=user_choice, data=pd.DataFrame([data]))
    st.sidebar.success("Cloud-Sync OK!")
    st.cache_data.clear()

# --- ANZEIGE ---
def display_day(day_label, keys, is_heavy):
    st.markdown('<div class="cardio-box">🏃 CARDIO: 30 MIN</div>', unsafe_allow_html=True)
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
