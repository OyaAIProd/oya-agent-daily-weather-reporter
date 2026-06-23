import os
import sys
import json
import httpx
from base64 import urlsafe_b64encode
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication

def main():
    creds_json = os.environ.get("GMAIL_CREDENTIALS_JSON")
    if not creds_json:
        print(json.dumps({"error": "GMAIL_CREDENTIALS_JSON missing"}))
        return

    inp = json.loads(os.environ.get("INPUT_JSON", "{}"))
    to = inp.get("to")
    subject = inp.get("subject")
    html_body = inp.get("html_body")
    attachment_filename = inp.get("attachment_filename")
    attachment_content = inp.get("attachment_content")

    if not to or not subject or not html_body:
        print(json.dumps({"error": "to, subject, and html_body are required"}))
        return

    try:
        creds = json.loads(creds_json)
        r = httpx.post(
            "https://oauth2.googleapis.com/token",
            data={
                "client_id": creds["client_id"],
                "client_secret": creds["client_secret"],
                "refresh_token": creds["refresh_token"],
                "grant_type": "refresh_token",
            },
        )
        r.raise_for_status()
        token = r.json()["access_token"]
    except Exception as e:
        print(json.dumps({"error": f"Failed to get access token: {e}"}))
        return

    try:
        msg = MIMEMultipart("mixed")
        msg["To"] = to
        msg["Subject"] = subject
        
        msg_body = MIMEMultipart("alternative")
        msg_body.attach(MIMEText("Please view this email in an HTML compatible client.", "plain"))
        msg_body.attach(MIMEText(html_body, "html", "utf-8"))
        msg.attach(msg_body)
        
        if attachment_filename and attachment_content:
            part = MIMEApplication(attachment_content.encode("utf-8"), Name=attachment_filename)
            part['Content-Disposition'] = f'attachment; filename="{attachment_filename}"'
            msg.attach(part)
            with open(attachment_filename, "w", encoding="utf-8") as f:
                f.write(attachment_content)
            print(f"A2ABASEAI_FILE: {os.path.abspath(attachment_filename)}")

        raw = urlsafe_b64encode(msg.as_bytes()).decode("ascii")

        r2 = httpx.post(
            "https://gmail.googleapis.com/gmail/v1/users/me/messages/send",
            headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
            json={"raw": raw},
            timeout=15.0
        )
        r2.raise_for_status()
        print(json.dumps({"ok": True, "message_id": r2.json().get("id")}))
    except Exception as e:
        print(json.dumps({"error": f"Failed to send email: {e}"}))

if __name__ == "__main__":
    main()