import streamlit as st
from openai import OpenAI
import json
from datetime import datetime

# ---------------- CONFIG ----------------
st.set_page_config(page_title="Prompt Evaluator", layout="wide")
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# ---------------- STYLE ----------------
st.markdown("""
<style>
body {
    background-color:#1f1a2e;  /* slightly lighter purple for body */
    color:white;
    font-family:'Segoe UI', sans-serif;
}
.stTextArea textarea {
    background-color:#2a1f45;  /* lighter than before for readability */
    color:white;
    border-radius:10px;
    padding:10px;
    font-size:16px;
    caret-color: white;  /* <-- cursor color changed to white */
}
.stButton button {
    background: linear-gradient(90deg,#7c3aed,#c084fc);
    color:white;
    border-radius:12px;
    font-size:18px;
    padding:8px 16px;
    font-weight:bold;
}
h1,h2,h3,h4,h5,h6 {
    color:#c084fc;
    font-weight:bold;
}
.metric-container {
    background: linear-gradient(90deg,#3b2a6b,#5c3eb2);  /* brighter gradient */
    padding:20px;
    border-radius:15px;
    margin:5px 0px;
    text-align:center;
    font-size:16px;
    font-weight:bold;
    color:white;
}
.tip-box {
    background: #3b2a6b;  /* slightly lighter for better readability */
    padding:10px 15px;
    border-radius:10px;
    margin:5px 0px;
    color:white;
}
.footer {
    text-align:center;
    margin-top:20px;
    color:#ccc;
    font-size:14px;
}
.progress-chart .stPlotlyChart {
    background-color:#2a1f45;
}
</style>
""", unsafe_allow_html=True)

# ---------------- SESSION ----------------
if "attempts" not in st.session_state:
    st.session_state.attempts = []

# ---------------- TITLE ----------------
st.title("🟣 AI Prompt Evaluator")
st.write("Check your prompt, get tips, see improvements, and track your progress!")

prompt = st.text_area("Enter your prompt", height=200)

# ---------------- EVALUATION FUNCTION ----------------
def evaluate_prompt(user_prompt):
    system_prompt = """
You are a prompt engineering evaluator.

Check if prompt includes the following 10 elements:
Role, Context, Clear task, Output format, Constraints,
Structure, Examples, Tone, Completeness, Effectiveness.

Score each element 0-10.

Return JSON exactly like this:
{
"Role": 0,
"Context":0,
"ClearTask":0,
"OutputFormat":0,
"Constraints":0,
"Structure":0,
"Examples":0,
"Tone":0,
"Completeness":0,
"Effectiveness":0,
"Overall":0,
"Issues": ["list missing elements"],
"Suggestions": ["list tips"],
"ImprovedPrompt": "better version of the prompt"
}
"""
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role":"system","content":system_prompt},
            {"role":"user","content":user_prompt}
        ],
        temperature=0
    )
    return json.loads(response.choices[0].message.content)

# ---------------- BUTTON ----------------
if st.button("🚀 Evaluate Prompt"):

    if not prompt.strip():
        st.warning("Enter a prompt first")
        st.stop()

    result = evaluate_prompt(prompt)

    # ---------------- DASHBOARD ----------------
    st.subheader("📊 Score Dashboard")
    rubric_keys = ["Role","Context","ClearTask","OutputFormat","Constraints",
                   "Structure","Examples","Tone","Completeness","Effectiveness"]

    # Display in 2 rows of 5 metrics
    for i in range(0,10,5):
        cols = st.columns(5)
        for j, key in enumerate(rubric_keys[i:i+5]):
            score = result[key]
            color = "#ff4b4b" if score<4 else "#facc15" if score<7 else "#4ade80"
            cols[j].markdown(f"""
            <div class='metric-container' style='background: linear-gradient(90deg,#3b2a6b,{color});'>
            {key}<br><span style='font-size:20px'>{score}/10</span>
            </div>
            """, unsafe_allow_html=True)

    st.success(f"Overall Score: {result['Overall']}/10")

    # ---------------- ISSUES ----------------
    st.subheader("❌ What went wrong / missing")
    if len(result["Issues"]) == 0:
        st.info("✅ No issues detected. Great prompt!")
    else:
        for issue in result["Issues"]:
            st.markdown(f"<div class='tip-box'>• {issue}</div>", unsafe_allow_html=True)

    # ---------------- TIPS ----------------
    st.subheader("💡 Tips to Improve")
    for tip in result["Suggestions"]:
        st.markdown(f"<div class='tip-box'>• {tip}</div>", unsafe_allow_html=True)

    # ---------------- EXAMPLE PROMPT ----------------
    st.subheader("✨ Example Improved Prompt")
    st.code(result["ImprovedPrompt"])

    # ---------------- SAVE ATTEMPT ----------------
    st.session_state.attempts.append(result["Overall"])

    # ---------------- PROGRESS ----------------
    if len(st.session_state.attempts) > 1:
        st.markdown("### 📈 Progress Tracker")
        st.line_chart(st.session_state.attempts, use_container_width=True)

    # ---------------- TRY AGAIN ----------------
    st.info("Edit your prompt and click 'Evaluate Prompt' again to see your progress!")

    # ---------------- DOWNLOAD REPORT ----------------
    report = f"""
PROMPT EVALUATION REPORT
Date: {datetime.now()}

Prompt:
{prompt}

Scores:
{json.dumps(result, indent=2)}
"""
    st.download_button("⬇ Download Report", report, file_name="prompt_report.txt")

# ---------------- FOOTER ----------------
st.markdown("<div class='footer'>© HCL Tech</div>", unsafe_allow_html=True)
