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
    background-color:#1f1a2e;  
    color:white;
    font-family:'Segoe UI', sans-serif;
}
.stTextArea textarea {
    background-color:#2a1f45;  
    color:white;
    border-radius:10px;
    padding:10px;
    font-size:16px;
    caret-color: white;  /* cursor color white */
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
    background: linear-gradient(90deg,#3b2a6b,#5c3eb2);  
    padding:20px;
    border-radius:15px;
    margin:5px 0px;
    text-align:center;
    font-size:16px;
    font-weight:bold;
    color:white;
}
.tip-box {
    background: #3b2a6b;  
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

# ---------------- SIDEBAR ----------------
st.sidebar.title("Activities")

# Dictionary of all activities and their questions
activity_questions = {
    "Banking Operations": "You are part of a banking operations team. Explain how an end-to-end transaction is processed, starting from customer initiation to final settlement, including key checkpoints.",
    "IT Service Management": "As an IT operations analyst, list common operational errors that occur during system deployments and suggest corrective actions for each.",
    "Business Operations": "You are launching a new back-office operations process. Create a detailed Standard Operating Procedure (SOP) covering roles, steps, controls, and escalation paths.",
    "Incident Management": "You are handling a critical production incident. Summarize a detailed incident report into a concise update suitable for senior management.",
    "Operations Analytics": "You have been given turnaround time data for multiple process stages. Analyze the data and identify bottlenecks affecting overall efficiency.",
    "Process Automation": "As an operations transformation consultant, identify areas within an operations workflow where automation can reduce manual effort and improve accuracy.",
    "High-Volume Operations": "Simulate a scenario where transaction volumes spike unexpectedly. Describe how the operations team should respond to ensure continuity and minimize impact.",
    "Healthcare Administration": "You work in hospital administration. Explain the end-to-end patient admission and discharge process, highlighting compliance and documentation steps.",
    "Supply Chain & Logistics": "Identify common operational issues in warehouse management and recommend solutions to improve order fulfillment accuracy.",
    "Retail Operations": "Analyze a retail store’s daily operations and suggest process improvements to reduce customer wait times and inventory mismatches.",
    "Human Resources Operations": "Explain the end-to-end employee onboarding process and identify areas where delays typically occur.",
    "Manufacturing Operations": "List common production floor operational failures and propose preventive controls to minimize downtime.",
    "FinTech Operations": "Explain how a digital payment transaction is validated, authorized, and settled across multiple systems.",
    "Customer Support Operations": "Summarize a high-priority customer complaint escalation report for leadership review.",
    "Quality & Compliance": "Identify operational compliance risks in a regulated environment and suggest mitigation strategies.",
    "Data Operations": "Analyze operational data latency issues and identify root causes affecting reporting timelines.",
    "Telecom Operations": "Explain the process flow of a service outage resolution from detection to closure.",
    "E-Commerce Operations": "Identify bottlenecks in order processing during peak sales periods and recommend corrective actions.",
    "Insurance Operations": "Explain the end-to-end insurance claims processing workflow and common failure points.",
    "Facilities Operations": "Describe how facility maintenance requests are processed and suggest ways to improve turnaround time.",
    "Cybersecurity Operations": "Summarize a security incident report into key risks and actions for non-technical stakeholders.",
    "Procurement Operations": "Explain the purchase-to-pay (P2P) process and identify inefficiencies that impact cost control.",
    "Airline Operations": "Simulate a flight disruption scenario and outline the operational response required to manage passengers effectively.",
    "Energy & Utilities": "Identify operational challenges in meter reading and billing processes and propose automation solutions.",
    "Shared Services": "Explain how shared services handle multi-region operations while maintaining SLA compliance.",
    "Project Operations": "Analyze delays in project execution and identify operational constraints affecting delivery timelines.",
    "Education Operations": "Explain how student enrollment and examination processes are managed end-to-end.",
    "Hospitality Operations": "Identify operational gaps in hotel check-in/check-out processes and suggest improvements.",
    "Legal Operations": "Summarize a case handling workflow and identify operational risks related to documentation and deadlines.",
    "Enterprise Operations": "Assess enterprise-wide operational dependencies and identify critical points of failure."
}

selected_activity = st.sidebar.selectbox("Select an activity", list(activity_questions.keys()))

# ---------------- MAIN AREA ----------------
st.title(f"🟣 {selected_activity} - Prompt Evaluator")

# Show the question for the selected activity
st.subheader("📝 Question")
st.info(activity_questions[selected_activity])

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
