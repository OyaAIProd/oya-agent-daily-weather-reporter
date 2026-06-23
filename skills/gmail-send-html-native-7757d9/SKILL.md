---
name: gmail-send-html-native
display_name: "Gmail Send HTML"
description: "Send an HTML email via Gmail API"
category: communication
icon: mail
skill_type: sandbox
catalog_type: platform
requirements: "httpx>=0.25,google-auth>=2.0,requests>=2.20"
resource_requirements:
  - env_var: GMAIL_CREDENTIALS_JSON
    name: "Gmail Service Account JSON"
    description: "Google service account credentials JSON"
  - env_var: GMAIL_USER_EMAIL
    name: "Gmail User Email"
    description: "Email address to send from (delegated)"
---
# Gmail Send HTML Native
Send an email via Gmail API using HTML.
