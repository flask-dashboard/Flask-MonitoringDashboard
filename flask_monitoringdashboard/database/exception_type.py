from sqlalchemy.orm import Session
from flask_monitoringdashboard.database import ExceptionType

def add_exception_type(session: Session, type: str) -> int:
        type = type[:256] # To avoid error if larger than allowed in db
        exception_type = (session.query(ExceptionType)
                          .filter_by(type=type)
                          .first())
        
        if exception_type is None:
            exception_type = ExceptionType(type=type)
            session.add(exception_type)
            session.flush()
        
        return exception_type.id
