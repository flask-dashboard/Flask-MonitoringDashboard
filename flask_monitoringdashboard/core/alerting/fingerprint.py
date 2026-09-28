from types import TracebackType
from typing import Union

from flask_monitoringdashboard.core.exceptions.text_hash import text_hash


def alert_fingerprint(exc: BaseException, tb: Union[TracebackType, None]) -> str:
    """
    Identifies an exception for alerting: its type plus the file and function name of every frame.

    Deliberately coarser than hash_stack_trace, which also hashes the message, the line numbers
    and the source of every function. With those, an error whose message contains an id
    ("user 123 not found") would alert on every occurrence, and every deploy that edits a function
    in a known stack trace would alert again.
    """
    parts = [type(exc).__module__ + "." + type(exc).__qualname__]
    while tb:
        code = tb.tb_frame.f_code
        parts.append(code.co_filename + ":" + code.co_name)
        tb = tb.tb_next
    return text_hash("\n".join(parts))
