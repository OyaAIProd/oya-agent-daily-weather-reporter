import os, json, base64, time, httpx
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication

try:
    from google.oauth2 import credentials, service_account
    from google.auth.transport.requests import Request as AuthRequest
except ImportError:
    print(json.dumps({"error": "google-auth not installed. pip install google-auth"}))
    raise SystemExit(1)
try:
    inp = json.loads(os.environ.get("INPUT_JSON", "{}"))
    creds_json = json.loads(os.environ["GMAIL_CREDENTIALS_JSON"])
    user_email = os.environ.get("GMAIL_USER_EMAIL", "")
    
    if creds_json.get("type") == "authorized_user":
        creds = credentials.Credentials.from_authorized_user_info(
            creds_json, scopes=["https://www.googleapis.com/auth/gmail.send"]
        )
    else:
        creds = service_account.Credentials.from_service_account_info(
            creds_json, scopes=["https://www.googleapis.com/auth/gmail.send"], subject=user_email
        )
    creds.refresh(AuthRequest())
    
    requested_to = inp["to"]
    requested_subject = inp["subject"]
    html_body = inp["html_body"]
    
    msg = MIMEMultipart("mixed")
    msg["to"] = requested_to
    msg["subject"] = requested_subject
    msg["from"] = user_email
    
    msg_body = MIMEMultipart("alternative")
    msg_body.attach(MIMEText("Please view this email in an HTML compatible client.", "plain"))
    msg_body.attach(MIMEText(html_body, "html", "utf-8"))
    msg.attach(msg_body)
    
    attachment_filename = inp.get("attachment_filename")
    attachment_content = inp.get("attachment_content")
    if attachment_filename and attachment_content:
        part = MIMEApplication(attachment_content.encode("utf-8"), Name=attachment_filename)
        part['Content-Disposition'] = f'attachment; filename="{attachment_filename}"'
        msg.attach(part)
        with open(attachment_filename, "w", encoding="utf-8") as f:
            f.write(attachment_content)
        print(f"A2ABASEAI_FILE: {os.path.abspath(attachment_filename)}")

    raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()
    response_json = None
    for _attempt in range(4):
        with httpx.Client(timeout=15) as c:
            r = c.post(f"https://gmail.googleapis.com/gmail/v1/users/me/messages/send",
                headers={"Authorization": f"Bearer {creds.token}", "Content-Type": "application/json"},
                json={"raw": raw})
        if r.status_code == 429 and _attempt < 3:
            time.sleep(min(2 ** _attempt, 30))
            continue
        r.raise_for_status()
        response_json = r.json()
        break

    message_id = (response_json or {}).get("id", "")
    thread_id = (response_json or {}).get("threadId", "")
    label_ids = (response_json or {}).get("labelIds", []) or []
    sent_label_present = "SENT" in label_ids
    
    out = {
        "ok": bool(message_id) and sent_label_present,
        "verified": bool(message_id) and sent_label_present,
        "message_id": message_id,
        "thread_id": thread_id
    }
    print(json.dumps(out))
except Exception as e:
    print(json.dumps({"error": str(e)}))
