import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# Seiteneinstellungen
st.set_page_config(page_title="Gym Progress Ultimate", page_icon="💪", layout="centered")

# CSS für MAXIMALEN Kontrast (Schwarz/Weiß Fokus) - Verhindert Grün-auf-Grün
st.markdown("""
    <style>
    /* Hintergrund der Karten auf Reinweiß und harter schwarzer Rahmen */
    [data-testid="stMetric"] {
        background-color: #ffffff !important;
        border: 2px solid #000000 !important;
        padding: 15px !important;
        border-radius: 10px !important;
        box-shadow: 4px 4px 0px #000000 !important;
    }
    /* Alle Texte und Werte in den Karten auf Tiefschwarz */
    [data-testid="stMetricLabel"] {
        color: #000000 !important;
        font-size: 1.1rem !important;
        font-weight: 800 !important;
    }
    [data-testid="stMetricValue"] {
        color: #000000 !important;
        font-size: 1.8rem !important;
        font-weight: 900 !important;
    }
    /* Delta-Bereich (Untertitel) auf Schwarz erzwingen */
    [data-testid="stMetricDelta"] > div {
        color: #000000 !important;
        font-weight: bold !important;
        opacity: 1 !important;
    }
    /* Cardio Box im Invers-Design */
    .cardio-box {
        background-color: #000000;
        color: #ffffff;
        padding: 15px;
        margin: 15px 0;
        border-radius: 8px;
        font-weight: bold;
        text-align: center;
        font-size: 1.2rem;
    }
    .stTabs [data-baseweb="tab"] {
        font-size: 20px;
        font-weight: 900;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🏋️ Trainingsplan: Nico & Jessi")

# --- VERBINDUNG ---
conn = st.connection("gsheets", type=GSheetsConnection)

# --- SETUP ---
col_n1, col_n2 = st.columns(2)
with col_n1:
    p1 = st.text_input("Name Person 1", "Nico")
with col_n2:
    p2 = st.text_input("Name Person 2", "Jessi")

user_choice = st.selectbox("Wer trainiert gerade?", [p1, p2])

@st.cache_data(ttl=2)
def load_data(user):
    try:
        data = conn.read(worksheet=user)
        if not data.empty: return data.iloc[0].to_dict()
    except: return {}
    return {}

saved_values = load_data(user_choice)
woche = st.select_slider("Trainingswoche", options=range(1, 7))

st.markdown("---")
ok_modus = st.radio("Modus für Oberkörper-Tage (Di/Do):", 
                    ["Ausdauer (55% Gewicht)", "Muskelaufbau (75%+ Gewicht)"], horizontal=True)
is_heavy_ok = "Muskelaufbau" in ok_modus
st.markdown("---")

# --- SIDEBAR: REIHENFOLGE & ÜBUNGEN ---
st.sidebar.header("🛠️ Management & Reihenfolge")

# 1. Reihenfolge ändern (Verschiebbar via Text-Input)
with st.sidebar.expander("🔄 Reihenfolge der Übungen ändern"):
    st.write("Kürzel sortieren (getrennt durch Komma):")
    # Wir speichern die Reihenfolge als kommagetrennte Liste im Sheet
    order_beine = st.text_input("Sortierung Beine (Mo/Fr)", saved_values.get("ORDER_BEINE", "BS,HS,BP,BSS,BB,AD,SS"))
    order_ok = st.text_input("Sortierung OK (Di/Do)", saved_values.get("ORDER_OK", "RE,RB,BR,SH,HSH,TD,BC,HC"))
    order_po = st.text_input("Sortierung Po (Mi)", saved_values.get("ORDER_PO", "HT,RDL,ABD,KB,KB45"))

# 2. Namen der Basisübungen
with st.sidebar.expander("📝 Namen der Übungen anpassen"):
    base_keys = ["BS", "HS", "BP", "BSS", "BB", "AD", "SS", "RE", "RB", "BR", "SH", "HSH", "TD", "BC", "HC", "HT", "RDL", "ABD", "KB", "KB45"]
    default_names = {
        "BS": "Beinstrecker", "HS": "Hack Squat", "BP": "Beinpresse", "BSS": "Bulg. Split Squat",
        "BB": "Beinbeuger", "AD": "Adduktoren", "SS": "Sissy Squat", "RE": "Rudern Eng",
        "RB": "Rudern Breit", "BR": "Brustpresse", "SH": "Seitheben", "HSH": "Hint. Schulter",
        "TD": "Trizepsdrücken", "BC": "Incline Bizeps", "HC": "Hammer Curls", "HT": "Hipthrusts",
        "RDL": "RDL", "ABD": "Abduktoren", "KB": "Kickbacks", "KB45": "Kickbacks 45°"
    }
    name_map = {k: st.text_input(f"Name für {k}", saved_values.get(f"NAME_{k}", default_names[k]), key=f"edit_{k}") for k in base_keys}

# 3. Extra Übungen hinzufügen
st.sidebar.markdown("---")
st.sidebar.subheader("➕ Zusatzübungen")
extra_exercises = {}
for i in range(1, 6):
    with st.sidebar.expander(f"Extra Übung {i}"):
        ex_n = st.text_input(f"Name Extra {i}", saved_values.get(f"EX_N_{i}", ""), key=f"ex_n_{i}")
        ex_d = st.selectbox(f"Tag Extra {i}", ["Keiner", "Mo: Beine", "Di: OK", "Mi: PO", "Do: OK", "Fr: Beine"], 
                            index=["Keiner", "Mo: Beine", "Di: OK", "Mi: PO", "Do: OK", "Fr: Beine"].index(saved_values.get(f"EX_D_{i}", "Keiner")), key=f"ex_d_{i}")
        if ex_n and ex_d != "Keiner":
            extra_exercises[f"EXTRA_{i}"] = {"name": ex_n, "day": ex_d}

# --- 1RM GEWICHTE (SIDEBAR) ---
st.sidebar.header(f"⚙️ 1RM Setup")
rms = {k: st.sidebar.number_input(f"1RM {name_map[k]} (kg)", value=float(saved_values.get(k, 50.0)), step=2.5, key=f"rm_{k}") for k in base_keys}
for k, info in extra_exercises.items():
    rms[k] = st.sidebar.number_input(f"1RM {info['name']} (kg)", value=float(saved_values.get(k, 50.0)), step=2.5, key=f"rm_{k}")

# --- SPEICHER-BUTTON ---
if st.sidebar.button("💾 ALLES IN CLOUD SPEICHERN"):
    data = rms.copy()
    # Namen & Reihenfolgen hinzufügen
    for k, v in name_map.items(): data[f"NAME_{k}"] = v
    data["ORDER_BEINE"] = order_beine
    data["ORDER_OK"] = order_ok
    data["ORDER_PO"] = order_po
    # Extras hinzufügen
    for i in range(1, 6):
        key = f"EXTRA_{i}"
        data[f"EX_N_{i}"] = extra_exercises[key]["name"] if key in extra_exercises else ""
        data[f"EX_D_{i}"] = extra_exercises[key]["day"] if key in extra_exercises else "Keiner"
    
    conn.update(worksheet=user_choice, data=pd.DataFrame([data]))
    st.sidebar.success("Cloud-Update erfolgreich!")
    st.cache_data.clear()

# --- RECHEN-LOGIK ---
def calc(val, heavy_day=False):
    f = (0.75 + (0.05 * (woche - 1))) if (heavy_day or is_heavy_ok) else 0.55
    return round(val * f, 1)

# --- RENDERING FUNKTION FÜR DIE TAGE ---
def render_exercises(keys_string, is_heavy, day_label):
    st.markdown('<div class="cardio-box">🏃 CARDIO: 30 MIN STAIRMASTER / WAHLWEISE</div>', unsafe_allow_html=True)
    # String in Liste umwandeln und leere Stellen entfernen
    ordered_keys = [k.strip() for k in keys_string.split(",") if k.strip() in name_map]
    
    # Basisübungen in der gewählten Reihenfolge
    for k in ordered_keys:
        st.metric(name_map[k], f"{calc(rms[k], is_heavy)} kg", "3-4 Sätze | 8-15 Wdh")
    
    # Extra Übungen für diesen Tag
    for k, info in extra_exercises.items():
        if info["day"] == day_label:
            st.metric(info["name"], f"{calc(rms[k], True)} kg", "Zusatzübung | 3 Sätze")

# --- TABS ---
tabs = st.tabs(["Mo: Beine", "Di: OK", "Mi: PO", "Do: OK", "Fr: Beine"])

with tabs[0]: # Montag
    render_exercises(order_beine, True, "Mo: Beine")

with tabs[1]: # Dienstag
    render_exercises(order_ok, False, "Di: OK")

with tabs[2]: # Mittwoch
    render_exercises(order_po, True, "Mi: PO")

with tabs[3]: # Donnerstag
    render_exercises(order_ok, False, "Do: OK")

with tabs[4]: # Freitag
    render_exercises(order_beine, True, "Fr: Beine")
