"""
ui/components.py
------------------
Piezas reutilizables de la interfaz: la fila de KPIs, el banner de avisos
urgentes, y cada "carril" (lane) con sus tarjetas.

Sobre el clic para ver detalle:
Cada tarjeta es un st.popover: un botón que, al hacer clic, abre un panel
con el detalle completo sin recargar ni salir de la pantalla. El círculo de
color (🟢🟡🔴) indica la urgencia de un vistazo, igual que en el diseño
aprobado.
"""
import streamlit as st

from data.constants import LANES, LANE_LABELS
from data.model import Item


def render_kpis(items_by_lane: dict[str, list[Item]]):
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

    st.markdown(
        f'<div class="fp-alert-banner"><p class="fp-alert-title">'
        f'⚠️ {len(urgent)} elemento(s) requieren atención urgente</p></div>',
        unsafe_allow_html=True,
    )
    cols = st.columns(min(len(urgent), 5) or 1)
    for col, (lane, item) in zip(cols * (len(urgent) // len(cols) + 1), urgent):
        with col:
            _render_item_popover(item)


def _render_item_popover(item: Item):
    label = f"{item.status_icon} {item.title}"
    with st.popover(label, width='stretch'):
        st.markdown(f"**{item.title}**")
        st.caption(item.subtitle)
        for key, value in item.detail.items():
            st.write(f"**{key}:** {value}")


def render_lane(lane: str, items: list[Item]):
    label, icon = LANE_LABELS[lane]
    st.markdown(
        f'<p class="fp-lane-title"><i class="ti ti-{icon}"></i> {label} '
        f'<span style="color:#9ca3af;font-weight:400;">({len(items)})</span></p>',
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
        import pandas as pd
        rows = [{"ID": it.id, "Sucursal": it.branch, "Estatus": it.status_icon, **it.detail} for it in items]
        st.dataframe(pd.DataFrame(rows), width='stretch', hide_index=True)


def render_branch_selector(branches_available: list[str], key: str = "branch_filter") -> list[str]:
    options = ["Todas"] + branches_available
    selected = st.segmented_control("Sucursal", options=options, default="Todas", key=key)
    if selected is None or selected == "Todas":
        return branches_available
    return [selected]
