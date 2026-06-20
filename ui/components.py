"""
ui/components.py
------------------
Piezas reutilizables de la interfaz: la fila de KPIs, el banner de avisos
urgentes, y cada "carril" (lane) con sus tarjetas.

Sobre los colores por sección:
Cada carril se dibuja dentro de un st.container(key=f"lane_{lane}", border=True).
Streamlit convierte ese "key" en una clase CSS (.st-key-lane_<lane>), y en
ui/styles.py pintamos esa clase con el color de esa categoría. Así los
widgets nativos (columnas, botones, tablas) quedan de verdad dentro de la
tarjeta de color, no solo decorados por encima.

Sobre el clic para ver detalle:
Cada tarjeta es un st.popover: un botón que, al hacer clic, abre un panel
con el detalle completo sin recargar ni salir de la pantalla. Si el item
trae líneas (`item.lines`), se muestra además una tabla con el detalle por
partida — por ejemplo, en pedidos, cuánto falta por entregar de cada
artículo contra cuánto hay disponible en el almacén correspondiente.
"""
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
        cols = st.columns(min(len(urgent), 4) or 1)
        for i, (lane, item) in enumerate(urgent):
            with cols[i % len(cols)]:
                _render_item_popover(item)


def _render_item_popover(item: Item):
    label = f"{item.status_icon} {item.title}"
    with st.popover(label, width="stretch"):
        st.markdown(f'<p class="fp-card-title">{item.title}</p>', unsafe_allow_html=True)
        st.markdown(f'<p class="fp-card-subtitle">{item.subtitle}</p>', unsafe_allow_html=True)
        st.divider()
        for key, value in item.detail.items():
            st.write(f"**{key}:** {value}")

        if item.lines:
            st.divider()
            st.caption("Detalle por partida")
            df = pd.DataFrame(item.lines)
            st.dataframe(df, width="stretch", hide_index=True)


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

        cols_per_row = 4
        for i in range(0, len(items), cols_per_row):
            row_items = items[i:i + cols_per_row]
            cols = st.columns(cols_per_row)
            for col, item in zip(cols, row_items):
                with col:
                    _render_item_popover(item)

        with st.expander("Ver tabla completa"):
            rows = []
            for it in items:
                row = {"ID": it.id, "Sucursal": it.branch, "Estatus": it.status_icon, **it.detail}
                rows.append(row)
            st.dataframe(pd.DataFrame(rows), width="stretch", hide_index=True)


def render_branch_selector(branches_available: list[str], key: str = "branch_filter") -> list[str]:
    options = ["Todas"] + branches_available
    selected = st.segmented_control("Sucursal", options=options, default="Todas", key=key)
    if selected is None or selected == "Todas":
        return branches_available
    return [selected]
