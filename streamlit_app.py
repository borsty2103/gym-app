import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# Seiteneinstellungen
st.set_page_config(page_title="Gym Progress Ultimate", page_icon="💪", layout="centered")

# CSS für maximale Lesbarkeit und festen Kontrast (Kein Weiß-auf-Weiß mehr!)
st.markdown("""
    <style>
    /* Karten-Design */
    [data-testid="stMetric"] {
        background-color: #ffffff !important;
        border: 1px solid #dddddd !important;
        padding: 20px !important;
        border-radius: 12px !important;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1) !important;
    }
    /* Schwarze Schriftfarbe für alle Texte in den Karten */
    [data-testid="stMetricLabel"] {
        color: #333333 !important;
        font-size: 1.1rem !important;
        font-weight: 600 !important;
    }
    [data-testid="stMetricValue"] {
        color: #000000 !important;
        font-size: 1.8rem !important;
        font-weight: 800 !important;
    }
    [data-testid="stMetricDelta"] {
        color: #555555 !important;
        font-size: 1rem !important;
        font-weight: 500 !important;
    }
    /* Cardio Box Design */
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
    /* Tabs Schriftgröße */
    .stTabs [data-baseweb="tab"] {
        font-size: 18px;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🏋️ Unser Trainingsplan (ABSOLUT VOLLSTÄNDIG)")

# Google Sheets Verbindung
conn = st.connection("gsheets", type=GSheetsConnection)

# --- SETUP BEREICH ---
col_n1, col_n2 = st.columns(2)
with col_n1:
    p1 = st.text_input("Name Person 1", "Elias")
with col_n2:
    p2 = st.text_input("Name Person 2", "Sarah")

user_choice = st.selectbox("Wer trainiert gerade?", [p1, p2])
woche = st.select_slider("Trainingswoche", options=range(1, 7))

# Modus-Umschalter für Oberkörper
st.markdown("---")
ok_modus = st.radio(
    "Modus für Oberkörper-Tage (Di/Do):",
    ["Ausdauer (55% Gewicht | 15-20 Wdh)", "Muskelaufbau (75%+ Gewicht | 8-12 Wdh)"],
    horizontal=True
)
is_heavy_ok = "Muskelaufbau" in ok_modus
st.markdown("---")

# --- SIDEBAR 1RM SETUP (Alle 20 Übungen einzeln) ---
st.sidebar.header(f"⚙️ 1RM Setup: {user_choice}")
def g1(label, default, k):
    return st.sidebar.number_input(f"1RM {label} (kg)", value=float(default), step=2.5, key=f"{user_choice}_{k}")

rms = {
    "BS": g1("Beinstrecker", 100, "bs"),
    "HS": g1("Hack Squat", 60, "hs"),
    "BP": g1("Beinpresse", 80, "bp"),
    "BSS": g1("Bulg. Split", 20, "bss"),
    "BB": g1("Beinbeuger", 40, "bb"),
    "AD": g1("Adduktoren", 70, "ad"),
    "SS": g1("Sissy Squat", 10, "ss"),
    "RE": g1("Rudern Eng", 50, "re"),
    "RB": g1("Rudern Breit", 50, "rb"),
    "BR": g1("Brustpresse", 40, "br"),
    "SH": g1("Seitheben", 15, "sh"),
    "HSH": g1("Hint. Schulter", 15, "hsh"),
    "TD": g1("Trizeps", 20, "td"),
    "BC": g1("Incline Bizeps", 15, "bc"),
    "HC": g1("Hammer Curls", 15, "hc"),
    "HT": g1("Hipthrusts", 120, "ht"),
    "RDL": g1("RDL", 80, "rdl"),
    "ABD": g1("Abduktoren", 80, "abd"),
    "KB": g1("Kickbacks", 15, "kb"),
    "KB45": g1("Kickbacks 45°", 15, "kb45")
}

if st.sidebar.button("✅ WERTE IN CLOUD SPEICHERN"):
    df = pd.DataFrame([rms])
    df['Nutzer'] = user_choice
    conn.update(worksheet=user_choice, data=df)
    st.sidebar.success("Erfolgreich gespeichert!")

# --- BERECHNUNG ---
def calc(val, force_heavy=False):
    if force_heavy or is_heavy_ok:
        f = 0.75 + (0.05 * (woche - 1))
    else:
        f = 0.55
    return round(val * f, 1)

tabs = st.tabs(["Mo: Beine", "Di: OK", "Mi: PO", "Do: OK", "Fr: Beine"])

# --- MONTAG: BEINE ---
with tabs[0]:
    st.markdown('<div class="cardio-box">🏃 Cardio: 30 Min Stairmaster (Pflicht)</div>', unsafe_allow_html=True)
    st.metric("Beinstrecker", f"{calc(rms['BS'], True)} kg", "4 Sätze | 8-12 Wdh | 120s Pause")
    st.metric("Hack Squat (Schräg)", f"{calc(rms['HS'], True)} kg", "4 Sätze | 8-12 Wdh | 120s Pause")
    st.metric("Beinpresse (Schulterbreit)", f"{calc(rms['BP'], True)} kg", "3 Sätze | 8-12 Wdh | 120s Pause")
    st.metric("Bulgarian Split Squats", f"{calc(rms['BSS'], True)} kg", "3 Sätze | 10-12 Wdh | 120s Pause")
    st.metric("Beinbeuger liegend", f"{calc(rms['BB'], True)} kg", "3 Sätze | 8-12 Wdh | 120s Pause")
    st.metric("Adduktoren", f"{calc(rms['AD'], True)} kg", "3 Sätze | 12-15 Wdh | 90s Pause")
    st.metric("Sissy Squat", f"{calc(rms['SS'], True)} kg", "3 Sätze | Max Wdh | 90s Pause")

# --- DIENSTAG: OK ---
with tabs[1]:
    st.markdown('<div class="cardio-box">🏃 Cardio: 30 Min Wahlweise</div>', unsafe_allow_html=True)
    r = "8-12 Wdh | 90s" if is_heavy_ok else "15-20 Wdh | 60s"
    st.metric("Rudern Seil (Eng)", f"{calc(rms['RE'])} kg", f"3 Sätze | {r} Pause")
    st.metric("Rudern Seil (Breit)", f"{calc(rms['RB'])} kg", f"3 Sätze | {r} Pause")
    st.metric("Brustpresse", f"{calc(rms['BR'])} kg", f"3 Sätze | {r} Pause")
    st.metric("Seitheben (Seil)", f"{calc(rms['SH'])} kg", f"3 Sätze | {r} Pause")
    st.metric("Hintere Schulter (Seil)", f"{calc(rms['HSH'])} kg", f"3 Sätze | {r} Pause")
    st.metric("Trizepsdrücken (Seil)", f"{calc(rms['TD'])} kg", f"3 Sätze | {r} Pause")
    st.metric("Incline Bizeps Curls", f"{calc(rms['BC'])} kg", f"3 Sätze | {r} Pause")
    st.metric("Hammer Curls (Seil)", f"{calc(rms['HC'])} kg", f"3 Sätze | {r} Pause")
    st.metric("Bauch: Plank", "Körpergewicht", "3 Sätze | Max Zeit | 60s Pause")

# --- MITTWOCH: PO ---
with tabs[2]:
    st.markdown('<div class="cardio-box">🏃 Cardio: 30 Min Stairmaster (Pflicht)</div>', unsafe_allow_html=True)
    st.metric("Hipthrusts", f"{calc(rms['HT'], True)} kg", "4 Sätze | 10-12 Wdh | 120s Pause")
    st.metric("RDL", f"{calc(rms['RDL'], True)} kg", "3 Sätze | 10-12 Wdh | 120s Pause")
    st.metric("Abduktoren (90° & 75°)", f"{calc(rms['ABD'], True)} kg", "4 Sätze | 12-15 Wdh | 90s Pause")
    st.metric("Kickbacks (Gerade)", f"{calc(rms['KB'], True)} kg", "3 Sätze | 12-15 Wdh | 60s Pause")
    st.metric("Kickbacks 45°", f"{calc(rms['KB45'], True)} kg", "3 Sätze | 12-15 Wdh | 60s Pause")

# --- DONNERSTAG: OK ---
with tabs[3]:
    st.markdown('<div class="cardio-box">🏃 Cardio: 30 Min Wahlweise</div>', unsafe_allow_html=True)
    r = "8-12 Wdh | 90s" if is_heavy_ok else "15-20 Wdh | 60s"
    st.metric("Rudern Seil (Eng)", f"{calc(rms['RE'])} kg", f"3 Sätze | {r} Pause")
    st.metric("Rudern Seil (Breit)", f"{calc(rms['RB'])} kg", f"3 Sätze | {r} Pause")
    st.metric("Brustpresse", f"{calc(rms['BR'])} kg", f"3 Sätze | {r} Pause")
    st.metric("Seitheben (Seil)", f"{calc(rms['SH'])} kg", f"3 Sätze | {r} Pause")
    st.metric("Hintere Schulter (Seil)", f"{calc(rms['HSH'])} kg", f"3 Sätze | {r} Pause")
    st.metric("Trizepsdrücken (Seil)", f"{calc(rms['TD'])} kg", f"3 Sätze | {r} Pause")
    st.metric("Incline Bizeps Curls", f"{calc(rms['BC'])} kg", f"3 Sätze | {r} Pause")
    st.metric("Hammer Curls (Seil)", f"{calc(rms['HC'])} kg", f"3 Sätze | {r} Pause")
    st.metric("Bauch: Plank", "Körpergewicht", "3 Sätze | Max Zeit | 60s Pause")

# --- FREITAG: BEINE ---
with tabs[4]:
    st.markdown('<div class="cardio-box">🏃 Cardio: 30 Min Stairmaster (Pflicht)</div>', unsafe_allow_html=True)
    st.metric("Beinstrecker", f"{calc(rms['BS'], True)} kg", "4 Sätze | 8-12 Wdh | 120s Pause")
    st.metric("Hack Squat (Schräg)", f"{calc(rms['HS'], True)} kg", "4 Sätze | 8-12 Wdh | 120s Pause")
    st.metric("Beinpresse (Schulterbreit)", f"{calc(rms['BP'], True)} kg", "3 Sätze | 8-12 Wdh | 120s Pause")
    st.metric("Bulgarian Split Squats", f"{calc(rms['BSS'], True)} kg", "3 Sätze | 10-12 Wdh | 120s Pause")
    st.metric("Beinbeuger liegend", f"{calc(rms['BB'], True)} kg", "3 Sätze | 8-12 Wdh | 120s Pause")
    st.metric("Adduktoren", f"{calc(rms['AD'], True)} kg", "3 Sätze | 12-15 Wdh | 90s Pause")
    st.metric("Sissy Squat", f"{calc(rms['SS'], True)} kg", "3 Sätze | Max Wdh | 90s Pause")
