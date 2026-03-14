import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# Seiteneinstellungen
st.set_page_config(page_title="Gym Progress Ultimate", page_icon="💪", layout="centered")

# CSS für MAXIMALEN Kontrast und mobile Bedienbarkeit (Kein Grün-auf-Grün)
st.markdown("""
    <style>
    /* Hintergrund der Karten auf Reinweiß und harter schwarzer Rahmen */
    [data-testid="stMetric"] {
        background-color: #ffffff !important;
        border: 2px solid #000000 !important;
        padding: 15px !important;
        border-radius: 10px !important;
        box-shadow: 4px 4px 0px #000000 !important;
        margin-bottom: 12px !important;
    }
    /* Texte in den Karten auf Tiefschwarz */
    [data-testid="stMetricLabel"] {
        color: #000000 !important;
        font-size: 1.2rem !important;
        font-weight: 800 !important;
    }
    [data-testid="stMetricValue"] {
        color: #000000 !important;
        font-size: 1.8rem !important;
        font-weight: 900 !important;
    }
    /* Delta Bereich (Wiederholungen & Sätze) auf Schwarz erzwingen */
    [data-testid="stMetricDelta"] > div {
        color: #000000 !important;
        font-weight: bold !important;
        opacity: 1 !important;
        font-size: 1rem !important;
    }
    /* Cardio Box */
    .cardio-box {
        background-color: #000000;
        color: #ffffff;
        padding: 18px;
        margin: 15px 0;
        border-radius: 8px;
        font-weight: bold;
        text-align: center;
        font-size: 1.2rem;
        border: 2px solid #444444;
    }
    /* Tabs für mobile Geräte optimieren */
    .stTabs [data-baseweb="tab"] {
        font-size: 16px;
        font-weight: 900;
        padding: 12px 8px !important;
        color: #000000 !important;
    }
    /* Radio Buttons (Wochenauswahl) fetten */
    div[data-testid="stMarkdownContainer"] > p {
        font-weight: bold;
        font-size: 1.1rem;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🏋️ Gym Plan: Nico & Jessi")

# --- VERBINDUNG ZU GOOGLE SHEETS ---
conn = st.connection("gsheets", type=GSheetsConnection)

# --- PERSONEN SETUP ---
col_n1, col_n2 = st.columns(2)
with col_n1:
    p1 = st.text_input("Name Person 1", "Nico")
with col_n2:
    p2 = st.text_input("Name Person 2", "Jessi")

user_choice = st.selectbox("Wer trainiert gerade?", [p1, p2])

# AUTOMATISCHES LADEN AUS DER CLOUD
@st.cache_data(ttl=2)
def load_data(user):
    try:
        data = conn.read(worksheet=user)
        if not data.empty:
            return data.iloc[0].to_dict()
    except:
        return {}
    return {}

saved_values = load_data(user_choice)

# MOBIL-OPTIMIERTE WOCHENAUSWAHL (Radio-Buttons statt Slider)
st.write("### 📅 Aktuelle Trainingswoche")
woche = st.radio("Woche wählen (Gewicht passt sich an):", 
                 options=[1, 2, 3, 4, 5, 6], 
                 index=0, 
                 horizontal=True)

st.markdown("---")
ok_modus = st.radio("Modus Oberkörper (Di/Do):", 
                    ["Ausdauer (55% | 15-20 Wdh)", "Muskelaufbau (75% | 8-12 Wdh)"], 
                    horizontal=True)
is_heavy_ok = "Muskelaufbau" in ok_modus
st.markdown("---")

# --- BASIS DATEN DEFINITION ---
base_keys = ["BS", "HS", "BP", "BSS", "BB", "AD", "SS", "RE", "RB", "BR", "SH", "HSH", "TD", "BC", "HC", "HT", "RDL", "ABD", "KB", "KB45"]
default_names = {
    "BS": "Beinstrecker", "HS": "Hack Squat", "BP": "Beinpresse", "BSS": "Bulg. Split Squat",
    "BB": "Beinbeuger", "AD": "Adduktoren", "SS": "Sissy Squat", "RE": "Rudern Eng",
    "RB": "Rudern Breit", "BR": "Brustpresse", "SH": "Seitheben", "HSH": "Hint. Schulter",
    "TD": "Trizepsdrücken", "BC": "Incline Bizeps", "HC": "Hammer Curls", "HT": "Hipthrusts",
    "RDL": "RDL", "ABD": "Abduktoren", "KB": "Kickbacks", "KB45": "Kickbacks 45°"
}

# --- SIDEBAR: KÜRZEL-LEXIKON ---
st.sidebar.header("📖 Kürzel-Lexikon")
with st.sidebar.expander("Abkürzungen anzeigen"):
    lexikon_data = [{"Kürzel": k, "Übung": default_names[k]} for k in base_keys]
    st.table(pd.DataFrame(lexikon_data))

# --- SIDEBAR: SORTIERUNG (MULTISELECT) ---
st.sidebar.header("🔄 Reihenfolge")
with st.sidebar.expander("Anordnung der Übungen"):
    def get_order(key, default):
        raw = saved_values.get(key, default)
        return [k.strip() for k in raw.split(",") if k.strip() in base_keys]

    order_beine = st.multiselect("Reihenfolge Beine (Mo/Fr)", options=base_keys, default=get_order("ORDER_BEINE", "BS,HS,BP,BSS,BB,AD,SS"))
    order_ok = st.multiselect("Reihenfolge OK (Di/Do)", options=base_keys, default=get_order("ORDER_OK", "RE,RB,BR,SH,HSH,TD,BC,HC"))
    order_po = st.multiselect("Reihenfolge Po (Mi)", options=base_keys, default=get_order("ORDER_PO", "HT,RDL,ABD,KB,KB45"))

# --- SIDEBAR: NAMEN & ZUSATZ ---
with st.sidebar.expander("📝 Namen ändern"):
    name_map = {k: st.text_input(f"Name für {k}", saved_values.get(f"NAME_{k}", default_names[k]), key=f"edit_{k}") for k in base_keys}

st.sidebar.subheader("➕ Zusatzübungen")
extra_exercises = {}
for i in range(1, 6):
    with st.sidebar.expander(f"Zusatz Übung {i}"):
        ex_n = st.text_input(f"Name #{i}", saved_values.get(f"EX_N_{i}", ""), key=f"ex_n_{i}")
        ex_d = st.selectbox(f"Tag #{i}", ["Keiner", "Mo: Beine", "Di: OK", "Mi: PO", "Do: OK", "Fr: Beine"], 
                            index=["Keiner", "Mo: Beine", "Di: OK", "Mi: PO", "Do: OK", "Fr: Beine"].index(saved_values.get(f"EX_D_{i}", "Keiner")), key=f"ex_d_{i}")
        if ex_n and ex_d != "Keiner":
            extra_exercises[f"EXTRA_{i}"] = {"name": ex_n, "day": ex_d}

# --- SIDEBAR: 1RM SETUP ---
st.sidebar.header(f"⚙️ 1RM Gewichte")
rms = {k: st.sidebar.number_input(f"1RM {name_map[k]} (kg)", value=float(saved_values.get(k, 50.0)), step=2.5, key=f"rm_{k}") for k in base_keys}
for k, info in extra_exercises.items():
    rms[k] = st.sidebar.number_input(f"1RM {info['name']} (kg)", value=float(saved_values.get(k, 50.0)), step=2.5, key=f"rm_{k}")

# --- SPEICHERN ---
if st.sidebar.button("💾 ALLES SPEICHERN"):
    data_to_save = {**rms, **{f"NAME_{k}": v for k, v in name_map.items()}, "ORDER_BEINE": ",".join(order_beine), "ORDER_OK": ",".join(order_ok), "ORDER_PO": ",".join(order_po)}
    for i in range(1, 6):
        key = f"EXTRA_{i}"
        data_to_save[f"EX_N_{i}"] = extra_exercises[key]["name"] if key in extra_exercises else ""
        data_to_save[f"EX_D_{i}"] = extra_exercises[key]["day"] if key in extra_exercises else "Keiner"
    conn.update(worksheet=user_choice, data=pd.DataFrame([data_to_save]))
    st.sidebar.success("Erfolgreich in Cloud gespeichert!")
    st.cache_data.clear()

# --- BERECHNUNGSLOGIK ---
def calculate_weight(val, is_heavy_day):
    factor = (0.75 + (0.05 * (woche - 1))) if (is_heavy_day or is_heavy_ok) else 0.55
    return round(val * factor, 1)

# --- ANZEIGEFUNKTION FÜR TRAININGSTAGE ---
def display_day(day_label, keys, is_heavy_training):
    st.markdown('<div class="cardio-box">🏃 CARDIO: 30 MIN (STAIRMASTER / WAHLWEISE)</div>', unsafe_allow_html=True)
    
    # Wiederholungs-Text basierend auf Modus
    wdh_text = "8-12 Wdh" if (is_heavy_training or is_heavy_ok) else "15-20 Wdh"
    satze = "3-4 Sätze" if is_heavy_training else "3 Sätze"

    for k in keys:
        if k in name_map:
            st.metric(
                label=f"{name_map[k]}", 
                value=f"{calculate_weight(rms[k], is_heavy_training)} kg", 
                delta=f"{satze} | {wdh_text} | Kürzel: {k}"
            )
    
    # Zusatzübungen
    for k, info in extra_exercises.items():
        if info["day"] == day_label:
            st.metric(
                label=info["name"], 
                value=f"{calculate_weight(rms[k], True)} kg", 
                delta="Zusatzübung | 3 Sätze | 10-15 Wdh"
            )

# --- HAUPTANSICHT: TABS ---
tabs = st.tabs(["📅 Mo: Beine", "📅 Di: OK", "📅 Mi: PO", "📅 Do: OK", "📅 Fr: Beine"])

with tabs[0]: # Montag
    display_day("Mo: Beine", order_beine, True)

with tabs[1]: # Dienstag
    display_day("Di: OK", order_ok, False)

with tabs[2]: # Mittwoch
    display_day("Mi: PO", order_po, True)

with tabs[3]: # Donnerstag
    display_day("Do: OK", order_ok, False)

with tabs[4]: # Freitag
    display_day("Fr: Beine", order_beine, True)
