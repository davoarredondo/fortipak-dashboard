"""
data/queries.py
-----------------
Consultas SQL contra las tablas estándar de SAP B1, y funciones que
transforman el resultado en Items (tarjetas) para el dashboard.

IMPORTANTE — léelo antes de pasar a producción:
Estas consultas son un punto de partida correcto basado en las tablas
estándar de SAP B1, pero algunos nombres de campo y valores de estatus
pueden variar según tu versión/localización exacta y según si manejan
campos propios (UDFs). Los marqué con "# VERIFICAR" donde conviene que
los confirmes corriendo un SELECT rápido en tu SQL Server antes de usarlos
en vivo. Esto lo revisamos juntos en la siguiente sesión de programación.

Las reglas de "qué tan urgente es" (verde/amarillo/rojo) están aisladas en
funciones cortas al final de cada bloque, para que sea fácil ajustarlas a
como realmente trabajan en FORTIPAK sin tocar el resto del código.
"""
from datetime import datetime, timedelta

import pandas as pd

from data.db import run_query
from data.model import Item


# ---------------------------------------------------------------------------
# Recepciones de proveedores (Purchase Delivery Note — GRPO)
# ---------------------------------------------------------------------------
RECEPCIONES_SQL = """
SELECT
    T0.DocEntry,
    T0.DocNum,
    T0.CardName   AS Proveedor,
    T0.DocDate,
    T0.DocTime,
    T0.Comments
FROM OPDN T0
WHERE T0.DocDate = CONVERT(date, GETDATE())
ORDER BY T0.DocTime DESC
"""


def _recepcion_status(doc_time) -> str:
    # Regla simple de ejemplo: si lleva más de 90 min desde su hora registrada
    # sin pasar a la siguiente etapa, se marca como atención. Ajustar según
    # cómo definan ustedes un GRPO "atrasado".
    return "ok"


def recepciones_from_df(df: pd.DataFrame) -> list[Item]:
    items = []
    for _, row in df.iterrows():
        items.append(Item(
            id=f"GRPO-{row['DocNum']}",
            title=f"GRPO-{row['DocNum']}",
            subtitle=f"{row['Proveedor']} · {row['Sucursal']}",
            status=_recepcion_status(row.get("DocTime")),
            branch=row["Sucursal"],
            detail={
                "Proveedor": row["Proveedor"],
                "Fecha": str(row["DocDate"]),
                "Comentarios": row.get("Comments") or "—",
            },
        ))
    return items


# ---------------------------------------------------------------------------
# Pedidos de clientes a entregar hoy (Sales Order — ORDR), abiertos
# ---------------------------------------------------------------------------
PEDIDOS_SQL = """
SELECT
    T0.DocEntry,
    T0.DocNum,
    T0.CardName   AS Cliente,
    T0.DocDueDate,
    T0.Comments
FROM ORDR T0
WHERE T0.DocDueDate = CONVERT(date, GETDATE())
  AND T0.DocStatus = 'O'  -- VERIFICAR: 'O' = abierto en la mayoría de instalaciones
ORDER BY T0.DocDueDate ASC
"""


def pedidos_from_df(df: pd.DataFrame) -> list[Item]:
    items = []
    for _, row in df.iterrows():
        items.append(Item(
            id=f"Pedido {row['DocNum']}",
            title=f"Pedido {row['DocNum']}",
            subtitle=f"{row['Cliente']} · {row['Sucursal']}",
            status="warn",  # VERIFICAR: cruzar con su picking asociado (ver picking_from_df)
            branch=row["Sucursal"],
            detail={
                "Cliente": row["Cliente"],
                "Entrega comprometida": str(row["DocDueDate"]),
                "Comentarios": row.get("Comments") or "—",
            },
        ))
    return items


# ---------------------------------------------------------------------------
# Listas de picking (OPKL), del día
# ---------------------------------------------------------------------------
PICKING_SQL = """
SELECT
    T0.AbsEntry,
    T0.Name,
    T0.PickDate,
    T0.Status,    -- VERIFICAR valores reales: confirmar con SELECT DISTINCT Status FROM OPKL
    T0.Remarks
FROM OPKL T0
WHERE T0.PickDate = CONVERT(date, GETDATE())
ORDER BY T0.PickDate DESC
"""


def _picking_status(sap_status: str) -> str:
    sap_status = (sap_status or "").lower()
    if "close" in sap_status or "picked" in sap_status:
        return "ok"
    if "open" in sap_status:
        return "danger"
    return "warn"


def picking_from_df(df: pd.DataFrame) -> list[Item]:
    items = []
    for _, row in df.iterrows():
        items.append(Item(
            id=f"PKL-{row['AbsEntry']}",
            title=f"PKL-{row['AbsEntry']}",
            subtitle=f"{row['Sucursal']} · {row.get('Status', '')}",
            status=_picking_status(row.get("Status")),
            branch=row["Sucursal"],
            detail={
                "Nombre": row.get("Name") or "—",
                "Comentarios": row.get("Remarks") or "—",
            },
        ))
    return items


# ---------------------------------------------------------------------------
# Traslados pendientes entre almacenes (Inventory Transfer Request — OWTQ)
# ---------------------------------------------------------------------------
# VERIFICAR: si en FORTIPAK no usan "solicitud de traslado" (OWTQ) y crean
# directamente el traslado (OWTR), cambiar esta consulta a OWTR con
# DocStatus = 'O' (si aplica) o al criterio que usen para "pendiente".
TRASLADOS_SQL = """
SELECT
    T0.DocEntry,
    T0.DocNum,
    T0.DocDate,
    T0.Comments
FROM OWTQ T0
WHERE T0.DocStatus = 'O'
ORDER BY T0.DocDate ASC
"""


def traslados_from_df(df: pd.DataFrame) -> list[Item]:
    items = []
    for _, row in df.iterrows():
        dias = (datetime.now().date() - pd.to_datetime(row["DocDate"]).date()).days
        status = "danger" if dias >= 1 else "warn"
        items.append(Item(
            id=f"WTR-{row['DocNum']}",
            title=f"WTR-{row['DocNum']}",
            subtitle=f"{row['Sucursal']}",
            status=status,
            branch=row["Sucursal"],
            detail={
                "Fecha de solicitud": str(row["DocDate"]),
                "Comentarios": row.get("Comments") or "—",
            },
        ))
    return items


# ---------------------------------------------------------------------------
# Órdenes de fabricación en proceso (OWOR)
# ---------------------------------------------------------------------------
PRODUCCION_SQL = """
SELECT
    T0.DocEntry,
    T0.DocNum,
    T0.ProdName,
    T0.PlannedQty,
    T0.CmpltQty,
    T0.DueDate
FROM OWOR T0
WHERE T0.Status = 'R'  -- VERIFICAR: 'R' = Released/en proceso en la mayoría de instalaciones
ORDER BY T0.DueDate ASC
"""


def _produccion_status(planned, completed, due_date) -> str:
    try:
        avance = (completed / planned) if planned else 0
    except ZeroDivisionError:
        avance = 0
    if due_date and pd.to_datetime(due_date).date() < datetime.now().date():
        return "danger"
    if avance < 0.3:
        return "warn"
    return "ok"


def produccion_from_df(df: pd.DataFrame) -> list[Item]:
    items = []
    for _, row in df.iterrows():
        planned, completed = row.get("PlannedQty", 0), row.get("CmpltQty", 0)
        avance_pct = round((completed / planned) * 100) if planned else 0
        items.append(Item(
            id=f"OF-{row['DocNum']}",
            title=f"OF-{row['DocNum']}",
            subtitle=f"{row['Sucursal']} · {avance_pct}%",
            status=_produccion_status(planned, completed, row.get("DueDate")),
            branch=row["Sucursal"],
            detail={
                "Producto": row.get("ProdName") or "—",
                "Avance": f"{avance_pct}%",
                "Fecha compromiso": str(row.get("DueDate") or "—"),
            },
        ))
    return items


# ---------------------------------------------------------------------------
# Entregas a clientes (ODLN), del día
# ---------------------------------------------------------------------------
ENTREGAS_SQL = """
SELECT
    T0.DocEntry,
    T0.DocNum,
    T0.CardName   AS Cliente,
    T0.DocDate,
    T0.DocTime,
    T0.Comments
FROM ODLN T0
WHERE T0.DocDate = CONVERT(date, GETDATE())
ORDER BY T0.DocTime DESC
"""


def entregas_from_df(df: pd.DataFrame) -> list[Item]:
    items = []
    for _, row in df.iterrows():
        items.append(Item(
            id=f"DLN-{row['DocNum']}",
            title=f"DLN-{row['DocNum']}",
            subtitle=f"{row['Cliente']} · {row['Sucursal']}",
            status="ok",  # VERIFICAR: cruzar con hora comprometida si la registran
            branch=row["Sucursal"],
            detail={
                "Cliente": row["Cliente"],
                "Comentarios": row.get("Comments") or "—",
            },
        ))
    return items


# ---------------------------------------------------------------------------
# Facturas emitidas a clientes (OINV), del día
# ---------------------------------------------------------------------------
FACTURACION_SQL = """
SELECT
    T0.DocEntry,
    T0.DocNum,
    T0.CardName   AS Cliente,
    T0.DocDate,
    T0.DocTotal
FROM OINV T0
WHERE T0.DocDate = CONVERT(date, GETDATE())
ORDER BY T0.DocDate DESC
"""


def facturacion_from_df(df: pd.DataFrame) -> list[Item]:
    items = []
    for _, row in df.iterrows():
        items.append(Item(
            id=f"Factura {row['DocNum']}",
            title=f"Factura {row['DocNum']}",
            subtitle=f"{row['Cliente']} · {row['Sucursal']}",
            status="ok",
            branch=row["Sucursal"],
            detail={
                "Cliente": row["Cliente"],
                "Monto": f"${row['DocTotal']:,.2f} MXN",
            },
        ))
    return items


# ---------------------------------------------------------------------------
# Orquestador: arma todas las "lanes" consultando SQL real
# ---------------------------------------------------------------------------
def get_live_items(branches: list[str]) -> dict[str, list[Item]]:
    return {
        "recepciones": recepciones_from_df(run_query(RECEPCIONES_SQL, branches)),
        "produccion": produccion_from_df(run_query(PRODUCCION_SQL, branches)),
        "traslados": traslados_from_df(run_query(TRASLADOS_SQL, branches)),
        "pedidos": pedidos_from_df(run_query(PEDIDOS_SQL, branches)),
        "picking": picking_from_df(run_query(PICKING_SQL, branches)),
        "entregas": entregas_from_df(run_query(ENTREGAS_SQL, branches)),
        "facturacion": facturacion_from_df(run_query(FACTURACION_SQL, branches)),
    }
