# AWS SAA Tracker — Shared Live Version (Neeti + Shweta)

Yeh guide follow karo — step by step. End mein tumhe ek shareable link milega jo dono
(Neeti & Shweta) use kar sakte ho, aur data dono ke liye same/live rahega.

## STEP 1 — GitHub par code daalo
1. https://github.com par account banao (agar nahi hai).
2. New repository banao — naam kuch bhi, e.g. `aws-saa-tracker`.
3. Is `python_app` folder ke andar ke 3 files (`streamlit_app.py`, `requirements.txt`, ye README)
   us repo mein upload kar do (GitHub web par "Add file" → "Upload files" se bhi ho jayega, no coding needed).

## STEP 2 — Google Sheet banao (shared database)
1. https://sheets.google.com par jaake ek naya spreadsheet banao.
2. Naam rakho exactly: `AWS_SAA_Tracker_Data`
3. Isse abhi khali hi rehne do — app khud header + 30 din bhar dega.

## STEP 3 — Google Cloud "Service Account" banao (ye Google Sheet ko app se connect karega)
1. https://console.cloud.google.com par jao → naya project banao (koi bhi naam).
2. Left menu → "APIs & Services" → "Library" → search karo **"Google Sheets API"** → Enable karo.
   Same tarah **"Google Drive API"** bhi enable karo.
3. Left menu → "APIs & Services" → "Credentials" → "Create Credentials" → **"Service Account"**.
   Koi bhi naam do, Create dabao, phir "Done".
4. Us service account par click karo → "Keys" tab → "Add Key" → "Create new key" → **JSON** select karke Create.
   Ek `.json` file download hogi — isse sambhal ke rakho, iske andar secret credentials hain.
5. Us JSON file ko kholo, usme ek email milega jaisa:
   `xxxxx@xxxxx.iam.gserviceaccount.com`
6. Wapas apni Google Sheet (`AWS_SAA_Tracker_Data`) mein jao → "Share" button dabao →
   Us email ko **Editor** access do, share kar do.

## STEP 4 — Streamlit Cloud par deploy karo
1. https://streamlit.io/cloud par jao, "Sign in with GitHub" karo.
2. "New app" → apna repo select karo → main file path: `streamlit_app.py` → "Deploy".
3. App deploy hote hi ek public URL milega jaisa: `https://your-app.streamlit.app`
   — **yehi tumhara shareable link hai jo Neeti/Shweta dono use karenge.**

## STEP 5 — App ko Google Sheet se connect karo (secrets)
1. Deployed app ke "Settings" (3 dots menu) → "Secrets" mein jao.
2. Apni downloaded JSON file kholo, aur is format mein paste karo (values apni file se copy karo):

```
[gcp_service_account]
type = "service_account"
project_id = "..."
private_key_id = "..."
private_key = "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n"
client_email = "xxxxx@xxxxx.iam.gserviceaccount.com"
client_id = "..."
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"
auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
client_x509_cert_url = "..."
```
(Yeh saari values tumhari downloaded `.json` file mein already hain — bas copy-paste karo.)

3. Save karo — app apne aap restart hoke Google Sheet se connect ho jayega.
4. Top par green message dikhega: "✅ Connected to shared Google Sheet".

## Ab kaise use karein
- Ye link Neeti aur Shweta dono ko bhej do: `https://your-app.streamlit.app`
- Dono apna status/date/notes edit kar sakte hain — data Google Sheet mein save hota hai,
  isliye dono ko same data dikhega (refresh button dabao latest dekhne ke liye).
- Data kabhi delete nahi hoga (Google Sheet mein permanently save hai), app redeploy hone
  par bhi safe rahega.

Agar kisi step mein atko, mujhe batao — main us step ko aur detail mein samjha dunga.
