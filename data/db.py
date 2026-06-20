"""
data/db.py
----------
Capa de acceso a datos: conexión de SOLO LECTURA a SQL Server donde vive la
base de datos de SAP B1.

Importante sobre seguridad:
El usuario SQL que se usa aquí (SQL_USER_* en el .env) debe ser un usuario de
aplicación creado especialmente para este dashboard, con permisos únicamente
de SELECT — idealmente sobre vistas (CREATE VIEW) en lugar de las tablas
directas, para no exponer columnas sensibles ni depender de la estructura
interna de SAP si cambia en una actualización. NO es el usuario personal de
cada quien: la identidad de cada persona ya se valida aparte en
auth/sap_auth.py contra el Service Layer.

Este módulo soporta dos escenarios sin que el resto de la app deba saber
cuál aplica:
  - Caso A: una sola base de datos para las 3 sucursales (SAP B1 con
    Multi-Sucursal activado). Se ejecuta la consulta una sola vez.
  - Caso B: una base de datos distinta por sucursal. Se ejecuta la misma
    consulta en cada conexión y se etiqueta cada resultado con su sucursal.
"""
from typing import Optional

import pandas as pd
import streamlit as st

import config


@st.cache_resource(show_spinner=False)
def _get_connection(server: str, database: str, user: str, password: str):
    # pyodbc se importa aquí adentro (no al inicio del archivo) para que el
    # modo demo funcione aunque todavía no tengas instalado el driver ODBC
    # de SQL Server en tu máquina.
    import pyodbc

    conn_str = (
        "DRIVER={ODBC Driver 18 for SQL Server};"
        f"SERVER={server};DATABASE={database};"
        f"UID={user};PWD={password};"
        "TrustServerCertificate=yes;"
    )
    return pyodbc.connect(conn_str, timeout=5)


def _connection_key(conn: dict) -> str:
    return f"{conn['server']}|{conn['database']}"


def run_query(query: str, branches: list[str]) -> pd.DataFrame:
    """Ejecuta `query` sobre las sucursales solicitadas y devuelve un único
    DataFrame con columna "Sucursal" agregada.

    `query` debe ser una consulta SELECT simple (sin filtro de sucursal):
    el filtrado por sucursal lo resuelve esta función según el caso A o B
    descrito arriba.
    """
    conns = {b: config.BRANCH_CONNECTIONS.get(b) for b in branches}
    conns = {b: c for b, c in conns.items() if c}
    if not conns:
        return pd.DataFrame()

    distinct_keys = {_connection_key(c) for c in conns.values()}

    if len(distinct_keys) == 1:
        # Caso A: una sola base de datos
        conn = next(iter(conns.values()))
        cn = _get_connection(conn["server"], conn["database"], conn["user"], conn["password"])
        df = pd.read_sql(query, cn)
        if "Sucursal" not in df.columns:
            # Si tu vista/consulta ya incluye la sucursal (por ejemplo a partir
            # de OBPL.BPLName), bórralo de esta condición para respetarla.
            df["Sucursal"] = "Todas"
        return df

    # Caso B: una base de datos por sucursal
    frames = []
    for branch, conn in conns.items():
        cn = _get_connection(conn["server"], conn["database"], conn["user"], conn["password"])
        df = pd.read_sql(query, cn)
        df["Sucursal"] = branch
        frames.append(df)
    return pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()


def test_connection(branch: str) -> Optional[str]:
    """Prueba la conexión a una sucursal. Devuelve None si todo bien,
    o un mensaje de error si algo falla. Útil para un botón de diagnóstico."""
    conn = config.BRANCH_CONNECTIONS.get(branch)
    if not conn:
        return f"No hay conexión configurada para {branch} en el archivo .env"
    try:
        cn = _get_connection(conn["server"], conn["database"], conn["user"], conn["password"])
        pd.read_sql("SELECT 1 AS ok", cn)
        return None
    except Exception as exc:
        return str(exc)
