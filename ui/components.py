"""
ui/components.py
------------------
Piezas reutilizables de la interfaz: la fila de KPIs, el banner de avisos
urgentes, y cada "carril" (lane) con sus tarjetas.

Sobre el detalle de cada tarjeta (MUY IMPORTANTE):
El detalle se abre en un st.dialog (modal centrado, ancho fijo grande),
NO en un st.popover. Un popover hereda el ancho de la columna angosta
donde vive su botón disparador, así que la tabla de partidas se cortaba.
Un modal es independiente de esa columna: siempre se ve ancho, y por eso
se pueden mostrar TODAS las columnas de la tabla de partidas de una sola
vez (Artículo, Solicitado, Entregado/Recibido, Pendiente, Almacén, Stock
en almacén) sin tener que hacer clic en cada línea para verlas.

st.dialog funciona como decorador: se define una sola vez, y para mostrar
datos distintos en cada llamada se guarda el item a mostrar en
st.session_state antes de invocar la función decorada.

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

ACTIVE_ITEM_KEY = "_fp_active_item"
DIALOG_OPEN_KEY = "_fp_dialog_open"


def _close_dialog():
    st.session_state[DIALOG_OPEN_KEY] = False


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


@st.dialog("Detalle del documento", width="large", on_dismiss=_close_dialog)
def _detail_dialog():
    item: Item = st.session_state.get(ACTIVE_ITEM_KEY)
    if not item:
        st.write("Sin información para mostrar.")
        return

    st.markdown(f'<p class="fp-card-title">{item.status_icon} {item.title}</p>', unsafe_allow_html=True)
    st.markdown(f'<p class="fp-card-subtitle">{item.subtitle}</p>', unsafe_allow_html=True)
    st.divider()

    for key, value in item.detail.items():
        st.write(f"**{key}:** {value}")

    if item.lines:
        st.divider()
        st.caption("Detalle por partida — todas las columnas visibles, sin necesidad de ampliar cada línea")
        df = pd.DataFrame(item.lines)
        if "Estatus" not in df.columns and {"Pendiente", "Stock en almacén"}.issubset(df.columns):
            df["Estatus"] = [
                _line_status(p, s) for p, s in zip(df["Pendiente"], df["Stock en almacén"])
            ]
        st.dataframe(
            df, width="stretch", hide_index=True, height=min(38 + 35 * len(df), 400),
            key=f"dialog_lines_{_slug(item.id)}",
        )


def _render_card(item: Item, key_suffix: str = ""):
    with st.container(border=True):
        st.markdown(
            f'<p class="fp-mini-id">{item.status_icon} {item.title}</p>'
            f'<p class="fp-mini-related">{item.related or "&nbsp;"}</p>'
            f'<p class="fp-mini-when">{item.when or "&nbsp;"}</p>',
            unsafe_allow_html=True,
        )
        btn_key = f"btn_{_slug(item.id)}_{key_suffix}"
        if st.button("Ver detalle", key=btn_key, width="stretch"):
            st.session_state[ACTIVE_ITEM_KEY] = item
            st.session_state[DIALOG_OPEN_KEY] = True


def maybe_reopen_dialog():
    """Si había un detalle abierto antes del último refresco automático,
    lo vuelve a mostrar en este run. Llamar una sola vez, al final del
    layout principal (después de dibujar todos los carriles)."""
    if st.session_state.get(DIALOG_OPEN_KEY):
        _detail_dialog()


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
