import re
from datetime import date, datetime
from base64 import b64encode
from decimal import Decimal

from lxml import etree
from sqlalchemy import create_engine, text
from database_connector import DatabaseConnector


class UniversalDBConnector(DatabaseConnector):

    def __init__(self, connection_string: str):
        """Configura la conexión con el SGBD"""
        self.engine = create_engine(connection_string)

    def do_work(self, xml_request: str) -> str:
        """Procesa una solicitud XML y devuelve un resultset XML."""
        sql, parameters = self._parse_request(xml_request)
        columns, rows = self._execute_query(sql, parameters)
        return self._build_resultset(columns, rows)

    def _parse_request(self, xml_request: str) -> tuple:
        """Extrae la consulta SQL y sus parámetros del XML"""
        try:
            root = etree.fromstring(xml_request.strip().encode("utf-8"))
        except etree.XMLSyntaxError as e:
            raise ValueError(f"El documento XML no es válido: {e}")

        # Validar que la raíz sea <request> y exista <query> (RF2)
        if root.tag != "request" or not root.xpath("/request/query"):
            raise ValueError("Estructura XML inválida: se requiere <request> y <query>.")

        # Corregido: 'root' en lugar de 'rooth'
        sql = root.xpath("string(/request/query)").strip()

        # Validar que sea únicamente una sentencia SELECT (RF3)
        if not re.match(r"^SELECT\b", sql, re.IGNORECASE):
            raise ValueError("Únicamente se admiten operaciones de consulta SELECT.")
        param_nodes=root.xpath("/request/parameters/param")
        parameters = {}

        # Iteramos sobre cada etiqueta <param> dentro de <parameters>
        for param in param_nodes:
            name = param.get("name")
            param_type = param.get("type","string")
            value=(param.text or "").strip()

            if not name:
                raise ValueError("Parámetro sin nombre")
            if name in parameters:
                raise ValueError("Parámetro duplicado: {name}")
            # Conversión del valor según el atributo type (opcional pero muy recomendable)
            if param_type == "integer":
                value = int(value)
            elif param_type == "float":
                value = float(value)
            elif param_type == "decimal":
                value = Decimal(value)
            elif param_type == "boolean":
                if value.lower() not in ("true","false"):
                    raise ValueError("Valor booleano no válido")
                value=value.lower() == "true"
            elif param_type != "string":
                raise ValueError(f"Tipo de parámetro no soportado: {param_type}")
            parameters[name] = value

        return sql, parameters

    def _execute_query(self, sql: str, parameters: dict) -> tuple:
        """Ejecuta la consulta parametrizada sobre el SGBD y devuelve columnas y filas (RF3, RF5)"""
        with self.engine.connect() as conn:
            result = conn.execute(text(sql), parameters)
            columns = list(result.keys())
            rows = result.fetchall()
        return columns, rows

    def _build_resultset(self, columns: list, rows: list) -> str:
        """Construye el documento XML <resultset> a partir de los registros obtenidos (RF4)"""
        resultset = etree.Element("resultset")

        for record in rows:
            row_element=etree.SubElement(resultset, "row")
            for column, value in zip(columns, record):
                field=etree.SubElement(row_element, "field")
                if value is None:
                    field.set("null","true")
                elif isinstance(value, (datetime, date)):
                    field.text=value.isoformat()
                elif isinstance(value, Decimal):
                    field.text=str(value)
                elif isinstance(value,(bytes,bytearray)):
                    field.set("encoding","base64")
                    field.text=b64encode(value).decode("ascii")
                else:
                    field.text=str(value)
                return etree.tostring(resultset, encoding="unicode", pretty_print=True)
