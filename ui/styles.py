"""
ui/styles.py
-------------
Estilos visuales de la app. La idea central de este archivo: Streamlit ya
soporta dar una "clase CSS" a un st.container(key="algo") -> se renderiza
como `.st-key-algo` en el HTML. Usamos eso para pintar cada sección
(carril) con su propio color, sin necesidad de componentes externos.
"""
import streamlit as st

from data.constants import LANE_COLORS

BASE_CSS = """
<style>
.fp-subtitle { color: #6b7280; font-size: 0.85rem; margin: 0; }
.fp-lane-title {
    font-weight: 700; font-size: 1rem; margin: 0 0 0.6rem 0;
    display: flex; align-items: center; gap: 0.45rem;
}
.fp-lane-count { font-weight: 400; opacity: 0.65; font-size: 0.85rem; }
.fp-card-title { font-weight: 600; font-size: 0.85rem; margin: 0; }
.fp-card-subtitle { font-size: 0.78rem; opacity: 0.75; margin: 0; }

/* Banner de avisos urgentes: contenedor con key="urgent_banner" */
.st-key-urgent_banner {
    background: #fef2f2 !important;
    border: 1px solid #fca5a5 !important;
    border-radius: 12px !important;
}
.st-key-urgent_banner .fp-lane-title { color: #991b1b; }

/* Fila de KPIs: fondo neutro suave para diferenciarla de los carriles */
.st-key-kpi_row {
    background: #f8fafc !important;
    border-radius: 12px !important;
    border: 1px solid #e2e8f0 !important;
    padding-top: 0.4rem !important;
}
</style>
"""


def _lane_css(lane: str, colors: dict) -> str:
    # Cada carril es un st.container(key=f"lane_{lane}") -> clase .st-key-lane_<lane>
    return f"""
    .st-key-lane_{lane} {{
        background: {colors['bg']} !important;
        border-left: 6px solid {colors['accent']} !important;
        border-radius: 10px !important;
    }}
    .st-key-lane_{lane} .fp-lane-title {{ color: {colors['text']}; }}
    """


def inject():
    lane_css = "".join(_lane_css(lane, colors) for lane, colors in LANE_COLORS.items())
    st.markdown(BASE_CSS, unsafe_allow_html=True)
    st.markdown(f"<style>{lane_css}</style>", unsafe_allow_html=True)
