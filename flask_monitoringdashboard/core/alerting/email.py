import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from flask_monitoringdashboard.core.alerting.alert_content import AlertContent


def send_email(alert_content: AlertContent):
    from flask_monitoringdashboard import config

    message = MIMEMultipart('alternative')
    message.set_charset('utf-8')
    message['Subject'] = alert_content.title
    message['From'] = config.smtp_user
    message['To'] = ', '.join(config.smtp_to)

    message.attach(MIMEText(alert_content.create_body_text(None), 'plain', 'utf-8'))
    message.attach(MIMEText(alert_content.create_body_html(None), 'html', 'utf-8'))

    try:
        with smtplib.SMTP(config.smtp_host, int(config.smtp_port)) as smtp:
            smtp.starttls()

            if config.smtp_password:
                smtp.login(config.smtp_user, config.smtp_password)

            smtp.sendmail(config.smtp_user, config.smtp_to, message.as_string())
    except Exception as e:
        print("Error sending email alert:", e)
