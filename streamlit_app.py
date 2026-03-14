import streamlit as st

# Seiteneinstellungen
st.set_page_config(page_title="Gym Progress Master", page_icon="💪", layout="centered")

# CSS für besseres Mobile-Handling und Kontrast
st.markdown("""
    <style>
    [data-testid="stMetric"] {
        background-color: #ffffff;
        border: 2px solid #eeeeee;
        padding: 15px;
        border-radius: 15px;
    }
    [data-testid="stMetricValue"] {
        color: #000000 !important;
        font-size: 1.8rem !important;
    }
    .stTabs [data-baseweb="tab"] {
        font-size: 14px;
        padding: 8px;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🏋️ Trainingsplan 2026")

# 1. Namen & Setup
col_n1, col_n2 = st.columns(2)
with col_n1:
    name_p1 = st.text_input("Name Person 1", "Elias")
with col_n2:
    name_p2 = st.text_input("Name Person 2", "Sarah")

user_choice = st.selectbox("Wer trainiert?", [name_p1, name_p2])
woche = st.select_slider("Trainingswoche", options=range(1, 7))

# 2. Sidebar Setup für alle Übungen
st.sidebar.header(f"⚙️ 1RM Setup: {user_choice}")

def get_1rm(label, default):
    return st.sidebar.number_input(f"1RM {label} (kg)", value=float(default), step=2.5)

# Alle 1RMs aus deiner Liste
rms = {
    # Beine
    "Beinstrecker": get_1rm("Beinstrecker", 100),
    "Hack Squat": get_1rm("Hack Squat", 80),
    "Beinpresse": get_1rm("Beinpresse", 150),
    "Beinbeuger": get_1rm("Beinbeuger", 50),
    "Adduktoren": get_1rm("Adduktoren", 60),
    "Sissy Squat": get_1rm("Sissy Squat", 20),
    "Bulg. Split": get_1rm("Bulg. Split", 40),
    # Oberkörper
    "Ruder Eng": get_1rm("Rudern Eng", 60),
    "Ruder Breit": get_1rm("Rudern Breit", 55),
    "Brust": get_1rm("Brustpresse", 50),
    "Seitheben": get_1rm("Seitheben", 10),
    "Hint. Schulter": get_1rm("Hint. Schulter", 10),
    "Trizeps": get_1rm("Trizeps", 25),
    "Incline Bizeps": get_1rm("Incline Bizeps", 15),
    "Hammer Curls": get_1rm("Hammer Curls", 15),
    # PO
    "Hipthrusts": get_1rm("Hipthrusts", 120),
    "RDL": get_1rm("RDL", 90),
    "Abduktoren": get_1rm("Abduktoren", 70),
    "Kickbacks": get_1rm("Kickbacks", 20),
    "Kickbacks 45": get_1rm("Kickbacks 45°", 15)
}

# Berechnungsfunktion
def weight(name, is_ausdauer=False):
    base = rms[name]
    if is_ausdauer:
        return round(base * 0.55, 1)
    # Kraft-Progression: 75% + 5% pro Woche
    factor = 0.75 + (0.05 * (woche - 1))
    return round(base * factor, 1)

# 3. Die Wochentage (Tabs)
tabs = st.tabs(["Mo: Beine", "Di: OK", "Mi: PO", "Do: OK", "Fr: Beine"])

# MONTAG: Beine
with tabs[0]:
    st.subheader("🟢 Montag: Beine (Kraft)")
    st.metric("Beinstrecker", f"{weight('Beinstrecker')} kg", "3 Sätze | 8-12")
    st.metric("Beinbeuger (liegend)", f"{weight('Beinbeuger')} kg", "3 Sätze | 8-12")
    st.metric("Hack Squat (schräg)", f"{weight('Hack Squat')} kg", "4 Sätze | 8-10")
    st.metric("Adduktoren", f"{weight('Adduktoren')} kg", "3 Sätze | 12-15")
    st.metric("Sissy-Squats", f"{weight('Sissy Squat')} kg", "3 Sätze | Max")
    st.metric("Beinpresse (oben/breit)", f"{weight('Beinpresse')} kg", "3 Sätze | 10-12")
    st.metric("Bulgarian Split Squats", f"{weight('Bulg. Split')} kg", "3 Sätze | 10")

# DIENSTAG: Oberkörper
with tabs[1]:
    st.subheader("🔵 Dienstag: Oberkörper (Ausdauer)")
    st.metric("Rudern Eng (Bauchnabel)", f"{weight('Ruder Eng', True)} kg", "15-20 Wdh")
    st.metric("Rudern Breit (Brust)", f"{weight('Ruder Breit', True)} kg", "15-20 Wdh")
    st.metric("Butterfly / Brustpresse", f"{weight('Brust', True)} kg", "15-20 Wdh")
    st.metric("Seitliche Schulter", f"{weight('Seitheben', True)} kg", "20 Wdh")
    st.metric("Hintere Schulter", f"{weight('Hint. Schulter', True)} kg", "20 Wdh")
    st.metric("Trizepsdrücken", f"{weight('Trizeps', True)} kg", "20 Wdh")
    st.metric("Incline Bizeps", f"{weight('Incline Bizeps', True)} kg", "20 Wdh")
    st.metric("Hammer Curls", f"{weight('Hammer Curls', True)} kg", "20 Wdh")
    st.info("Bauch: Plank (3 Sätze Max)")

# MITTWOCH: PO
with tabs[2]:
    st.subheader("🍑 Mittwoch: PO (Kraft)")
    st.metric("Hipthrusts", f"{weight('Hipthrusts')} kg", "4 Sätze | 10-12")
    st.metric("Kickbacks (gerade)", f"{weight('Kickbacks')} kg", "3 Sätze | 15")
    st.metric("Abduktoren (90° & 75°)", f"{weight('Abduktoren')} kg", "4 Sätze | 15")
    st.metric("Kickbacks 45°", f"{weight('Kickbacks 45')} kg", "3 Sätze | 15")
    st.metric("RDL", f"{weight('RDL')} kg", "3 Sätze | 10-12")

# DONNERSTAG: Oberkörper
with tabs[3]:
    st.subheader("🔵 Donnerstag: OK (Ausdauer)")
    st.write("Wiederholung von Dienstag – Fokus auf kurze Pausen (45-60s).")
    # Einfachheitshalber Link auf Dienstag setzen oder Felder duplizieren
    st.metric("Brustpresse", f"{weight('Brust', True)} kg", "20 Wdh")
    st.metric("Rudern Breit", f"{weight('Ruder Breit', True)} kg", "20 Wdh")
    st.metric("Seitheben", f"{weight('Seitheben', True)} kg", "20 Wdh")

# FREITAG: Beine
with tabs[4]:
    st.subheader("🟢 Freitag: Beine (Kraft)")
    st.write("Wiederholung von Montag – Versuche die Intensität zu halten!")
    st.metric("Hack Squat", f"{weight('Hack Squat')} kg", "4 Sätze")
    st.metric("Beinpresse", f"{weight('Beinpresse')} kg", "3 Sätze")
    st.metric("Beinstrecker", f"{weight('Beinstrecker')} kg", "3 Sätze")
