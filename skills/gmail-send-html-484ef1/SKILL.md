---
name: gmail-send-html
display_name: "Gmail Send HTML"
description: "Send an HTML email via Gmail with an optional HTML file attachment"
category: communication
icon: mail
skill_type: sandbox
catalog_type: platform
requirements: "httpx>=0.25"
resource_requirements:
  - env_var: GMAIL_CREDENTIALS_JSON
    name: "Gmail Service Account JSON"
    description: "Google service account credentials JSON"
---
# Gmail Send HTML
Send a beautifully formatted HTML email with an optional standalone HTML attachment.
