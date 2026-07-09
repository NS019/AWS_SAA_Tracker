import streamlit as st
import pandas as pd
from datetime import date

st.set_page_config(page_title="AWS SAA — 30 Day Tracker", layout="wide")

SHEET_NAME = "AWS_SAA_Tracker_Data"
WORKSHEET_NAME = "Sheet1"

TOPICS = [
    "IAM basics & shared responsibility", "S3 fundamentals & storage classes", "S3 advanced (lifecycle, replication)",
    "EC2 fundamentals", "EC2 pricing & purchasing options", "EBS & instance storage",
    "VPC fundamentals", "VPC advanced (peering, endpoints)", "Route 53 & DNS",
    "ELB & Auto Scaling Groups", "RDS fundamentals", "Aurora & DynamoDB",
    "ElastiCache", "Lambda & Serverless basics", "API Gateway",
    "SQS, SNS, EventBridge", "Step Functions", "CloudFront & Global Accelerator",
    "ECS, EKS, Fargate", "CloudFormation basics", "Well-Architected Framework",
    "Security: KMS, Secrets Manager", "Security: WAF, Shield, GuardDuty", "Monitoring: CloudWatch, CloudTrail",
    "Migration & Transfer services", "Disaster recovery strategies", "Cost optimization strategies",
    "Advanced networking review", "Practice exam #1 review", "Practice exam #2 + final review",
]

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

COLUMNS = ["Day", "Topic", "Actual Topic Done", "Neeti Status", "Shweta Status", "Neeti Date", "Shweta Date", "Notes"]


@st.cache_resource
def get_worksheet():
    """Connects to Google Sheets using service account creds stored in Streamlit secrets.
    Returns (worksheet, None) on success, (None, error_message) on failure."""
    try:
        import gspread
        from google.oauth2.service_account import Credentials

        scopes = ["https://www.googleapis.com/auth/spreadsheets"]
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
        "Topic": [TOPICS[i] if i < len(TOPICS) else "" for i in range(30)],
        "Actual Topic Done": [""] * 30,
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


ws, sync_error = get_worksheet()
sync_ok = ws is not None

st.title("AWS SAA — 30 Day Challenge")
st.caption("Solutions Architect Associate · Daily topic tracker for Neeti & Shweta")

if sync_ok:
    st.success("✅ Connected to shared Google Sheet — both of you see the same live data.")
else:
    st.warning("⚠️ Not connected to Google Sheets yet — running in local/session mode (see README to enable shared sync).")
    with st.expander("Show connection error (for debugging)"):
        st.code(sync_error or "No secrets found — check Secrets tab is saved.")

if "df" not in st.session_state:
    st.session_state.df = load_data(ws)

if st.button("🔄 Refresh (pull latest from Shweta/Neeti)"):
    st.session_state.df = load_data(ws)
    st.rerun()

df = st.session_state.df

col1, col2 = st.columns(2)
for col, person in zip([col1, col2], ["Neeti", "Shweta"]):
    done = (df[f"{person} Status"] == "Done").sum()
    pct = round(done / 30 * 100)
    with col:
        st.metric(f"{person}", f"{done}/30 done", f"{pct}%")
        st.progress(pct / 100)

st.divider()

edited_rows = []
current_week = None
for idx, row in df.iterrows():
    week_num = idx // 7 + 1
    if week_num != current_week:
        current_week = week_num
        st.markdown(f"### Week {week_num} - {WEEK_SUBTITLES.get(week_num, '')}")

    cols = st.columns([0.4, 2, 1.6, 1.1, 1.1, 1, 1, 1.6])
    cols[0].write(f"**{row['Day']}**")
    topic = cols[1].text_input("Topic", value=row["Topic"], key=f"topic_{idx}", label_visibility="collapsed")
    actual = cols[2].selectbox("Actual", ACTUAL_TOPIC_OPTIONS, index=ACTUAL_TOPIC_OPTIONS.index(row["Actual Topic Done"]) if row["Actual Topic Done"] in ACTUAL_TOPIC_OPTIONS else 0, key=f"actual_{idx}", label_visibility="collapsed")
    neeti = cols[3].selectbox("Neeti", STATUS_OPTIONS, index=STATUS_OPTIONS.index(row["Neeti Status"]) if row["Neeti Status"] in STATUS_OPTIONS else 0, key=f"neeti_{idx}", label_visibility="collapsed")
    shweta = cols[4].selectbox("Shweta", STATUS_OPTIONS, index=STATUS_OPTIONS.index(row["Shweta Status"]) if row["Shweta Status"] in STATUS_OPTIONS else 0, key=f"shweta_{idx}", label_visibility="collapsed")
    neeti_date = cols[5].text_input("N.Date", value=row["Neeti Date"], key=f"ndate_{idx}", label_visibility="collapsed")
    shweta_date = cols[6].text_input("S.Date", value=row["Shweta Date"], key=f"sdate_{idx}", label_visibility="collapsed")
    notes = cols[7].text_input("Notes", value=row["Notes"], key=f"notes_{idx}", label_visibility="collapsed")

    edited_rows.append({
        "Day": row["Day"], "Topic": topic, "Actual Topic Done": actual,
        "Neeti Status": neeti, "Shweta Status": shweta,
        "Neeti Date": neeti_date, "Shweta Date": shweta_date, "Notes": notes,
    })

new_df = pd.DataFrame(edited_rows)
if not new_df.equals(df):
    st.session_state.df = new_df
    save_data(ws, new_df)
    st.rerun()
