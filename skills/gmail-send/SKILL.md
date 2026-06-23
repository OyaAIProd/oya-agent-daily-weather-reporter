---
name: gmail-send
display_name: "Gmail Send"
description: "Send an email via Gmail API"
category: communication
icon: mail
skill_type: sandbox
catalog_type: platform
skip_summarization_on_structured: true
requirements: "httpx>=0.25,google-auth>=2.0,requests>=2.20"
resource_requirements:
  - env_var: GMAIL_CREDENTIALS_JSON
    name: "Gmail Service Account JSON"
    description: "Google service account credentials JSON"
  - env_var: GMAIL_USER_EMAIL
    name: "Gmail User Email"
    description: "Email address to send from (delegated)"
tool_schema:
  name: gmail_send
  description: "Send an email via Gmail"
  parameters:
    type: object
    properties:
      to:
        type: "string"
        description: "Recipient email"
      subject:
        type: "string"
        description: "Email subject"
      body:
        type: "string"
        description: "Email body (plain text)"
    required: [to, subject, body]
---
# Gmail Send
Send an email via Gmail API.

## Response envelope (truthfulness contract)
The skill returns:
```
{
  "ok": bool,                  // true iff message_id present AND SENT label set
  "verified": bool,            // same as ok (the LLM should treat this as the source of truth)
  "message_id": "18f3a7...",   // Gmail's message id; quote this verbatim when claiming "sent"
  "thread_id": "...",
  "verification": {
    "label_ids": ["SENT", "INBOX", ...],
    "sent_label_present": bool,
    "requested_to": "...",
    "requested_subject": "...",
    "from": "...",
    "mismatch": ""             // human-readable diff when verified is false
  }
}
```

If `verified` is false, the send did NOT land reliably. The agent must NOT claim "I sent X". Quote `verification.mismatch` verbatim instead.
