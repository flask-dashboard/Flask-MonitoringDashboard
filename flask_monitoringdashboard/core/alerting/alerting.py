from flask_monitoringdashboard.core.config import Config
from . import chat, email, issue
from .alert_content import AlertContent


def send_alert(
        exception: BaseException,
        config: Config,
        alert_url: str,
        is_user_captured: bool
):
    # Create alert content
    alert_content = AlertContent(exception, config, alert_url, is_user_captured)
    types = config.alert_type

    if 'email' in types:
        email.send_email(alert_content)
    if 'issue' in types:
        # Send Post Request to repository to create issue
        issue.create_issue(config.github_token, config.repository_owner, config.repository_name, alert_content)
    if 'chat' in types:
        chat.send_message(alert_content)
