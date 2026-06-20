"""
ui/styles.py
-------------
Estilos visuales de la app. Streamlit no trae "tarjetas de color" como
componente nativo, así que usamos un poco de CSS propio para que el
banner de avisos urgentes y los encabezados de cada sección se vean como
en el diseño aprobado.
"""
import streamlit as st

CUSTOM_CSS = """
<style>
.fp-header {
    display: flex; justify-content: space-between; align-items: center;
    margin-bottom: 0.5rem;
}
.fp-subtitle { color: #6b7280; font-size: 0.85rem; margin: 0; }
.fp-lane-title {
    font-weight: 600; font-size: 0.95rem; margin: 1.1rem 0 0.3rem 0;
    display: flex; align-items: center; gap: 0.4rem;
}
.fp-alert-banner {
    background: #FCEBEB; border: 1px solid #F09595; border-radius: 10px;
    padding: 0.9rem 1.1rem; margin-bottom: 1rem;
}
.fp-alert-title { color: #791F1F; font-weight: 600; font-size: 0.9rem; margin: 0 0 0.5rem 0; }
</style>
"""


def inject():
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)
