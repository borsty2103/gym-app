import streamlit as st

# Seiteneinstellungen für Mobile
st.set_page_config(page_title="Gym Progress Pro", page_icon="🏋️", layout="centered")

# Design-Anpassung für große Buttons am Handy
st.markdown("""
    <style>
    .stButton>button { width: 100%; height: 3em; font-size: 20px; }
    .stMetric { background-color: #f0f2f6; padding: 10px; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

st.title("🏋️ Unser Trainingsplan")

# 1. Personen & Wochen Auswahl
col_user, col_week = st.columns(2)
with col_user:
    user = st.selectbox("Wer trainiert?", ["Person 1", "Person 2"])
with col_week:
    woche = st.number_input("Woche", min_value=1, max_value=12, value=1)

# 2. 1RM Speicher (Simuliert - für eine echte DB müsste man Google Sheets anbinden)
# Hier definieren wir Standardwerte, die du in der Sidebar ändern kannst
st.sidebar.header(f"Setze 1RM für {user}")
def get_1rm(label, default):
    return st.sidebar.number_input(f"1RM {label} (kg)", value=default)

# Deine Übungsliste mit 1RM Eingabe
one_rm = {
    "Beinstrecker": get_1rm("Beinstrecker", 100),
    "Hack Squat": get_1rm("Hack Squat", 60),
    "Beinpresse": get_1rm("Beinpresse", 80),
    "Bulgarian Split": get_1rm("Bulg. Split", 20),
    "Beinbeuger": get_1rm("Beinbeuger", 40),
    "Adduktoren": get_1rm("Adduktoren", 70),
    "Sissy Squat": get_1rm("Sissy Squat", 10),
    "Rudern Eng": get_1rm("Rudern Eng", 50),
    "Rudern Breit": get_1rm("Rudern Breit", 50),
    "Brustpresse": get_1rm("Brustpresse", 40),
    "Seitheben": get_1rm("Seitheben", 15),
    "Hintere Schulter": get_1rm("Hint. Schulter", 15),
    "Trizeps": get_1rm("Trizeps", 20),
    "Bizeps Incline": get_1rm("Bizeps Incline", 15),
    "Hammer Curls": get_1rm("Hammer Curls", 15),
    "Hipthrusts": get_1rm("Hipthrusts", 120),
    "RDL": get_1rm("RDL", 80),
    "Abduktoren": get_1rm("Abduktoren", 80),
    "Kickbacks": get_1rm("Kickbacks", 15)
}

# 3. Berechnungs-Logik
def calc_weight(name, is_ausdauer=False):
    base = one_rm[name]
    if is_ausdauer:
        return round(base * 0.55, 1) # Konstante Ausdauerlast
    # Kraft: Woche 1 = 75%, Woche 2 = 80%, etc.
    factor = 0.75 + (0.05 * (woche - 1))
    return round(base * factor, 1)

# 4. Die Wochentage als Tabs (Mobile optimiert)
tag_names = ["Mo: Beine", "Di: OK", "Mi: PO", "Do: OK", "Fr: Beine"]
tabs = st.tabs(tag_names)

# MONTAG & FREITAG (Beine)
for i in [0, 4]:
    with tabs[i]:
        st.success("Fokus: Muskelaufbau | Cardio: 30m Stairmaster")
        st.metric("Hack Squat (Schräg)", f"{calc_weight('Hack Squat')} kg", "8-12 Wdh")
        st.metric("Beinpresse (Schulterbreit)", f"{calc_weight('Beinpresse')} kg", "8-12 Wdh")
        st.metric("Bulgarian Split Squats", f"{calc_weight('Bulgarian Split')} kg", "10-12 Wdh")
        st.metric("Beinstrecker", f"{calc_weight('Beinstrecker')} kg", "12 Wdh")
        st.metric("Beinbeuger liegend", f"{calc_weight('Beinbeuger')} kg", "12 Wdh")
        st.write("Finisher: Adduktoren & Sissy Squats (3 Sätze Max)")

# DIENSTAG & DONNERSTAG (Oberkörper)
for i in [1, 3]:
    with tabs[i]:
        st.info("Fokus: Ausdauer | Cardio: 30m Wahl")
        st.metric("Rudern (Eng & Breit)", f"{calc_weight('Rudern Eng', True)} kg", "15-20 Wdh")
        st.metric("Brustpresse / Butterfly", f"{calc_weight('Brustpresse', True)} kg", "15-20 Wdh")
        st.metric("Schultern (Seite/Hinten)", f"{calc_weight('Seitheben', True)} kg", "20 Wdh")
        st.metric("Arme (Bizeps/Trizeps)", f"{calc_weight('Trizeps', True)} kg", "20 Wdh")
        st.write("Core: Bauch Plank (3 Sätze Max)")

# MITTWOCH (PO)
with tabs[2]:
    st.warning("Fokus: PO Aufbau | Cardio: 30m Stairmaster")
    st.metric("Hip Thrusts", f"{calc_weight('Hipthrusts')} kg", "10-12 Wdh")
    st.metric("RDL (Rumänisch Kreuzheben)", f"{calc_weight('RDL')} kg", "10-12 Wdh")
    st.metric("Abduktoren (90° & 75°)", f"{calc_weight('Abduktoren')} kg", "15 Wdh")
    st.metric("Kickbacks (Gerade & 45°)", f"{calc_weight('Kickbacks')} kg", "15 Wdh")
