from typing import Union
from flask import Request
from sqlalchemy.sql.expression import ColumnExpressionArgument

from flask_monitoringdashboard.database import Endpoint, ExceptionMessage, ExceptionType


class ExceptionFilter():
    def __init__(self, req: Request):
        self.messageFilter: str = req.args.get("message", "", str)
        self.typeFilter: str = req.args.get("type", "", str)
        self.endpointFilter: str = req.args.get("endpoint", "", str)
        self.genericSearch: Union[str, None] = req.args.get("genericSearch")

    def get_filter(self) -> ColumnExpressionArgument[bool]:
        if self.genericSearch is not None:
            return ExceptionType.type.contains(self.genericSearch)|\
                ExceptionMessage.message.contains(self.genericSearch)|\
                Endpoint.name.contains(self.genericSearch)

        return ExceptionType.type.contains(self.typeFilter)&\
                ExceptionMessage.message.contains(self.messageFilter)&\
                Endpoint.name.contains(self.endpointFilter)
        
