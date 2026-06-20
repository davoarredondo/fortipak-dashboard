# Centro de operaciones FORTIPAK

Dashboard en Streamlit con visión 360° de las operaciones diarias: recepciones
de proveedores, producción, traslados entre almacenes, pedidos a entregar hoy,
picking, entregas y facturación — con filtro por sucursal y avisos urgentes.

Este proyecto ya fue probado y arranca correctamente en **modo demo** (datos de
ejemplo, sin conexión real a SAP). Cuando quieras conectarlo a tu SAP real,
solo necesitas editar el archivo `.env` — no hay que tocar el código.

---

## 1. Qué necesitas instalar (una sola vez)

Como nunca has usado Python, esto es lo mínimo que necesita tu máquina:

1. **Python 3.11 o superior** — descárgalo de https://www.python.org/downloads/
   Durante la instalación en Windows, marca la casilla "Add python.exe to PATH".
2. **Driver ODBC 18 para SQL Server** (solo necesario cuando conectes a SAP de
   verdad, no para el modo demo) — descárgalo de Microsoft:
   https://learn.microsoft.com/sql/connect/odbc/download-odbc-driver-for-sql-server

## 2. Preparar el proyecto (una sola vez)

Abre una terminal (en Windows: PowerShell) dentro de esta carpeta y ejecuta:

```bash
# Crea un "entorno virtual": una copia aislada de Python solo para este
# proyecto, para no mezclar librerías con otras cosas que tengas instaladas.
python -m venv venv

# Actívalo (cada vez que vayas a trabajar en el proyecto, este paso se repite)
# En Windows:
venv\Scripts\activate
# En Mac/Linux:
source venv/bin/activate

# Instala las librerías que usa el proyecto (se leen de requirements.txt)
pip install -r requirements.txt

# Copia la plantilla de configuración
# En Windows:
copy .env.example .env
# En Mac/Linux:
cp .env.example .env
```

## 3. Correr la app en modo demo (recomendado para la primera prueba)

El archivo `.env` ya viene con `DEMO_MODE=true`, así que no necesitas
configurar nada más. Solo ejecuta:

```bash
streamlit run app.py
```

Se abrirá tu navegador en `http://localhost:8501`. El login acepta
cualquier usuario y contraseña en este modo.

## 4. Conectar con tu SAP B1 real

Cuando estés listo, edita el archivo `.env` (con cualquier editor de texto,
como Bloc de notas o VS Code) y ajusta estos bloques:

### a) Autenticación (Service Layer)
```
SAP_SERVICE_LAYER_URL=https://tu-servidor:50000/b1s/v1
SAP_COMPANY_DB=SBO_FORTIPAK
```
Esto es lo que valida usuario y contraseña de cada persona contra SAP.

### b) Lectura de datos (SQL Server)
Antes de esto, pide a tu administrador de SAP/SQL que cree un **usuario de
SQL Server de solo lectura** dedicado a este dashboard (no uses el usuario
`sa` ni el de SAP_SYSTEM). Permisos mínimos: `SELECT` sobre la base de datos
de la empresa. Con esos datos llena:
```
SQL_SERVER_DEFAULT=servidor,1433
SQL_DATABASE_DEFAULT=SBO_FORTIPAK
SQL_USER_DEFAULT=fortipak_dashboard_ro
SQL_PASSWORD_DEFAULT=la-contraseña-que-le-asignen
```

Si en lugar de una sola base de datos multi-sucursal manejan una base de
datos distinta por planta, hay un bloque alternativo (LEON/AGS/SLP) ya
explicado dentro del propio archivo `.env.example`.

### c) Apagar el modo demo
```
DEMO_MODE=false
```

Vuelve a correr `streamlit run app.py` y ya estará leyendo datos reales.

## 5. Sobre las consultas SQL (`data/queries.py`)

Las consultas a SAP que incluí están basadas en las tablas estándar de
SAP B1 (OPDN, ORDR, OPKL, OWTQ, OWOR, ODLN, OINV), pero marqué con
`# VERIFICAR` los puntos donde conviene confirmar contigo los valores
exactos de estatus y las reglas de "qué cuenta como urgente" que de verdad
usan en FORTIPAK — eso lo afinamos juntos en la siguiente sesión, una vez
que puedas correr algunas consultas de prueba contra tu base de datos real.

## 6. Estructura del proyecto

```
app.py                  → pantalla principal (login + dashboard)
config.py                → lee la configuración del archivo .env
auth/sap_auth.py          → autenticación contra SAP Service Layer
data/db.py                 → conexión de solo lectura a SQL Server
data/queries.py             → consultas SQL reales y su transformación a tarjetas
data/demo_data.py            → datos de ejemplo para el modo demo
data/source.py                → decide si usar datos demo o reales
ui/components.py               → KPIs, banner de avisos, carriles, tarjetas
ui/styles.py                    → estilos visuales
```

## 7. Seguridad — recordatorios importantes

- El archivo `.env` contiene contraseñas: **nunca lo compartas ni lo subas**
  a ningún repositorio o carpeta compartida sin protección.
- El usuario SQL de este dashboard debe ser de **solo lectura**.
- La identidad de cada persona se valida contra SAP (Service Layer), no
  contra el archivo `.env` ni contra ninguna lista propia de la app.
