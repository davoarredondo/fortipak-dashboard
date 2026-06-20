"""
ui/components.py
------------------
Piezas reutilizables de la interfaz: la fila de KPIs, el banner de avisos
urgentes, y cada "carril" (lane) con sus tarjetas.

Sobre el diseño de cada tarjeta:
Cada tarjeta es un mini-recuadro (st.container(border=True)) con 3 líneas
siempre visibles, sin necesidad de hacer clic:
  - Estatus + identificador del documento (ej. "🟢 Pedido 1023")
  - A quién/qué corresponde (ej. "Cliente: Nissan Aguascalientes",
    "Proveedor: Aceros SA", "Almacén: PT-LEON → PT-SLP")
  - El dato de tiempo más relevante (ej. "Entrega: 16:00")
Debajo, un botón "Ver detalle" abre el popover con todo lo demás: datos
completos del documento y, si aplica, la tabla de partidas (con clic en
una fila para ver su detalle completo: solicitado, entregado, almacén,
stock).

Sobre los colores por sección:
Cada carril se dibuja dentro de un st.container(key=f"lane_{lane}", border=True).
Streamlit convierte ese "key" en una clase CSS (.st-key-lane_<lane>), y en
ui/styles.py pintamos esa clase con el color de esa categoría.
"""
import re

import pandas as pd
import streamlit as st

from data.constants import LANES, LANE_LABELS
from data.model import Item


def render_kpis(items_by_lane: dict[str, list[Item]]):
    with st.container(key="kpi_row", border=True):
        cols = st.columns(len(LANES))
        for col, lane in zip(cols, LANES):
            label, _ = LANE_LABELS[lane]
            col.metric(label, len(items_by_lane.get(lane, [])))


def render_urgent_banner(items_by_lane: dict[str, list[Item]]):
    urgent = []
    for lane in LANES:
        for item in items_by_lane.get(lane, []):
            if item.status == "danger":
                urgent.append((lane, item))

    if not urgent:
        return

    with st.container(key="urgent_banner", border=True):
        st.markdown(
            f'<p class="fp-lane-title">⚠️ {len(urgent)} elemento(s) requieren atención urgente</p>',
            unsafe_allow_html=True,
        )
        cols = st.columns(min(len(urgent), 3) or 1)
        for i, (lane, item) in enumerate(urgent):
            with cols[i % len(cols)]:
                _render_card(item, key_suffix=f"urgent_{lane}")


def _slug(text: str) -> str:
    return re.sub(r"[^a-zA-Z0-9]+", "_", text).strip("_").lower()


def _line_status(pendiente, stock) -> str:
    """Semáforo genérico cuando la categoría no trae ya su propio mensaje
    de estatus: compara lo pendiente contra el stock disponible."""
    try:
        pendiente = float(pendiente)
        stock = float(stock)
    except (TypeError, ValueError):
        return "—"
    if pendiente <= 0:
        return "🟢 Cubierto"
    if stock < pendiente:
        return f"🔴 Insuficiente, faltan {pendiente - stock:.0f}"
    if stock == pendiente:
        return "🟡 Justo, sin margen"
    return "🟢 Cubierto"


def _render_lines_table(lines: list[dict], widget_key: str):
    df = pd.DataFrame(lines)
    label_col = df.columns[0]

    if "Estatus" not in df.columns and {"Pendiente", "Stock en almacén"}.issubset(df.columns):
        df["Estatus"] = [
            _line_status(p, s) for p, s in zip(df["Pendiente"], df["Stock en almacén"])
        ]

    if "Pendiente" in df.columns:
        compact_cols = [c for c in [label_col, "Pendiente", "Estatus"] if c in df.columns]
    else:
        compact_cols = list(df.columns)

    event = st.dataframe(
        df, width="stretch", hide_index=True,
        column_order=compact_cols,
        on_select="rerun", selection_mode="single-row",
        key=widget_key,
    )

    selected_rows = event.selection.rows if event and event.selection else []
    if selected_rows:
        line = lines[selected_rows[0]]
        st.markdown(f"**Detalle completo — {line.get(label_col, '')}**")
        fields = [(k, v) for k, v in line.items() if k != label_col]
        detail_cols = st.columns(min(len(fields), 4) or 1)
        for i, (k, v) in enumerate(fields):
            detail_cols[i % len(detail_cols)].metric(k, v if v not in (None, "") else "—")
    else:
        st.caption("Haz clic en una fila para ver su detalle completo (solicitado, entregado, almacén, stock).")


def _render_card(item: Item, key_suffix: str = ""):
    with st.container(border=True):
        st.markdown(
            f'<p class="fp-mini-id">{item.status_icon} {item.title}</p>'
            f'<p class="fp-mini-related">{item.related or "&nbsp;"}</p>'
            f'<p class="fp-mini-when">{item.when or "&nbsp;"}</p>',
            unsafe_allow_html=True,
        )
        with st.popover("Ver detalle", width="stretch"):
            st.markdown(f'<p class="fp-card-title">{item.title}</p>', unsafe_allow_html=True)
            st.markdown(f'<p class="fp-card-subtitle">{item.subtitle}</p>', unsafe_allow_html=True)
            st.divider()
            for key, value in item.detail.items():
                st.write(f"**{key}:** {value}")

            if item.lines:
                st.divider()
                st.caption("Detalle por partida")
                widget_key = f"lines_{_slug(item.id)}_{key_suffix}"
                _render_lines_table(item.lines, widget_key)


def render_lane(lane: str, items: list[Item]):
    label, icon = LANE_LABELS[lane]
    with st.container(key=f"lane_{lane}", border=True):
        st.markdown(
            f'<p class="fp-lane-title"><i class="ti ti-{icon}"></i> {label} '
            f'<span class="fp-lane-count">({len(items)})</span></p>',
            unsafe_allow_html=True,
        )

        if not items:
            st.caption("Sin elementos por mostrar.")
            return

        cols_per_row = 3
        for i in range(0, len(items), cols_per_row):
            row_items = items[i:i + cols_per_row]
            cols = st.columns(cols_per_row)
            for col, item in zip(cols, row_items):
                with col:
                    _render_card(item, key_suffix=f"lane_{lane}")

        with st.expander("Ver tabla completa"):
            rows = []
            for it in items:
                row = {
                    "ID": it.id, "Sucursal": it.branch, "Estatus": it.status_icon,
                    "Relacionado": it.related, "Cuándo": it.when, **it.detail,
                }
                rows.append(row)
            st.dataframe(pd.DataFrame(rows), width="stretch", hide_index=True)


def render_branch_selector(branches_available: list[str], key: str = "branch_filter") -> list[str]:
    options = ["Todas"] + branches_available
    selected = st.segmented_control("Sucursal", options=options, default="Todas", key=key)
    if selected is None or selected == "Todas":
        return branches_available
    return [selected]
