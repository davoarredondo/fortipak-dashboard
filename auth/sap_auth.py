"""
auth/sap_auth.py
-----------------
Autenticación de usuarios contra SAP Business One Service Layer.

Por qué así y no contra la base de datos directamente:
SAP B1 guarda las contraseñas de usuario cifradas/con hash dentro de SQL Server.
Validar "a mano" contra esa tabla sería fragil, inseguro, y se rompería con
cada actualización de SAP. El Service Layer ya expone un endpoint de login
oficial (POST /Login) que hace esa validación por nosotros: nuestra app nunca
ve ni guarda contraseñas, solo recibe "sí, es válido" o "no, no es válido".
"""
from dataclasses import dataclass
from typing import Optional

import requests


@dataclass
class AuthResult:
    success: bool
    session_id: Optional[str] = None
    user_name: Optional[str] = None
    error: Optional[str] = None


def login_to_sap(
    service_layer_url: str,
    company_db: str,
    username: str,
    password: str,
    verify_ssl: bool = True,
    timeout: int = 10,
) -> AuthResult:
    """Intenta iniciar sesión en SAP B1 Service Layer.

    Devuelve un AuthResult. Si success=True, session_id trae el token de
    sesión que el Service Layer asignó (útil si más adelante quieres hacer
    también lecturas vía Service Layer, no solo autenticación).
    """
    if not service_layer_url or not company_db:
        return AuthResult(
            success=False,
            error="Falta configurar SAP_SERVICE_LAYER_URL o SAP_COMPANY_DB en el archivo .env",
        )

    url = f"{service_layer_url}/Login"
    payload = {
        "CompanyDB": company_db,
        "UserName": username,
        "Password": password,
    }

    try:
        response = requests.post(url, json=payload, verify=verify_ssl, timeout=timeout)
    except requests.exceptions.SSLError:
        return AuthResult(
            success=False,
            error=(
                "Error de certificado SSL al conectar con SAP. Si tu Service Layer "
                "usa un certificado autofirmado, ajusta SAP_VERIFY_SSL=false en .env."
            ),
        )
    except requests.exceptions.RequestException as exc:
        return AuthResult(success=False, error=f"No se pudo contactar al servidor SAP: {exc}")

    if response.status_code == 200:
        data = response.json()
        return AuthResult(success=True, session_id=data.get("SessionId"), user_name=username)

    # SAP devuelve el detalle del error en este formato
    try:
        message = response.json().get("error", {}).get("message", {}).get("value")
    except Exception:
        message = None
    return AuthResult(success=False, error=message or "Usuario o contraseña incorrectos")


def login_demo(username: str, password: str) -> AuthResult:
    """Versión de autenticación para modo demo: acepta cualquier usuario y
    contraseña no vacíos, sin contactar ningún servidor."""
    if not username or not password:
        return AuthResult(success=False, error="Escribe usuario y contraseña (modo demo).")
    return AuthResult(success=True, session_id="demo-session", user_name=username)
