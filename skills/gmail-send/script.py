import os, json, base64, time, httpx
from email.mime.text import MIMEText
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
    msg = MIMEText(inp["body"])
    msg["to"] = requested_to
    msg["subject"] = requested_subject
    msg["from"] = user_email
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

    # Auto-verify against the send response itself. Gmail's API returns the
    # full Message resource on success, including `labelIds` — if SENT is in
    # there, the message landed in the user's Sent folder. The wrapper LLM
    # cannot claim "sent" if verified is false.
    message_id = (response_json or {}).get("id", "")
    thread_id = (response_json or {}).get("threadId", "")
    label_ids = (response_json or {}).get("labelIds", []) or []
    sent_label_present = "SENT" in label_ids
    mismatches = []
    if not message_id:
        mismatches.append("no message_id returned from Gmail API")
    if not sent_label_present:
        mismatches.append(f"SENT label missing from response (got: {label_ids})")
    out = {
        "ok": bool(message_id) and sent_label_present,
        "verified": bool(message_id) and sent_label_present,
        "message_id": message_id,
        "thread_id": thread_id,
        "verification": {
            "label_ids": label_ids,
            "sent_label_present": sent_label_present,
            "requested_to": requested_to,
            "requested_subject": requested_subject,
            "from": user_email,
            "mismatch": "; ".join(mismatches) if mismatches else "",
        },
    }
    print(json.dumps(out))
except Exception as e:
    print(json.dumps({"error": str(e)}))
