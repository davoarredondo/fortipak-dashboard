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

Sobre el cruce de stock en Pedidos:
Para cada partida pendiente de un pedido, se compara contra OITW.OnHand
(existencia física en el almacén de esa partida). Esto es una
simplificación: lo más correcto suele ser comparar contra "disponible"
(OnHand - Comprometido + En tránsito), porque parte del OnHand puede ya
estar comprometido con otro pedido. Lo dejé así para la primera versión
porque es lo más fácil de verificar a simple vista, y lo afinamos juntos
con tus reglas reales de cuándo SAP considera algo "disponible".
"""
from datetime import datetime

import pandas as pd

from data.db import run_query
from data.model import Item


# ---------------------------------------------------------------------------
# Recepciones de proveedores (Purchase Delivery Note — GRPO)
# ---------------------------------------------------------------------------
RECEPCIONES_SQL = """
SELECT
    T0.DocEntry, T0.DocNum, T0.CardCode, T0.CardName AS Proveedor,
    T0.DocDate, T0.DocTime, T0.DocTotal, T0.NumAtCard, T0.Comments,
    (SELECT COUNT(*) FROM PDN1 L WHERE L.DocEntry = T0.DocEntry) AS Partidas,
    (SELECT TOP 1 L.WhsCode FROM PDN1 L WHERE L.DocEntry = T0.DocEntry) AS Almacen
FROM OPDN T0
WHERE T0.DocDate = CONVERT(date, GETDATE())
ORDER BY T0.DocTime DESC
"""


def recepciones_from_df(df: pd.DataFrame) -> list[Item]:
    items = []
    for _, row in df.iterrows():
        items.append(Item(
            id=f"GRPO-{row['DocNum']}",
            title=f"GRPO-{row['DocNum']}",
            subtitle=f"{row['Proveedor']} · {row['Sucursal']}",
            status="ok",  # VERIFICAR: definir regla de "atrasado" (ej. cruzar con OC origen)
            branch=row["Sucursal"],
            detail={
                "Proveedor": row["Proveedor"],
                "Código proveedor": row.get("CardCode", "—"),
                "Almacén": row.get("Almacen", "—"),
                "Fecha": str(row["DocDate"]),
                "Partidas": row.get("Partidas", "—"),
                "Monto": f"${row['DocTotal']:,.2f} MXN" if pd.notna(row.get("DocTotal")) else "—",
                "Referencia proveedor": row.get("NumAtCard", "—"),
                "Comentarios": row.get("Comments") or "—",
            },
        ))
    return items


# ---------------------------------------------------------------------------
# Pedidos de clientes a entregar hoy (ORDR + RDR1), con cruce de stock
# ---------------------------------------------------------------------------
PEDIDOS_LINES_SQL = """
SELECT
    T0.DocEntry, T0.DocNum, T0.CardCode, T0.CardName AS Cliente,
    T0.DocDueDate, T0.Comments, T0.DocTotal,
    S.SlpName AS Vendedor,
    T1.LineNum, T1.ItemCode, T1.Dscription, T1.WhsCode,
    T1.OpenQty,                                   -- VERIFICAR: pendiente por entregar
    W.OnHand AS StockAlmacen                       -- VERIFICAR: ver nota sobre "disponible" arriba
FROM ORDR T0
JOIN RDR1 T1 ON T1.DocEntry = T0.DocEntry
LEFT JOIN OITW W ON W.ItemCode = T1.ItemCode AND W.WhsCode = T1.WhsCode
LEFT JOIN OSLP S ON S.SlpCode = T0.SlpCode
WHERE T0.DocDueDate = CONVERT(date, GETDATE())
  AND T0.DocStatus = 'O'    -- VERIFICAR: 'O' = abierto
  AND T1.LineStatus = 'O'   -- VERIFICAR: solo partidas aún abiertas
ORDER BY T0.DocNum, T1.LineNum
"""


def pedidos_from_df(df: pd.DataFrame) -> list[Item]:
    items = []
    if df.empty:
        return items
    for (doc_num, sucursal), grupo in df.groupby(["DocNum", "Sucursal"]):
        first = grupo.iloc[0]
        lines = []
        hay_insuficiente = False
        hay_justo = False
        for _, l in grupo.iterrows():
            pendiente = l.get("OpenQty", 0) or 0
            stock = l.get("StockAlmacen", 0) or 0
            if pendiente <= 0:
                estatus = "🟢 Cubierto"
            elif stock < pendiente:
                estatus = f"🔴 Insuficiente, faltan {pendiente - stock:.0f}"
                hay_insuficiente = True
            elif stock == pendiente:
                estatus = "🟡 Justo, sin margen"
                hay_justo = True
            else:
                estatus = "🟢 Cubierto"
            lines.append({
                "Artículo": l.get("Dscription") or l.get("ItemCode"),
                "Pendiente por entregar": pendiente,
                f"Stock disponible ({l.get('WhsCode', '—')})": stock,
                "Estatus": estatus,
            })

        status = "danger" if hay_insuficiente else ("warn" if hay_justo else "ok")
        items.append(Item(
            id=f"Pedido {doc_num}",
            title=f"Pedido {doc_num}",
            subtitle=f"{first['Cliente']} · {sucursal}",
            status=status,
            branch=sucursal,
            detail={
                "Cliente": first["Cliente"],
                "Código cliente": first.get("CardCode", "—"),
                "Vendedor": first.get("Vendedor", "—"),
                "Entrega comprometida": str(first["DocDueDate"]),
                "Monto": f"${first['DocTotal']:,.2f} MXN" if pd.notna(first.get("DocTotal")) else "—",
                "Comentarios": first.get("Comments") or "—",
            },
            lines=lines,
        ))
    return items


# ---------------------------------------------------------------------------
# Listas de picking (OPKL + PKL1), del día
# ---------------------------------------------------------------------------
PICKING_LINES_SQL = """
SELECT
    T0.AbsEntry, T0.Name, T0.PickDate, T0.Status, T0.Remarks,
    T1.ItemCode,
    T1.ReleasedQuantity,    -- VERIFICAR nombre exacto de columna en tu versión
    T1.PickedQuantity,      -- VERIFICAR nombre exacto de columna en tu versión
    T1.WhsCode,
    O.DocNum AS PedidoAsociado
FROM OPKL T0
JOIN PKL1 T1 ON T1.AbsEntry = T0.AbsEntry
LEFT JOIN ORDR O ON O.DocEntry = T1.OrderEntry AND T1.BaseObject = 17  -- VERIFICAR: 17 = pedido de venta
WHERE T0.PickDate = CONVERT(date, GETDATE())
ORDER BY T0.AbsEntry
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
    if df.empty:
        return items
    for (abs_entry, sucursal), grupo in df.groupby(["AbsEntry", "Sucursal"]):
        first = grupo.iloc[0]
        lines = []
        for _, l in grupo.iterrows():
            a_surtir = l.get("ReleasedQuantity", 0) or 0
            surtido = l.get("PickedQuantity", 0) or 0
            lines.append({
                "Artículo": l.get("ItemCode"),
                "A surtir": a_surtir,
                "Ya surtido": surtido,
                "Pendiente": max(a_surtir - surtido, 0),
            })
        items.append(Item(
            id=f"PKL-{abs_entry}",
            title=f"PKL-{abs_entry}",
            subtitle=f"{sucursal} · {first.get('Status', '')}",
            status=_picking_status(first.get("Status")),
            branch=sucursal,
            detail={
                "Nombre": first.get("Name") or "—",
                "Pedido asociado": first.get("PedidoAsociado", "—"),
                "Almacén": first.get("WhsCode", "—"),
                "Comentarios": first.get("Remarks") or "—",
            },
            lines=lines,
        ))
    return items


# ---------------------------------------------------------------------------
# Traslados pendientes entre almacenes (Inventory Transfer Request — OWTQ)
# ---------------------------------------------------------------------------
# VERIFICAR: si en FORTIPAK no usan "solicitud de traslado" (OWTQ) y crean
# directamente el traslado (OWTR), cambiar esta consulta a OWTR.
TRASLADOS_SQL = """
SELECT
    T0.DocEntry, T0.DocNum, T0.DocDate, T0.Comments,
    (SELECT TOP 1 L.FromWhsCode FROM WTQ1 L WHERE L.DocEntry = T0.DocEntry) AS Origen,
    (SELECT TOP 1 L.WhsCode FROM WTQ1 L WHERE L.DocEntry = T0.DocEntry) AS Destino,
    (SELECT COUNT(*) FROM WTQ1 L WHERE L.DocEntry = T0.DocEntry) AS Partidas
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
            subtitle=f"{row.get('Origen', '—')} → {row.get('Destino', '—')}",
            status=status,
            branch=row["Sucursal"],
            detail={
                "Origen": row.get("Origen", "—"),
                "Destino": row.get("Destino", "—"),
                "Partidas": row.get("Partidas", "—"),
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
    T0.DocEntry, T0.DocNum, T0.ItemCode, T0.ProdName,
    T0.PlannedQty, T0.CmpltQty, T0.DueDate, T0.WhsCode
FROM OWOR T0
WHERE T0.Status = 'R'  -- VERIFICAR: 'R' = Released/en proceso
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
                "Código artículo": row.get("ItemCode", "—"),
                "Almacén": row.get("WhsCode", "—"),
                "Cantidad planeada": planned,
                "Cantidad completada": completed,
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
    T0.DocEntry, T0.DocNum, T0.CardCode, T0.CardName AS Cliente,
    T0.DocDate, T0.DocTime, T0.DocTotal, T0.Comments,
    (SELECT COUNT(*) FROM DLN1 L WHERE L.DocEntry = T0.DocEntry) AS Partidas,
    (SELECT TOP 1 L.BaseEntry FROM DLN1 L WHERE L.DocEntry = T0.DocEntry AND L.BaseType = 17) AS PedidoOrigenEntry
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
                "Código cliente": row.get("CardCode", "—"),
                "Partidas": row.get("Partidas", "—"),
                "Monto": f"${row['DocTotal']:,.2f} MXN" if pd.notna(row.get("DocTotal")) else "—",
                "Pedido origen (DocEntry)": row.get("PedidoOrigenEntry", "—"),
                "Comentarios": row.get("Comments") or "—",
            },
        ))
    return items


# ---------------------------------------------------------------------------
# Facturas emitidas a clientes (OINV), del día
# ---------------------------------------------------------------------------
FACTURACION_SQL = """
SELECT
    T0.DocEntry, T0.DocNum, T0.CardCode, T0.CardName AS Cliente,
    T0.DocDate, T0.DocTotal, T0.PaidToDate,
    (SELECT TOP 1 L.BaseEntry FROM INV1 L WHERE L.DocEntry = T0.DocEntry AND L.BaseType = 15) AS EntregaOrigenEntry
FROM OINV T0
WHERE T0.DocDate = CONVERT(date, GETDATE())
ORDER BY T0.DocDate DESC
"""


def facturacion_from_df(df: pd.DataFrame) -> list[Item]:
    items = []
    for _, row in df.iterrows():
        saldo = (row.get("DocTotal", 0) or 0) - (row.get("PaidToDate", 0) or 0)
        items.append(Item(
            id=f"Factura {row['DocNum']}",
            title=f"Factura {row['DocNum']}",
            subtitle=f"{row['Cliente']} · {row['Sucursal']}",
            status="ok",
            branch=row["Sucursal"],
            detail={
                "Cliente": row["Cliente"],
                "Código cliente": row.get("CardCode", "—"),
                "Monto": f"${row['DocTotal']:,.2f} MXN",
                "Saldo pendiente": f"${saldo:,.2f} MXN",
                "Entrega origen (DocEntry)": row.get("EntregaOrigenEntry", "—"),
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
        "pedidos": pedidos_from_df(run_query(PEDIDOS_LINES_SQL, branches)),
        "picking": picking_from_df(run_query(PICKING_LINES_SQL, branches)),
        "entregas": entregas_from_df(run_query(ENTREGAS_SQL, branches)),
        "facturacion": facturacion_from_df(run_query(FACTURACION_SQL, branches)),
    }
