import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# Seiteneinstellungen
st.set_page_config(page_title="Gym Progress Ultimate", page_icon="💪", layout="centered")

# CSS für MAXIMALEN Kontrast (Schwarz auf Weiß) - Optimiert für helle Gym-Umgebungen
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
    /* Alle Texte und Werte in den Karten auf Tiefschwarz erzwingen */
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
    /* Untertitel/Delta Bereich auf Schwarz */
    [data-testid="stMetricDelta"] > div {
        color: #000000 !important;
        font-weight: bold !important;
        opacity: 1 !important;
    }
    /* Cardio Box Invers-Design */
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
    /* Tab Design */
    .stTabs [data-baseweb="tab"] {
        font-size: 18px;
        font-weight: 900;
        color: #000000 !important;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🏋️ Trainingsplan: Nico & Jessi")

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
woche = st.select_slider("Trainingswoche", options=range(1, 7))

st.markdown("---")
ok_modus = st.radio("Modus für Oberkörper-Tage (Di/Do):", 
                    ["Ausdauer (55% Gewicht)", "Muskelaufbau (75%+ Gewicht)"], horizontal=True)
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
st.sidebar.header("📖 Kürzel-Erklärung")
with st.sidebar.expander("Welches Kürzel ist was?"):
    lexikon_data = [{"Kürzel": k, "Standard-Name": default_names[k]} for k in base_keys]
    st.table(pd.DataFrame(lexikon_data))

# --- SIDEBAR: REIHENFOLGE (SORTIERUNG) ---
st.sidebar.header("🔄 Reihenfolge der Übungen")
with st.sidebar.expander("Reihenfolge anpassen"):
    st.write("Wähle die Übungen in der Reihenfolge aus, in der sie erscheinen sollen:")
    
    order_beine_list = saved_values.get("ORDER_BEINE", "BS,HS,BP,BSS,BB,AD,SS").split(",")
    order_beine = st.multiselect("Sortierung Beine (Mo/Fr)", options=base_keys, 
                                 default=[k for k in order_beine_list if k in base_keys])
    
    order_ok_list = saved_values.get("ORDER_OK", "RE,RB,BR,SH,HSH,TD,BC,HC").split(",")
    order_ok = st.multiselect("Sortierung OK (Di/Do)", options=base_keys, 
                               default=[k for k in order_ok_list if k in base_keys])
    
    order_po_list = saved_values.get("ORDER_PO", "HT,RDL,ABD,KB,KB45").split(",")
    order_po = st.multiselect("Sortierung Po (Mi)", options=base_keys, 
                               default=[k for k in order_po_list if k in base_keys])

# --- SIDEBAR: ÜBUNGSMANAGEMENT ---
with st.sidebar.expander("📝 Namen der Basisübungen ändern"):
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

# --- SPEICHER-BUTTON (CLOUD SYNC) ---
if st.sidebar.button("💾 ALLES IN CLOUD SPEICHERN"):
    data_to_save = rms.copy()
    for k, v in name_map.items(): data_to_save[f"NAME_{k}"] = v
    data_to_save["ORDER_BEINE"] = ",".join(order_beine)
    data_to_save["ORDER_OK"] = ",".join(order_ok)
    data_to_save["ORDER_PO"] = ",".join(order_po)
    for i in range(1, 6):
        key = f"EXTRA_{i}"
        data_to_save[f"EX_N_{i}"] = extra_exercises[key]["name"] if key in extra_exercises else ""
        data_to_save[f"EX_D_{i}"] = extra_exercises[key]["day"] if key in extra_exercises else "Keiner"
    
    df_save = pd.DataFrame([data_to_save])
    conn.update(worksheet=user_choice, data=df_save)
    st.sidebar.success(f"Daten für {user_choice} erfolgreich gesichert!")
    st.cache_data.clear()

# --- RECHEN-LOGIK ---
def calculate_weight(val, is_heavy_day=False):
    # Logik: Muskelaufbau/Beine/Po = Progressiv | Ausdauer = Statisch 55%
    if is_heavy_day or is_heavy_ok:
        factor = 0.75 + (0.05 * (woche - 1))
    else:
        factor = 0.55
    return round(val * factor, 1)

# --- ANZEIGEFUNKTION FÜR TRAININGSTAGE ---
def display_training_day(day_label, active_keys, heavy_default):
    st.markdown('<div class="cardio-box">🏃 CARDIO: 30 MIN (STAIRMASTER / WAHLWEISE)</div>', unsafe_allow_html=True)
    
    # Basisübungen rendern
    for k in active_keys:
        if k in name_map:
            st.metric(
                label=name_map[k], 
                value=f"{calculate_weight(rms[k], heavy_default)} kg", 
                delta=f"Kürzel: {k} | 3-4 Sätze | 8-15 Wdh",
                delta_color="normal"
            )
            
    # Zusatzübungen für diesen spezifischen Tag rendern
    for k, info in extra_exercises.items():
        if info["day"] == day_label:
            st.metric(
                label=info["name"], 
                value=f"{calculate_weight(rms[k], True)} kg", 
                delta="Zusatzübung | 3 Sätze",
                delta_color="normal"
            )

# --- HAUPTANSICHT: TABS ---
tabs = st.tabs(["Mo: Beine", "Di: OK", "Mi: PO", "Do: OK", "Fr: Beine"])

with tabs[0]: # Montag
    display_training_day("Mo: Beine", order_beine, True)

with tabs[1]: # Dienstag
    display_training_day("Di: OK", order_ok, False)

with tabs[2]: # Mittwoch
    display_training_day("Mi: PO", order_po, True)

with tabs[3]: # Donnerstag
    display_training_day("Do: OK", order_ok, False)

with tabs[4]: # Freitag
    display_training_day("Fr: Beine", order_beine, True)
