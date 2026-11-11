
import os
import cx_Oracle
from dotenv import load_dotenv

# Leer las variables privadas del archivo .env
load_dotenv()

# Inicializar Oracle Instant Client
ruta_cliente = os.getenv("ORACLE_CLIENT_LIB")

if ruta_cliente:
    cx_Oracle.init_oracle_client(lib_dir=ruta_cliente)


def obtener_conexion():
    conexion = cx_Oracle.connect(
        user=os.getenv("ORACLE_USER"),
        password=os.getenv("ORACLE_PASSWORD"),
        dsn=os.getenv("ORACLE_DSN")
    )

    return conexion

