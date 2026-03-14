import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# Seiteneinstellungen
st.set_page_config(page_title="Gym Progress Ultimate", page_icon="💪", layout="centered")

# CSS für Design & Mobile-Sichtbarkeit
st.markdown("""
    <style>
    [data-testid="stMetric"] { background-color: #ffffff; border: 2px solid #eeeeee; padding: 15px; border-radius: 15px; }
    [data-testid="stMetricValue"] { color: #000000 !important; font-size: 1.6rem !important; }
    [data-testid="stMetricLabel"] { color: #444444 !important; font-size: 1.1rem !important; }
    .cardio-box { background-color: #f0f2f6; border-left: 5px solid #ff4b4b; padding: 15px; margin: 10px 0; border-radius: 10px; font-size: 1.1rem; }
    </style>
    """, unsafe_allow_html=True)

st.title("🏋️ Trainingsplan: Vollversion mit Cloud-Speicher")

# --- GOOGLE SHEETS VERBINDUNG ---
conn = st.connection("gsheets", type=GSheetsConnection)

# 1. Setup & Namen
col_n1, col_n2 = st.columns(2)
with col_n1:
    name_p1 = st.text_input("Name Person 1", "Elias")
with col_n2:
    name_p2 = st.text_input("Name Person 2", "Sarah")

user_choice = st.selectbox("Wer trainiert gerade?", [name_p1, name_p2])
woche = st.select_slider("Aktuelle Trainingswoche", options=range(1, 7))

# 2. Sidebar für ALLE 1RM Werte
st.sidebar.header(f"⚙️ 1RM Setup: {user_choice}")

def get_1rm(label, default, key_suffix):
    # Die Werte werden hier pro Person gespeichert
    return st.sidebar.number_input(f"1RM {label} (kg)", value=float(default), step=2.5, key=f"{user_choice}_{key_suffix}")

rms = {
    "Beinstrecker": get_1rm("Beinstrecker", 100, "bs"),
    "Hack Squat": get_1rm("Hack Squat", 60, "hs"),
    "Beinpresse": get_1rm("Beinpresse (schulterbreit)", 79, "bp"),
    "Bulg. Split": get_1rm("Bulgarian Split Squats", 7, "bss"),
    "Beinbeuger": get_1rm("Beinbeuger (liegend)", 6, "bb"),
    "Adduktoren": get_1rm("Adduktoren", 78, "ad"),
    "Sissy Squat": get_1rm("Sissy Squats", 80, "ss"),
    "Ruder Eng": get_1rm("Rudern Seil (eng)", 50, "re"),
    "Ruder Breit": get_1rm("Rudern Seil (breit)", 50, "rb"),
    "Brust": get_1rm("Butterfly / Brustpresse", 40, "bp_ok"),
    "Seitheben": get_1rm("Seitliche Schulter", 15, "sh"),
    "Hint. Schulter": get_1rm("Hintere Schulter", 15, "hsh"),
    "Trizeps": get_1rm("Trizepsdrücken", 20, "td"),
    "Incline Bizeps": get_1rm("Incline Bizeps Curls", 15, "bc"),
    "Hammer Curls": get_1rm("Hammer Curls", 15, "hc"),
    "Hipthrusts": get_1rm("Hipthrusts", 120, "ht"),
    "RDL": get_1rm("RDL", 90, "rdl"),
    "Abduktoren": get_1rm("Abduktoren", 80, "abd"),
    "Kickbacks": get_1rm("Kickbacks (gerade)", 20, "kb"),
    "Kickbacks 45": get_1rm("Kickbacks 45°", 15, "kb45")
}

# SPEICHER-BUTTON FÜR DAS GOOGLE SHEET
if st.sidebar.button("✅ JETZT IN CLOUD SPEICHERN"):
    # Daten in DataFrame umwandeln
    df_to_save = pd.DataFrame([rms])
    df_to_save['Nutzer'] = user_choice
    # In Google Sheet schreiben
    conn.update(worksheet=user_choice, data=df_to_save)
    st.sidebar.success(f"Werte für {user_choice} gespeichert!")

# Berechnungs-Logik
def weight(name, is_ausdauer=False):
    base = rms[name]
    if is_ausdauer: return round(base * 0.55, 1)
    return round(base * (0.75 + (0.05 * (woche - 1))), 1)

# 3. Die Wochentage (ALLE VOLLSTÄNDIG)
tabs = st.tabs(["Mo: Beine", "Di: OK", "Mi: PO", "Do: OK", "Fr: Beine"])

# --- MONTAG: BEINE ---
with tabs[0]:
    st.markdown('<div class="cardio-box">🏃 <b>Cardio:</b> 30 Min Stairmaster (Pflicht)</div>', unsafe_allow_html=True)
    st.metric("Beinstrecker", f"{weight('Beinstrecker')} kg", "4 Sätze | 8-12 Wdh | 120s Pause")
    st.metric("Hack Squat", f"{weight('Hack Squat')} kg", "4 Sätze | 8-12 Wdh | 120s Pause")
    st.metric("Beinpresse (schulterbreit)", f"{weight('Beinpresse')} kg", "3 Sätze | 8-12 Wdh | 120s Pause")
    st.metric("Bulgarian Split Squats", f"{weight('Bulg. Split')} kg", "3 Sätze | 10-12 Wdh | 120s Pause")
    st.metric("Beinbeuger (liegend)", f"{weight('Beinbeuger')} kg", "3 Sätze | 8-12 Wdh | 120s Pause")
    st.metric("Adduktoren", f"{weight('Adduktoren')} kg", "3 Sätze | 12-15 Wdh | 90s Pause")
    st.metric("Sissy Squats", f"{weight('Sissy Squat')} kg", "3 Sätze | Max | 90s Pause")

# --- DIENSTAG: OK ---
with tabs[1]:
    st.markdown('<div class="cardio-box">🏃 <b>Cardio:</b> 30 Min Wahlweise</div>', unsafe_allow_html=True)
    st.metric("Rudern Seil (eng)", f"{weight('Ruder Eng', True)} kg", "3 Sätze | 15-20 Wdh | 60s Pause")
    st.metric("Rudern Seil (breit)", f"{weight('Ruder Breit', True)} kg", "3 Sätze | 15-20 Wdh | 60s Pause")
    st.metric("Butterfly / Brustpresse", f"{weight('Brust', True)} kg", "3 Sätze | 15-20 Wdh | 60s Pause")
    st.metric("Seitliche Schulter (Seil)", f"{weight('Seitheben', True)} kg", "3 Sätze | 15-20 Wdh | 60s Pause")
    st.metric("Hintere Schulter (Seil)", f"{weight('Hint. Schulter', True)} kg", "3 Sätze | 15-20 Wdh | 60s Pause")
    st.metric("Trizepsdrücken (Seil)", f"{weight('Trizeps', True)} kg", "3 Sätze | 15-20 Wdh | 60s Pause")
    st.metric("Incline Bizeps Curls", f"{weight('Incline Bizeps', True)} kg", "3 Sätze | 15-20 Wdh | 60s Pause")
    st.metric("Hammer Curls (Seil)", f"{weight('Hammer Curls', True)} kg", "3 Sätze | 15-20 Wdh | 60s Pause")
    st.metric("Bauch Plank", "Körpergewicht", "3 Sätze | Max | 60s Pause")

# --- MITTWOCH: PO ---
with tabs[2]:
    st.markdown('<div class="cardio-box">🏃 <b>Cardio:</b> 30 Min Stairmaster (Pflicht)</div>', unsafe_allow_html=True)
    st.metric("Hipthrusts", f"{weight('Hipthrusts')} kg", "4 Sätze | 10-12 Wdh | 120s Pause")
    st.metric("RDL", f"{weight('RDL')} kg", "3 Sätze | 10-12 Wdh | 120s Pause")
    st.metric("Abduktoren (90°/75°)", f"{weight('Abduktoren')} kg", "4 Sätze | 12-15 Wdh | 90s Pause")
    st.metric("Kickbacks (gerade)", f"{weight('Kickbacks')} kg", "3 Sätze | 12-15 Wdh | 60s Pause")
    st.metric("Kickbacks 45°", f"{weight('Kickbacks 45')} kg", "3 Sätze | 12-15 Wdh | 60s Pause")

# --- DONNERSTAG: OK (Vollständig) ---
with tabs[3]:
    st.markdown('<div class="cardio-box">🏃 <b>Cardio:</b> 30 Min Wahlweise</div>', unsafe_allow_html=True)
    st.metric("Rudern Seil (eng)", f"{weight('Ruder Eng', True)} kg", "3 Sätze | 15-20 Wdh | 60s Pause")
    st.metric("Rudern Seil (breit)", f"{weight('Ruder Breit', True)} kg", "3 Sätze | 15-20 Wdh | 60s Pause")
    st.metric("Butterfly / Brustpresse", f"{weight('Brust', True)} kg", "3 Sätze | 15-20 Wdh | 60s Pause")
    st.metric("Seitliche Schulter (Seil)", f"{weight('Seitheben', True)} kg", "3 Sätze | 15-20 Wdh | 60s Pause")
    st.metric("Hintere Schulter (Seil)", f"{weight('Hint. Schulter', True)} kg", "3 Sätze | 15-20 Wdh | 60s Pause")
    st.metric("Trizepsdrücken (Seil)", f"{weight('Trizeps', True)} kg", "3 Sätze | 15-20 Wdh | 60s Pause")
    st.metric("Incline Bizeps Curls", f"{weight('Incline Bizeps', True)} kg", "3 Sätze | 15-20 Wdh | 60s Pause")
    st.metric("Hammer Curls (Seil)", f"{weight('Hammer Curls', True)} kg", "3 Sätze | 15-20 Wdh | 60s Pause")
    st.metric("Bauch Plank", "Körpergewicht", "3 Sätze | Max | 60s Pause")

# --- FREITAG: BEINE (Vollständig) ---
with tabs[4]:
    st.markdown('<div class="cardio-box">🏃 <b>Cardio:</b> 30 Min Stairmaster (Pflicht)</div>', unsafe_allow_html=True)
    st.metric("Beinstrecker", f"{weight('Beinstrecker')} kg", "4 Sätze | 8-12 Wdh | 120s Pause")
    st.metric("Hack Squat", f"{weight('Hack Squat')} kg", "4 Sätze | 8-12 Wdh | 120s Pause")
    st.metric("Beinpresse (schulterbreit)", f"{weight('Beinpresse')} kg", "3 Sätze | 8-12 Wdh | 120s Pause")
    st.metric("Bulgarian Split Squats", f"{weight('Bulg. Split')} kg", "3 Sätze | 10-12 Wdh | 120s Pause")
    st.metric("Beinbeuger (liegend)", f"{weight('Beinbeuger')} kg", "3 Sätze | 8-12 Wdh | 120s Pause")
    st.metric("Adduktoren", f"{weight('Adduktoren')} kg", "3 Sätze | 12-15 Wdh | 90s Pause")
    st.metric("Sissy Squats", f"{weight('Sissy Squat')} kg", "3 Sätze | Max | 90s Pause")
