import streamlit as st
import pandas as pd
from datetime import date, datetime

st.set_page_config(page_title="AWS SAA — 30 Day Tracker", layout="wide")

st.markdown("""
    <style>
        .block-container { padding-top: 3.2rem; padding-bottom: 1rem; }
        div[data-testid="stAlert"] { padding: 0.3rem 0.7rem; margin-bottom: 0; }
        div[data-testid="stAlert"] p { font-size: 0.78rem; margin: 0; }
        div.stButton > button { padding: 0.15rem 0.7rem; font-size: 0.75rem; margin-top: 4px; }
        input[aria-label="Custom Topic"] { width: 480% !important; }
        .status-notstarted div[data-baseweb="select"] > div { background: #ffd9d9 !important; border-color: #e88 !important; }
        .status-inprogress div[data-baseweb="select"] > div { background: #ffe3b8 !important; border-color: #e0a04a !important; }
        .status-done div[data-baseweb="select"] > div { background: #d3f2d3 !important; border-color: #6cbf6c !important; }
    </style>
""", unsafe_allow_html=True)

SHEET_NAME = "AWS_SAA_Tracker_Data"
WORKSHEET_NAME = "Sheet1"

TOPICS = [
    "IAM, Users, Roles, Policies, MFA",
    "EC2 Basics, AMI, EBS, Security Group",
    "Load Balancer + Auto Scaling",
    "S3 Deep Dive + Storage Classes",
    "VPC Basics, Subnets, NAT, Internet Gateway",
    "Route 53 & DNS",
    "Revision + 40 Practice Questions",
    "RDS + MultiAZ + Read Replica",
    "DynamoDB",
    "Lambda + API Gateway",
    "SQS, SNS, EventBridge",
    "ECS/EKS Basics",
    "CloudWatch + CloudTrail",
    "Revision + 40 Practice Questions",
    "Well-Architected Framework",
    "Disaster Recovery + Backup",
    "Hybrid Architecture + Migration",
    "Cost Optimization",
    "High Availability + Fault Tolerance",
    "Full Mock Test 1",
    "Analyse Mistakes + Weak Topics",
    "Full Mock Test 2",
    "Review Wrong Answers",
    "High Frequency Scenarios",
    "Serverless + Networking Revision",
    "Security + Storage Revision",
    "Full Mock Test 3",
    "Final Notes Revision",
    "Rapid Fire AWS Review",
    "Relax + Light Revision + Exam Strategy",
]

TOPIC_PLACEHOLDER = "Click to add Topic"
TOPIC_CUSTOM_OPTION = "✏️ Custom / Other (type your own)"
TOPIC_SELECT_CHOICES = [TOPIC_PLACEHOLDER] + TOPICS + [TOPIC_CUSTOM_OPTION]

ACTUAL_TOPIC_OPTIONS = [
    "", "IAM", "Users", "Roles", "Policies", "MFA", "EC2", "AMI", "EBS", "Security Groups", "Load Balancer",
    "Auto Scaling", "S3", "Storage Classes", "VPC Basics", "Subnets", "NAT", "Internet Gateway",
    "Route 53", "CloudFront", "RDS", "Multi-AZ", "Read Replica", "DynamoDB", "Lambda", "API Gateway",
    "SQS", "SNS", "EventBridge", "ECS/EKS", "CloudWatch", "CloudTrail", "Disaster Recovery", "Backup",
    "Cost Optimization", "Fault Tolerance", "High Frequency Scenarios", "Serverless", "VPC", "Others",
]

STATUS_OPTIONS = ["Not started", "In progress", "Done"]

WEEK_SUBTITLES = {
    1: "Core AWS Fundamentals",
    2: "Databases + Serverless + Integration",
    3: "Architecture + Security + Mock Practice",
    4: "Exam Conditioning + Final Revision",
    5: "Light Revision",
}

COLUMNS = ["Day", "Topic", "Neeti Status", "Shweta Status", "Neeti Date", "Shweta Date", "Notes"]


@st.cache_resource
def get_worksheet():
    """Connects to Google Sheets using service account creds stored in Streamlit secrets.
    Returns (worksheet, None) on success, (None, error_message) on failure."""
    try:
        import gspread
        from google.oauth2.service_account import Credentials

        scopes = [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive",
        ]
        creds_dict = dict(st.secrets["gcp_service_account"])
        creds = Credentials.from_service_account_info(creds_dict, scopes=scopes)
        gc = gspread.authorize(creds)
        sh = gc.open(SHEET_NAME)
        try:
            ws = sh.worksheet(WORKSHEET_NAME)
        except Exception:
            ws = sh.add_worksheet(title=WORKSHEET_NAME, rows=40, cols=10)
        return ws, None
    except Exception as e:
        return None, str(e)


def default_df():
    today = date.today().strftime("%d-%b-%y").upper()
    return pd.DataFrame({
        "Day": list(range(1, 31)),
        "Topic": [""] * 30,
        "Neeti Status": ["Not started"] * 30,
        "Shweta Status": ["Not started"] * 30,
        "Neeti Date": [today] * 30,
        "Shweta Date": [today] * 30,
        "Notes": [""] * 30,
    })


def load_data(ws):
    if ws is None:
        return default_df()
    values = ws.get_all_values()
    if not values or len(values) < 2:
        df = default_df()
        save_data(ws, df)
        return df
    header, rows = values[0], values[1:]
    df = pd.DataFrame(rows, columns=header)
    for col in COLUMNS:
        if col not in df.columns:
            df[col] = ""
    df["Day"] = df["Day"].astype(int)
    return df[COLUMNS]


def save_data(ws, df):
    if ws is None:
        return
    ws.clear()
    ws.update([df.columns.values.tolist()] + df.astype(str).values.tolist())


def parse_dmy(s):
    try:
        return datetime.strptime(s, "%d-%b-%y").date()
    except Exception:
        return date.today()


def format_dmy(d):
    return d.strftime("%d-%b-%y").upper()


ws, sync_error = get_worksheet()
sync_ok = ws is not None

if "df" not in st.session_state:
    st.session_state.df = load_data(ws)

header_col, stats_col, status_col = st.columns([1.8, 1.6, 1.6])
with header_col:
    st.markdown(
        "<div style='font-size:1.5rem; font-weight:700; color:#1a1a1a; line-height:1.2;'>AWS SAA — 30 Day Challenge</div>"
        "<div style='font-size:0.8rem; color:#666; margin-top:2px;'>Solutions Architect Associate · Daily topic tracker for Neeti &amp; Shweta</div>",
        unsafe_allow_html=True,
    )

df = st.session_state.df

with stats_col:
    stat_html = "<div style='display:flex; gap:22px; margin-top:4px;'>"
    for person, color in [("Neeti", "#FF6B6B"), ("Shweta", "#4ECDC4")]:
        done = (df[f"{person} Status"] == "Done").sum()
        pct = round(done / 30 * 100)
        stat_html += (
            f"<div style='flex:1;'>"
            f"<div style='font-size:0.75rem; color:#555;'>{person} — {done}/30 · {pct}%</div>"
            f"<div style='height:5px; background:#eee; border-radius:3px; margin-top:3px; overflow:hidden;'>"
            f"<div style='height:100%; width:{pct}%; background:{color};'></div></div>"
            f"</div>"
        )
    stat_html += "</div>"
    st.markdown(stat_html, unsafe_allow_html=True)

with status_col:
    status_inner, btn_inner = st.columns([2.4, 1])
    with status_inner:
        if sync_ok:
            st.success("✅ Connected to shared Google Sheet")
        else:
            st.warning("⚠️ Not connected — local mode")
    with btn_inner:
        st.write("")
        if st.button("🔄 Refresh"):
            st.session_state.df = load_data(ws)
            st.rerun()
    if not sync_ok:
        with st.expander("Show connection error (debug)"):
            st.code(sync_error or "No secrets found — check Secrets tab is saved.")

st.markdown("<hr style='margin:10px 0;'>", unsafe_allow_html=True)

edited_rows = []
current_week = None
for idx, row in df.iterrows():
    week_num = idx // 7 + 1
    if week_num != current_week:
        current_week = week_num
        st.markdown(f"### Week {week_num} - {WEEK_SUBTITLES.get(week_num, '')}")

    cols = st.columns([0.4, 2, 1.1, 1.1, 1, 1, 3])
    cols[0].write(f"**{row['Day']}**")
    with cols[1]:
        current_topic = row["Topic"]
        if current_topic in TOPICS:
            default_choice = current_topic
        elif current_topic == "":
            default_choice = TOPIC_PLACEHOLDER
        else:
            default_choice = TOPIC_CUSTOM_OPTION
        choice = st.selectbox("Topic", TOPIC_SELECT_CHOICES, index=TOPIC_SELECT_CHOICES.index(default_choice), key=f"topicsel_{idx}", label_visibility="collapsed")
        if choice == TOPIC_CUSTOM_OPTION:
            custom_default = current_topic if default_choice == TOPIC_CUSTOM_OPTION else ""
            topic = st.text_input("Custom Topic", value=custom_default, key=f"topictxt_{idx}", label_visibility="collapsed", placeholder="Type topic…")
        elif choice == TOPIC_PLACEHOLDER:
            topic = ""
        else:
            topic = choice
    status_class = {"Not started": "status-notstarted", "In progress": "status-inprogress", "Done": "status-done"}
    neeti_cls = status_class.get(row["Neeti Status"], "status-notstarted")
    shweta_cls = status_class.get(row["Shweta Status"], "status-notstarted")
    with cols[2]:
        st.markdown(f"<div class='{neeti_cls}'>", unsafe_allow_html=True)
        neeti = st.selectbox("Neeti", STATUS_OPTIONS, index=STATUS_OPTIONS.index(row["Neeti Status"]) if row["Neeti Status"] in STATUS_OPTIONS else 0, key=f"neeti_{idx}", label_visibility="collapsed")
        st.markdown("</div>", unsafe_allow_html=True)
    with cols[3]:
        st.markdown(f"<div class='{shweta_cls}'>", unsafe_allow_html=True)
        shweta = st.selectbox("Shweta", STATUS_OPTIONS, index=STATUS_OPTIONS.index(row["Shweta Status"]) if row["Shweta Status"] in STATUS_OPTIONS else 0, key=f"shweta_{idx}", label_visibility="collapsed")
        st.markdown("</div>", unsafe_allow_html=True)
    neeti_date_val = cols[4].date_input("N.Date", value=parse_dmy(row["Neeti Date"]), key=f"ndate_{idx}", label_visibility="collapsed", format="DD-MM-YYYY")
    shweta_date_val = cols[5].date_input("S.Date", value=parse_dmy(row["Shweta Date"]), key=f"sdate_{idx}", label_visibility="collapsed", format="DD-MM-YYYY")
    neeti_date = format_dmy(neeti_date_val)
    shweta_date = format_dmy(shweta_date_val)
    notes = cols[6].text_input("Notes", value=row["Notes"], key=f"notes_{idx}", label_visibility="collapsed")

    edited_rows.append({
        "Day": row["Day"], "Topic": topic,
        "Neeti Status": neeti, "Shweta Status": shweta,
        "Neeti Date": neeti_date, "Shweta Date": shweta_date, "Notes": notes,
    })

    st.markdown("<hr style='margin:4px 0; border:none; border-top:1px solid #bbb;'>", unsafe_allow_html=True)

new_df = pd.DataFrame(edited_rows)
if not new_df.equals(df):
    st.session_state.df = new_df
    save_data(ws, new_df)
    st.rerun()
