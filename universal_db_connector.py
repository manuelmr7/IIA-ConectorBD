from sqlalchemy import create_engine

from database_connector import DatabaseConnector


class UniversalDBConnector(DatabaseConnector):

    def __init__(self, connection_string: str):
        print("Conector creado con:", connection_string)
        """Configura la conexión con el SGBD"""
        self.engine=create_engine(connection_string)

    def do_work(self, xml_request: str) -> str:
        return "<resultset/>"