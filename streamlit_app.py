import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# Seiteneinstellungen
st.set_page_config(page_title="Gym Progress Ultimate", page_icon="💪", layout="centered")

# CSS für maximale Lesbarkeit und festen Kontrast
st.markdown("""
    <style>
    [data-testid="stMetric"] {
        background-color: #ffffff !important;
        border: 1px solid #dddddd !important;
        padding: 20px !important;
        border-radius: 12px !important;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1) !important;
    }
    [data-testid="stMetricLabel"] { color: #333333 !important; font-size: 1.1rem !important; font-weight: 600 !important; }
    [data-testid="stMetricValue"] { color: #000000 !important; font-size: 1.8rem !important; font-weight: 800 !important; }
    .cardio-box {
        background-color: #f0f2f6;
        border-left: 5px solid #ff4b4b;
        color: #1f2937;
        padding: 15px;
        margin: 15px 0;
        border-radius: 8px;
        font-weight: bold;
        font-size: 1.1rem;
    }
    .stTabs [data-baseweb="tab"] { font-size: 18px; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

st.title("🏋️ Trainingsplan: Nico & Jessi")

# --- VERBINDUNG ZU GOOGLE SHEETS ---
conn = st.connection("gsheets", type=GSheetsConnection)

# --- SETUP PERSONEN ---
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
                    ["Ausdauer (55% | 15-20 Wdh)", "Muskelaufbau (75%+ | 8-12 Wdh)"], horizontal=True)
is_heavy_ok = "Muskelaufbau" in ok_modus
st.markdown("---")

# --- SIDEBAR: ÜBUNGEN VERWALTEN ---
st.sidebar.header("🛠️ Übungen & Cloud-Management")

# 1. Bestehende Übungen umbenennen
with st.sidebar.expander("Bestehende Übungen umbenennen"):
    base_keys = ["BS", "HS", "BP", "BSS", "BB", "AD", "SS", "RE", "RB", "BR", "SH", "HSH", "TD", "BC", "HC", "HT", "RDL", "ABD", "KB", "KB45"]
    default_names = {
        "BS": "Beinstrecker", "HS": "Hack Squat", "BP": "Beinpresse", "BSS": "Bulgarian Split",
        "BB": "Beinbeuger", "AD": "Adduktoren", "SS": "Sissy Squat", "RE": "Rudern Eng",
        "RB": "Rudern Breit", "BR": "Brustpresse", "SH": "Seitheben", "HSH": "Hint. Schulter",
        "TD": "Trizeps", "BC": "Incline Bizeps", "HC": "Hammer Curls", "HT": "Hipthrusts",
        "RDL": "RDL", "ABD": "Abduktoren", "KB": "Kickbacks", "KB45": "Kickbacks 45°"
    }
    name_map = {}
    for k in base_keys:
        name_map[k] = st.text_input(f"Name für {k}", saved_values.get(f"NAME_{k}", default_names[k]), key=f"edit_{k}")

# 2. Neue Übungen hinzufügen (5 Slots) - Werden automatisch im Sheet gespeichert
st.sidebar.markdown("---")
st.sidebar.subheader("➕ Neue Übungen (Cloud-Sync)")
extra_exercises = {}
for i in range(1, 6):
    with st.sidebar.expander(f"Zusatz-Übung {i}"):
        ex_name = st.text_input(f"Name Übung {i}", saved_values.get(f"EXTRA_NAME_{i}", ""), key=f"ex_name_{i}")
        ex_day = st.selectbox(f"Tag für Übung {i}", ["Keiner", "Mo: Beine", "Di: OK", "Mi: PO", "Do: OK", "Fr: Beine"], 
                              index=0 if f"EXTRA_DAY_{i}" not in saved_values else ["Keiner", "Mo: Beine", "Di: OK", "Mi: PO", "Do: OK", "Fr: Beine"].index(saved_values[f"EXTRA_DAY_{i}"]),
                              key=f"ex_day_{i}")
        if ex_name:
            extra_exercises[f"EXTRA_{i}"] = {"name": ex_name, "day": ex_day}

# --- SIDEBAR: 1RM SETUP (Werte kommen aus Cloud) ---
st.sidebar.header(f"⚙️ Gewichte: {user_choice}")
rms = {}
for k in base_keys:
    val = float(saved_values.get(k, 50.0))
    rms[k] = st.sidebar.number_input(f"1RM {name_map[k]} (kg)", value=val, step=2.5, key=f"rm_{k}")

for k, info in extra_exercises.items():
    val = float(saved_values.get(k, 50.0))
    rms[k] = st.sidebar.number_input(f"1RM {info['name']} (kg)", value=val, step=2.5, key=f"rm_{k}")

# --- DER SPEICHER-MECHANISMUS (Aktualisiert das Google Sheet vollständig) ---
if st.sidebar.button("💾 ALLES IN CLOUD SPEICHERN"):
    # Erstelle ein Dictionary für alle Daten
    data_to_save = rms.copy()
    # Namen der Basis-Übungen hinzufügen
    for k, v in name_map.items(): 
        data_to_save[f"NAME_{k}"] = v
    # Namen und Tage der Zusatz-Übungen hinzufügen
    for i in range(1, 6):
        key = f"EXTRA_{i}"
        if key in extra_exercises:
            data_to_save[f"EXTRA_NAME_{i}"] = extra_exercises[key]["name"]
            data_to_save[f"EXTRA_DAY_{i}"] = extra_exercises[key]["day"]
        else:
            data_to_save[f"EXTRA_NAME_{i}"] = ""
            data_to_save[f"EXTRA_DAY_{i}"] = "Keiner"
    
    # In DataFrame umwandeln und Cloud-Update triggern
    df = pd.DataFrame([data_to_save])
    conn.update(worksheet=user_choice, data=df)
    st.sidebar.success(f"Daten für {user_choice} wurden in Google Sheets überschrieben!")
    st.cache_data.clear()

# --- BERECHNUNG ---
def calc(val, force_heavy=False):
    f = (0.75 + (0.05 * (woche - 1))) if (force_heavy or is_heavy_ok) else 0.55
    return round(val * f, 1)

def show_extras(day_name):
    for k, info in extra_exercises.items():
        if info["day"] == day_name:
            st.metric(info["name"], f"{calc(rms[k], True)} kg", "Zusatzübung | 3 Sätze")

tabs = st.tabs(["Mo: Beine", "Di: OK", "Mi: PO", "Do: OK", "Fr: Beine"])

# --- ANZEIGE DER TAGE (Keine Kürzungen!) ---
with tabs[0]: # MONTAG
    st.markdown('<div class="cardio-box">🏃 Cardio: 30 Min Stairmaster</div>', unsafe_allow_html=True)
    for k in ["BS", "HS", "BP", "BSS", "BB", "AD", "SS"]:
        st.metric(name_map[k], f"{calc(rms[k], True)} kg", "4 Sätze | 8-12 Wdh | 120s Pause")
    show_extras("Mo: Beine")

with tabs[1]: # DIENSTAG
    st.markdown('<div class="cardio-box">🏃 Cardio: 30 Min Wahlweise</div>', unsafe_allow_html=True)
    r = "8-12 Wdh | 90s" if is_heavy_ok else "15-20 Wdh | 60s"
    for k in ["RE", "RB", "BR", "SH", "HSH", "TD", "BC", "HC"]:
        st.metric(name_map[k], f"{calc(rms[k])} kg", f"3 Sätze | {r}")
    st.metric("Bauch: Plank", "Körpergewicht", "3 Sätze | Max Zeit")
    show_extras("Di: OK")

with tabs[2]: # MITTWOCH
    st.markdown('<div class="cardio-box">🏃 Cardio: 30 Min Stairmaster</div>', unsafe_allow_html=True)
    for k in ["HT", "RDL", "ABD", "KB", "KB45"]:
        st.metric(name_map[k], f"{calc(rms[k], True)} kg", "3-4 Sätze | 10-15 Wdh | 90-120s")
    show_extras("Mi: PO")

with tabs[3]: # DONNERSTAG
    st.markdown('<div class="cardio-box">🏃 Cardio: 30 Min Wahlweise</div>', unsafe_allow_html=True)
    r = "8-12 Wdh | 90s" if is_heavy_ok else "15-20 Wdh | 60s"
    for k in ["RE", "RB", "BR", "SH", "HSH", "TD", "BC", "HC"]:
        st.metric(name_map[k], f"{calc(rms[k])} kg", f"3 Sätze | {r}")
    show_extras("Do: OK")

with tabs[4]: # FREITAG
    st.markdown('<div class="cardio-box">🏃 Cardio: 30 Min Stairmaster</div>', unsafe_allow_html=True)
    for k in ["BS", "HS", "BP", "BSS", "BB", "AD", "SS"]:
        st.metric(name_map[k], f"{calc(rms[k], True)} kg", "4 Sätze | 8-12 Wdh | 120s Pause")
    show_extras("Fr: Beine")
