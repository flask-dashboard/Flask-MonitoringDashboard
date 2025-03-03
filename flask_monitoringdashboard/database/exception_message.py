
from flask_monitoringdashboard.database import ExceptionMessage

def add_exception_message(session, message) -> int:
        exception_message = (session.query(ExceptionMessage)
                             .filter_by(message=message)
                             .first())
        
        if exception_message is None:
            exception_message = ExceptionMessage(message=message)
            session.add(exception_message)
            session.flush()
        
        return exception_message.id
