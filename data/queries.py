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

Patrón general:
Cada categoría trae dos niveles: encabezado del documento (cliente,
proveedor, fechas, montos) y partidas (qué artículos contiene). Las
consultas siempre traen el resultado "aplanado" (una fila por partida, con
los datos del encabezado repetidos), y la función *_from_df() lo agrupa
por documento para armar un Item con su lista de líneas (`item.lines`).
Esto es lo que permite que cualquier tarjeta se pueda abrir y mostrar
exactamente qué contiene, sin una consulta aparte por cada clic.

Sobre el cruce de stock en Pedidos:
Para cada partida pendiente de un pedido, se compara contra OITW.OnHand
(existencia física en el almacén de esa partida). Esto es una
simplificación: lo más correcto suele ser comparar contra "disponible"
(OnHand - Comprometido + En tránsito). Lo dejé así para la primera
versión porque es lo más fácil de verificar a simple vista, y lo afinamos
juntos con tus reglas reales de cuándo SAP considera algo "disponible".
"""
from datetime import datetime

import pandas as pd

from data.db import run_query
from data.model import Item


def _group_items(df: pd.DataFrame, doc_key: str):
    """Utilidad común: agrupa un DataFrame "aplanado" (encabezado + partidas)
    por documento y sucursal, y entrega (encabezado, grupo_de_lineas) por
    cada documento, en el orden en que aparecen."""
    if df.empty:
        return
    for (doc_num, sucursal), grupo in df.groupby([doc_key, "Sucursal"], sort=False):
        yield doc_num, sucursal, grupo.iloc[0], grupo


# ---------------------------------------------------------------------------
# Recepciones de proveedores (OPDN + PDN1)
# ---------------------------------------------------------------------------
RECEPCIONES_SQL = """
SELECT
    T0.DocEntry, T0.DocNum, T0.CardCode, T0.CardName AS Proveedor,
    T0.DocDate, T0.DocTime, T0.NumAtCard, T0.Comments,
    T1.LineNum, T1.ItemCode, T1.Dscription, T1.Quantity, T1.Price, T1.WhsCode
FROM OPDN T0
JOIN PDN1 T1 ON T1.DocEntry = T0.DocEntry
WHERE T0.DocDate = CONVERT(date, GETDATE())
ORDER BY T0.DocNum, T1.LineNum
"""


def recepciones_from_df(df: pd.DataFrame) -> list[Item]:
    items = []
    for doc_num, sucursal, first, grupo in _group_items(df, "DocNum"):
        lines = [{
            "Artículo": l.get("Dscription") or l.get("ItemCode"),
            "Cantidad recibida": l.get("Quantity"),
            "Precio unitario": f"${l['Price']:,.2f}" if pd.notna(l.get("Price")) else "—",
            "Almacén": l.get("WhsCode", "—"),
        } for _, l in grupo.iterrows()]

        items.append(Item(
            id=f"GRPO-{doc_num}",
            title=f"GRPO-{doc_num}",
            subtitle=f"{first['Proveedor']} · {sucursal}",
            status="ok",  # VERIFICAR: definir regla de "atrasado" (ej. cruzar con OC origen)
            branch=sucursal,
            detail={
                "Proveedor": first["Proveedor"],
                "Código proveedor": first.get("CardCode", "—"),
                "Fecha": str(first["DocDate"]),
                "Referencia proveedor": first.get("NumAtCard", "—"),
                "Comentarios": first.get("Comments") or "—",
            },
            lines=lines,
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
    T1.Quantity,                                  -- cantidad original pedida
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
    for doc_num, sucursal, first, grupo in _group_items(df, "DocNum"):
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
                "Cantidad pedida": l.get("Quantity"),
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
    for abs_entry, sucursal, first, grupo in _group_items(df, "AbsEntry"):
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
# Traslados pendientes entre almacenes (OWTQ + WTQ1)
# ---------------------------------------------------------------------------
# VERIFICAR: si en FORTIPAK no usan "solicitud de traslado" (OWTQ) y crean
# directamente el traslado (OWTR), cambiar esta consulta a OWTR + WTR1.
TRASLADOS_SQL = """
SELECT
    T0.DocEntry, T0.DocNum, T0.DocDate, T0.Comments,
    T1.LineNum, T1.ItemCode, T1.Dscription, T1.Quantity,
    T1.FromWhsCode AS Origen, T1.WhsCode AS Destino
FROM OWTQ T0
JOIN WTQ1 T1 ON T1.DocEntry = T0.DocEntry
WHERE T0.DocStatus = 'O'
ORDER BY T0.DocNum, T1.LineNum
"""


def traslados_from_df(df: pd.DataFrame) -> list[Item]:
    items = []
    for doc_num, sucursal, first, grupo in _group_items(df, "DocNum"):
        dias = (datetime.now().date() - pd.to_datetime(first["DocDate"]).date()).days
        status = "danger" if dias >= 1 else "warn"
        lines = [{
            "Artículo": l.get("Dscription") or l.get("ItemCode"),
            "Cantidad": l.get("Quantity"),
            "Origen": l.get("Origen", "—"),
            "Destino": l.get("Destino", "—"),
        } for _, l in grupo.iterrows()]

        items.append(Item(
            id=f"WTR-{doc_num}",
            title=f"WTR-{doc_num}",
            subtitle=f"{first.get('Origen', '—')} → {first.get('Destino', '—')}",
            status=status,
            branch=sucursal,
            detail={
                "Origen": first.get("Origen", "—"),
                "Destino": first.get("Destino", "—"),
                "Fecha de solicitud": str(first["DocDate"]),
                "Comentarios": first.get("Comments") or "—",
            },
            lines=lines,
        ))
    return items


# ---------------------------------------------------------------------------
# Órdenes de fabricación en proceso (OWOR + WOR1 = componentes)
# ---------------------------------------------------------------------------
PRODUCCION_SQL = """
SELECT
    T0.DocEntry, T0.DocNum, T0.ItemCode, T0.ProdName,
    T0.PlannedQty, T0.CmpltQty, T0.DueDate, T0.WhsCode,
    T1.LineNum, T1.ItemCode AS ComponenteCode, T1.ItemName AS ComponenteDesc,
    T1.PlannedQty AS ComponentePlaneado,
    T1.IssuedQty AS ComponenteEmitido    -- VERIFICAR nombre exacto de columna
FROM OWOR T0
JOIN WOR1 T1 ON T1.DocEntry = T0.DocEntry
WHERE T0.Status = 'R'  -- VERIFICAR: 'R' = Released/en proceso
ORDER BY T0.DocNum, T1.LineNum
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
    for doc_num, sucursal, first, grupo in _group_items(df, "DocNum"):
        planned, completed = first.get("PlannedQty", 0), first.get("CmpltQty", 0)
        avance_pct = round((completed / planned) * 100) if planned else 0
        lines = [{
            "Componente": l.get("ComponenteDesc") or l.get("ComponenteCode"),
            "Planeado": l.get("ComponentePlaneado"),
            "Emitido": l.get("ComponenteEmitido"),
            "Pendiente": max((l.get("ComponentePlaneado") or 0) - (l.get("ComponenteEmitido") or 0), 0),
        } for _, l in grupo.iterrows()]

        items.append(Item(
            id=f"OF-{doc_num}",
            title=f"OF-{doc_num}",
            subtitle=f"{sucursal} · {avance_pct}%",
            status=_produccion_status(planned, completed, first.get("DueDate")),
            branch=sucursal,
            detail={
                "Producto": first.get("ProdName") or "—",
                "Código artículo": first.get("ItemCode", "—"),
                "Almacén": first.get("WhsCode", "—"),
                "Cantidad planeada": planned,
                "Cantidad completada": completed,
                "Avance": f"{avance_pct}%",
                "Fecha compromiso": str(first.get("DueDate") or "—"),
            },
            lines=lines,
        ))
    return items


# ---------------------------------------------------------------------------
# Entregas a clientes (ODLN + DLN1), del día
# ---------------------------------------------------------------------------
ENTREGAS_SQL = """
SELECT
    T0.DocEntry, T0.DocNum, T0.CardCode, T0.CardName AS Cliente,
    T0.DocDate, T0.DocTime, T0.Comments,
    T1.LineNum, T1.ItemCode, T1.Dscription, T1.Quantity, T1.Price, T1.WhsCode,
    T1.BaseEntry AS PedidoOrigenEntry, T1.BaseType
FROM ODLN T0
JOIN DLN1 T1 ON T1.DocEntry = T0.DocEntry
WHERE T0.DocDate = CONVERT(date, GETDATE())
ORDER BY T0.DocNum, T1.LineNum
"""


def entregas_from_df(df: pd.DataFrame) -> list[Item]:
    items = []
    for doc_num, sucursal, first, grupo in _group_items(df, "DocNum"):
        lines = [{
            "Artículo": l.get("Dscription") or l.get("ItemCode"),
            "Cantidad entregada": l.get("Quantity"),
            "Precio unitario": f"${l['Price']:,.2f}" if pd.notna(l.get("Price")) else "—",
            "Almacén": l.get("WhsCode", "—"),
        } for _, l in grupo.iterrows()]

        items.append(Item(
            id=f"DLN-{doc_num}",
            title=f"DLN-{doc_num}",
            subtitle=f"{first['Cliente']} · {sucursal}",
            status="ok",  # VERIFICAR: cruzar con hora comprometida si la registran
            branch=sucursal,
            detail={
                "Cliente": first["Cliente"],
                "Código cliente": first.get("CardCode", "—"),
                "Pedido origen (DocEntry)": first.get("PedidoOrigenEntry", "—"),
                "Comentarios": first.get("Comments") or "—",
            },
            lines=lines,
        ))
    return items


# ---------------------------------------------------------------------------
# Facturas emitidas a clientes (OINV + INV1), del día
# ---------------------------------------------------------------------------
FACTURACION_SQL = """
SELECT
    T0.DocEntry, T0.DocNum, T0.CardCode, T0.CardName AS Cliente,
    T0.DocDate, T0.DocTotal, T0.PaidToDate,
    T1.LineNum, T1.ItemCode, T1.Dscription, T1.Quantity, T1.Price, T1.LineTotal
FROM OINV T0
JOIN INV1 T1 ON T1.DocEntry = T0.DocEntry
WHERE T0.DocDate = CONVERT(date, GETDATE())
ORDER BY T0.DocNum, T1.LineNum
"""


def facturacion_from_df(df: pd.DataFrame) -> list[Item]:
    items = []
    for doc_num, sucursal, first, grupo in _group_items(df, "DocNum"):
        saldo = (first.get("DocTotal", 0) or 0) - (first.get("PaidToDate", 0) or 0)
        lines = [{
            "Artículo": l.get("Dscription") or l.get("ItemCode"),
            "Cantidad facturada": l.get("Quantity"),
            "Precio unitario": f"${l['Price']:,.2f}" if pd.notna(l.get("Price")) else "—",
            "Importe": f"${l['LineTotal']:,.2f}" if pd.notna(l.get("LineTotal")) else "—",
        } for _, l in grupo.iterrows()]

        items.append(Item(
            id=f"Factura {doc_num}",
            title=f"Factura {doc_num}",
            subtitle=f"{first['Cliente']} · {sucursal}",
            status="ok",
            branch=sucursal,
            detail={
                "Cliente": first["Cliente"],
                "Código cliente": first.get("CardCode", "—"),
                "Monto": f"${first['DocTotal']:,.2f} MXN",
                "Saldo pendiente": f"${saldo:,.2f} MXN",
            },
            lines=lines,
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
