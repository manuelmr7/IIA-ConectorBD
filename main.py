from sqlalchemy import create_engine, text
from universal_db_connector import UniversalDBConnector

# -------------------------------------------------
# Configuración de las bases de datos
# -------------------------------------------------
SQLITE_URL = "sqlite:///clientes.db"

# Adaptar usuario, contraseña y base de datos
# a la instalación local de PostgreSQL.
POSTGRESQL_URL = (
    "postgresql+psycopg://alumno:clave123@localhost:5432/empresa"
)


# -------------------------------------------------
# Preparación de las bases de datos
# -------------------------------------------------
def prepare_database(connection_string: str):
    engine = create_engine(connection_string)
    try:
        with engine.begin() as conn:
            # Crear la tabla si no existe
            conn.execute(text("""
                              CREATE TABLE IF NOT EXISTS clientes
                              (
                                  id
                                  INTEGER
                                  PRIMARY
                                  KEY,
                                  nombre
                                  VARCHAR
                              (
                                  100
                              ),
                                  email VARCHAR
                              (
                                  150
                              ),
                                  provincia VARCHAR
                              (
                                  100
                              )
                                  )
                              """))

            # Eliminar registros anteriores
            conn.execute(text("DELETE FROM clientes"))

            # Insertar los datos de prueba
            conn.execute(
                text("""
                     INSERT INTO clientes
                         (id, nombre, email, provincia)
                     VALUES (:id, :nombre, :email, :provincia)
                     """),
                [
                    {
                        "id": 1,
                        "nombre": "Juan García",
                        "email": "juan@empresa.es",
                        "provincia": "Sevilla"
                    },
                    {
                        "id": 2,
                        "nombre": "Ana López",
                        "email": "ana@empresa.es",
                        "provincia": "Sevilla"
                    },
                    {
                        "id": 3,
                        "nombre": "Pedro Ruiz",
                        "email": None,
                        "provincia": "Cádiz"
                    }
                ]
            )
    finally:
        engine.dispose()


# -------------------------------------------------
# Preparación inicial
# -------------------------------------------------
# SQLite: necesaria para las pruebas P1-P5
prepare_database(SQLITE_URL)

# PostgreSQL: descomentar para realizar la prueba P6.
# Antes, crear la base de datos y configurar POSTGRESQL_URL.
# prepare_database(POSTGRESQL_URL)

# -------------------------------------------------
# Creación del conector SQLite
# -------------------------------------------------
conector = UniversalDBConnector(SQLITE_URL)

# -------------------------------------------------
# P1. Consulta SELECT sin parámetros
# -------------------------------------------------
xml1 = """
<request>
    <query>
        SELECT id, nombre FROM clientes
    </query>
</request>
"""

print("PRUEBA P1")
print(conector.do_work(xml1))

# -------------------------------------------------
# P2. Consulta SELECT con parámetros
# -------------------------------------------------
xml2 = """
<request>
    <query>
        SELECT id, nombre, email
        FROM clientes
        WHERE provincia = :provincia
    </query>
    <parameters>
        <param name="provincia" type="string">Sevilla</param>
    </parameters>
</request>
"""

print("PRUEBA P2")
print(conector.do_work(xml2))

# -------------------------------------------------
# P3. Consulta que devuelve varios registros
# -------------------------------------------------
xml3 = """
<request>
    <query>
        SELECT id, nombre, provincia
        FROM clientes
        ORDER BY id
    </query>
</request>
"""

print("PRUEBA P3")
print(conector.do_work(xml3))

# -------------------------------------------------
# P4. Consulta sin resultados
# -------------------------------------------------
xml4 = """
<request>
    <query>
        SELECT id, nombre
        FROM clientes
        WHERE provincia = 'Madrid'
    </query>
</request>
"""

print("PRUEBA P4")
print(conector.do_work(xml4))

# -------------------------------------------------
# P5. Consulta con valores NULL
# -------------------------------------------------
xml5 = """
<request>
    <query>
        SELECT id, nombre, email
        FROM clientes
        WHERE id = 3
    </query>
</request>
"""

print("PRUEBA P5")
print(conector.do_work(xml5))

# -------------------------------------------------
# P6. Ejecución sobre PostgreSQL
# -------------------------------------------------
# Descomentar para realizar la prueba P6,
# una vez configurada y preparada la base PostgreSQL.
# conector2 = UniversalDBConnector(POSTGRESQL_URL)
#
# print("PRUEBA P6 - PostgreSQL")
# print(conector2.do_work(xml2))
