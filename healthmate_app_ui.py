
import streamlit as st
import time
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import datetime

# -------------------- UI SETTINGS --------------------
st.set_page_config(page_title="HealthMate", layout="centered")

st.markdown(
    '''
    <style>
    body { background-color: #f9fbfc; }
    .title { text-align: center; font-size: 32px; font-weight: bold; color: #008080; margin-bottom: 10px; }
    .subtitle { text-align: center; font-size: 18px; color: #444; margin-bottom: 20px; }
    .section-title { font-size: 20px; margin-top: 20px; color: #006666; }
    </style>
    ''',
    unsafe_allow_html=True
)

st.markdown('<div class="title">🩺 HealthMate</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Your Smart Health Assistant</div>', unsafe_allow_html=True)

# -------------------- BASIC INFO --------------------
st.markdown('<div class="section-title">👤 Basic Information</div>', unsafe_allow_html=True)
age = st.slider("Age", 1, 100, 25)
gender = st.radio("Gender", ["Male", "Female", "Other"], horizontal=True)
activity_level = st.selectbox("Physical Activity Level", ["Low", "Moderate", "High"])

# -------------------- SYMPTOMS --------------------
st.markdown('<div class="section-title">🤒 Current Symptoms</div>', unsafe_allow_html=True)
symptoms = st.multiselect(
    "What symptoms are you experiencing?",
    ["Fever", "Cough", "Shortness of breath", "Joint Pain", "Headache", "Fatigue", "Skin rash", "Chest pain"]
)

uploaded_image = st.file_uploader("📷 Upload an image (optional)", type=["jpg", "jpeg", "png"])

# -------------------- ANALYSIS --------------------
symptom_weights = {
    "Fever": 2, "Cough": 1, "Shortness of breath": 4,
    "Joint Pain": 2, "Headache": 1, "Fatigue": 1,
    "Skin rash": 2, "Chest pain": 5
}

def get_modifier(age, gender, activity):
    m = 1.0
    if age > 60: m += 0.5
    elif age < 12: m += 0.3
    if gender == "Female": m += 0.1
    if activity == "Low": m += 0.2
    elif activity == "High": m -= 0.1
    return m

def next_step(risk):
    return {
        "Low": "🟢 Rest, stay hydrated, and monitor for 48 hrs.",
        "Medium": "🟠 Consider clinic if symptoms persist >2 days.",
        "High": "🔴 Seek medical attention immediately."
    }[risk]

def analyze(symptoms, age, gender, activity):
    score = sum(symptom_weights[s] for s in symptoms) * get_modifier(age, gender, activity)
    if score <= 2.5:  return "✅ Mild symptoms. Monitor at home and rest.", "Low", "#d4edda"
    if score <= 6:    return "⚠️ Moderate. Consider consulting a doctor.", "Medium", "#fff3cd"
    return "🚨 Severe. Seek medical attention immediately.", "High", "#f8d7da"

if st.button("🔍 Analyze My Health"):
    if not symptoms:
        st.warning("Please select at least one symptom.")
    else:
        with st.spinner("Analyzing your input..."):
            time.sleep(1)
        text, risk, color = analyze(symptoms, age, gender, activity_level)
        suggestion = next_step(risk)

        st.markdown(f'''
        <div style="background-color:{color}; padding:15px; border-radius:10px;">
        <h4>{text}</h4>
        <p><b>Risk Level:</b> {risk}</p>
        <p><b>Next Step:</b> {suggestion}</p>
        </div>
        ''', unsafe_allow_html=True)

        st.caption(f"Personalized for age={age}, gender={gender}, activity={activity_level}")

        # -------------------- PDF GENERATION --------------------
        buffer = BytesIO()
        c = canvas.Canvas(buffer, pagesize=A4)
        w, h = A4
        c.setFont("Helvetica-Bold", 16)
        c.drawString(50, h - 50, "HealthMate Report")
        c.setFont("Helvetica", 12)
        c.drawString(50, h - 80, f"Date: {datetime.datetime.now():%Y-%m-%d %H:%M}")
        y = h - 120
        c.setFont("Helvetica-Bold", 14); c.drawString(50, y, "Basic Info:")
        c.setFont("Helvetica", 12)
        y -= 20; c.drawString(70, y, f"Age: {age}")
        y -= 15; c.drawString(70, y, f"Gender: {gender}")
        y -= 15; c.drawString(70, y, f"Activity Level: {activity_level}")
        y -= 25; c.setFont("Helvetica-Bold", 14); c.drawString(50, y, "Symptoms:")
        c.setFont("Helvetica", 12)
        for s in symptoms:
            y -= 15; c.drawString(70, y, f"- {s}")
        y -= 25; c.setFont("Helvetica-Bold", 14); c.drawString(50, y, "Assessment:")
        c.setFont("Helvetica", 12)
        y -= 20; c.drawString(70, y, text)
        y -= 15; c.drawString(70, y, f"Risk Level: {risk}")
        y -= 25; c.setFont("Helvetica-Bold", 14); c.drawString(50, y, "Next Step:")
        c.setFont("Helvetica", 12); y -= 20; c.drawString(70, y, suggestion)
        c.showPage(); c.save(); buffer.seek(0)

        st.download_button("⬇️ Download PDF Report", data=buffer,
                           file_name="healthmate_report.pdf", mime="application/pdf")

st.markdown("---")
st.markdown("<center style='color: gray'>© 2025 HealthMate | Powered by AI</center>", unsafe_allow_html=True)
