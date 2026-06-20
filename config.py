"""
config.py
---------
Carga toda la configuración de la app desde variables de entorno (archivo .env).
Así separamos datos sensibles (servidores, usuarios, contraseñas) del código
fuente, que sí se puede compartir o versionar sin riesgo.

No necesitas modificar este archivo: todo se ajusta editando ".env".
"""
import os
from dotenv import load_dotenv

load_dotenv()


def _bool(value, default=False):
    if value is None:
        return default
    return str(value).strip().lower() in ("1", "true", "yes", "si", "sí")


# --- Modo demo -------------------------------------------------------------
DEMO_MODE = _bool(os.getenv("DEMO_MODE"), default=True)

# --- Autenticación (SAP Service Layer) --------------------------------------
SAP_SERVICE_LAYER_URL = os.getenv("SAP_SERVICE_LAYER_URL", "").rstrip("/")
SAP_COMPANY_DB = os.getenv("SAP_COMPANY_DB", "")
SAP_VERIFY_SSL = _bool(os.getenv("SAP_VERIFY_SSL"), default=True)

# --- Refresco automático -----------------------------------------------------
REFRESH_INTERVAL_SECONDS = int(os.getenv("REFRESH_INTERVAL_SECONDS", "60"))

# --- Sucursales --------------------------------------------------------------
BRANCHES = ["León", "Aguascalientes", "SLP"]


def _branch_connection(suffix: str):
    """Arma el diccionario de conexión SQL para una sucursal a partir de
    las variables SQL_SERVER_<suffix>, SQL_DATABASE_<suffix>, etc.
    Devuelve None si no están definidas (para saber que no aplica)."""
    server = os.getenv(f"SQL_SERVER_{suffix}")
    database = os.getenv(f"SQL_DATABASE_{suffix}")
    if not server or not database:
        return None
    return {
        "server": server,
        "database": database,
        "user": os.getenv(f"SQL_USER_{suffix}", ""),
        "password": os.getenv(f"SQL_PASSWORD_{suffix}", ""),
    }


_default_conn = _branch_connection("DEFAULT")

# Si existen variables específicas por sucursal (LEON / AGS / SLP) se usan esas;
# si no, las 3 sucursales apuntan a la misma conexión DEFAULT (caso típico de
# SAP B1 con Multi-Sucursal activado dentro de una sola base de datos).
BRANCH_CONNECTIONS = {
    "León": _branch_connection("LEON") or _default_conn,
    "Aguascalientes": _branch_connection("AGS") or _default_conn,
    "SLP": _branch_connection("SLP") or _default_conn,
}
