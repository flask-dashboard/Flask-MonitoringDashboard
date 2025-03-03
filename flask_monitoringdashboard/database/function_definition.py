from sqlalchemy.orm import Session
from flask_monitoringdashboard.database import CodeLine, ExceptionStackLine, FunctionDefinition


def add_function_definition(session : Session, f_def: FunctionDefinition) -> int:
    """
    Adds a FunctionDefinition to the database if it does not already exist.
    :param session: Session for the database
    :param f_def: The FunctionDefinition object to be added
    :return: The ID of the existing or newly added FunctionDefinition.
    """
    result : FunctionDefinition | None = (session.query(FunctionDefinition)
            .filter(FunctionDefinition.function_hash == f_def.function_hash)
            .first())
    if result is not None:
        return result.id
    else:
        session.add(f_def)
        session.flush()
        return f_def.id

def get_function_definition_from_id(session: Session, function_id: int) -> FunctionDefinition | None:
    return (session.query(FunctionDefinition)
            .filter(FunctionDefinition.id == function_id)
            .first())

def get_function_startlineno_and_relativelineno_from_function_definition_id(session : Session, function_defintion_id : int, full_stack_trace_id : int) -> tuple[int, int] | None:
    """
    Retrieves the starting line number of a function and the relative line number of an exception 
    from the ExceptionStackLine table.

    :param session: session for the database
    :param function_definition_id: id of the function
    :param full_stack_trace_id: id of the stack trace
    :return: A tuple containing:
            - (int) The absolute starting line number of the function in the source file.
            - (int) The relative line number of the exception within the function.
            Returns None if no matching data is found.
    """
    result : ExceptionStackLine | None = (session.query(ExceptionStackLine)
                    .filter(ExceptionStackLine.function_definition_id == function_defintion_id)
                    .filter(ExceptionStackLine.full_stack_trace_id == full_stack_trace_id)
                    .first())
    if result is not None and isinstance(result.code, CodeLine):
        return result.code.line_number, result.relative_line_number
    else:
        return None


