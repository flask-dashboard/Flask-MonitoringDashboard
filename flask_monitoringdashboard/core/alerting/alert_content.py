import importlib.resources
import os
import traceback
from datetime import datetime

from jinja2 import Environment, FileSystemLoader

import flask_monitoringdashboard
from flask_monitoringdashboard.core.config import Config

template_root = os.path.join(importlib.resources.files(flask_monitoringdashboard).__str__(), 'templates', 'alert')
template_env = Environment(loader=FileSystemLoader(template_root))
template = template_env.get_template('report.html')


class AlertContent:
    """
    Central data object for exception alerting.

    This class is instantiated once for every uncaught and user-captured
    exception and acts as a shared container between all alerting types
    (email, chat platforms, issue creation). It extracts relevant information
    from the exception and configuration, such as timestamps, stack traces,
    and metadata, and exposes helper methods to render this data in different
    output formats.

    Alert senders should not inspect or format exception data themselves.
    Instead, they receive an AlertContent instance and call the appropriate
    `create_body_*` methods to generate channel-specific payloads while
    respecting platform-specific character limits.
    """

    def __init__(self, exception: BaseException, config: Config, url: str, is_user_captured: bool):
        self._exception = exception

        self.created_at = datetime.now(config.timezone)
        self.created_at_str = self.created_at.strftime('%Y-%m-%d %H:%M:%S')
        self.send_at = None  # When was the alert sent, None if not sent yet

        self.exception_type = exception.__class__.__name__
        self.exception_message = exception.__str__()

        self.is_user_captured = is_user_captured
        self.title = self._create_title()
        self.stack_trace = ''.join(traceback.format_exception(type(exception), exception, exception.__traceback__))

        self.url = url

    def _create_title(self) -> str:
        exception_type = "User-captured" if self.is_user_captured else "Uncaught"
        return f"[{self.exception_type}] {exception_type} exception at {self.created_at_str}"

    def get_limited_stack_trace(self, char_limit: int | None) -> str:
        if not char_limit:
            return self.stack_trace
        return self.stack_trace[:char_limit] + ('...' if len(self.stack_trace) > char_limit else '')

    def create_body_text(self, char_limit: int | None) -> str:
        return (
            f"An exception of type {self.exception_type} occurred.\n\n"
            f"Message: {self.exception_message}\n\n"
            f"You can see the full exception page here: {self.url}\n\n"
            f"Stack trace: {self.get_limited_stack_trace(char_limit)}"
        )

    def create_body_markdown(self, char_limit: int | None) -> str:
        return (
            f"**Type:** `{self.exception_type}`\n"
            f"**Message:** `{self.exception_message}`\n"
            f"**Timestamp:** `{self.created_at_str}`\n"
            f"**Exception page:** [{self.url}]({self.url})\n"
            f"**Stack trace:**\n```\n{self.get_limited_stack_trace(char_limit)}\n```"
        )

    def create_body_mrkdwn(self, char_limit: int | None) -> str:
        return (
            f"*Type:* `{self.exception_type}`\n"
            f"*Message:* `{self.exception_message}`\n"
            f"*Timestamp:* `{self.created_at_str}`\n"
            f"*Exception page:* {self.url}\n"
            f"*Stack trace:*\n```\n{self.get_limited_stack_trace(char_limit)}\n```"
        )

    def create_body_html(self, char_limit: int | None) -> str:
        return template.render(
            exc_type=self.exception_type,
            exc_message=self.exception_message,
            timestamp=self.created_at_str,
            url=self.url,
            stacktrace=self.get_limited_stack_trace(char_limit)
        )
