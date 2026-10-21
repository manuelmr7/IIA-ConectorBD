import re
from sqlalchemy import create_engine
from datetime import date, datetime
from base64 import b64encode
from lxml import etree

from sqlalchemy.orm import create_engine, text
from database_connector import DatabaseConnector


class UniversalDBConnector(DatabaseConnector):

    def __init__(self, connection_string: str):
        print("Conector creado con:", connection_string)
        """Configura la conexión con el SGBD"""
        self.engine=create_engine(connection_string)

    def do_work(self, xml_request: str) -> str:
        """Procesa una solicitud XML y devuelve un resultset XML."""
        sql,parameters = self._parse_request(xml_request)
        columns,rows=self._execute_query(sql,parameters)
        return self._build_resultset(columns,rows)
