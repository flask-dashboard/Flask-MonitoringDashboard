import requests

from flask_monitoringdashboard.core.alerting.alert_content import AlertContent

SLACK_CHAR_LIMIT = 2750
ROCKET_CHAT_CHAR_LIMIT = 4500
TEAMS_CHAR_LIMIT = 5000


def send_message(alert_content: AlertContent):
    from flask_monitoringdashboard import config

    payload_creators = {
        "SLACK": create_slack_payload,
        "ROCKET_CHAT": create_rocket_chat_payload,
        "TEAMS": create_teams_payload,
    }

    creator = payload_creators.get(config.chat_platform)
    if not creator:
        print("Invalid chat platform.")
        return

    payload = creator(alert_content)

    try:
        resp = requests.post(config.chat_webhook_url, json=payload, timeout=5)
        resp.raise_for_status()
    except Exception as e:
        print("Alert delivery failed:", e)


def create_slack_payload(alert_content: AlertContent):
    return {
        "blocks": [
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": alert_content.create_body_mrkdwn(SLACK_CHAR_LIMIT)}
            }
        ]
    }


def create_rocket_chat_payload(alert_content: AlertContent):
    return {
        "text": alert_content.create_body_markdown(ROCKET_CHAT_CHAR_LIMIT),
    }


def create_teams_payload(alert_content: AlertContent):
    return {
        "type": "message",
        "attachments": [
            {
                "contentType": "application/vnd.microsoft.card.adaptive",
                "content": {
                    "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
                    "type": "AdaptiveCard",
                    "version": "1.4",
                    "body": [
                        {
                            "type": "TextBlock",
                            "text": "Exception Alert",
                            "weight": "Bolder",
                            "size": "Large",
                            "color": "Attention"
                        },
                        {
                            "type": "FactSet",
                            "facts": [
                                {
                                    "title": "Type:",
                                    "value": f"{alert_content.exception_type}"
                                },
                                {
                                    "title": "Message:",
                                    "value": f"{alert_content.exception_message}"
                                },
                                {
                                    "title": "Timestamp:",
                                    "value": f"{alert_content.created_at_str}"
                                },
                                {
                                    "title": "Exception page:",
                                    "value": f"[{alert_content.url}]({alert_content.url})"
                                }
                            ]
                        },
                        {
                            "type": "TextBlock",
                            "text": "Stack trace:",
                            "weight": "Bolder",
                            "wrap": True
                        },
                        {
                            "type": "Container",
                            "id": "stackContainer",
                            "isVisible": True,
                            "items": [
                                {
                                    "type": "CodeBlock",
                                    "codeSnippet": f"{alert_content.get_limited_stack_trace(TEAMS_CHAR_LIMIT)}",
                                    "language": "bash",
                                    "wrap": True,
                                    "fontType": "Monospace",
                                    "targetWidth": "Standard",
                                    "fallback": {
                                        "type": "TextBlock",
                                        "text": f"{alert_content.get_limited_stack_trace(TEAMS_CHAR_LIMIT)}",
                                        "wrap": True,
                                        "fontType": "Monospace"
                                    }
                                }
                            ]
                        }
                    ]
                }
            }
        ]
    }
