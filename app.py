"""
app.py
-------
Punto de entrada de la app. Para correrla:

    streamlit run app.py

Flujo:
1. Si no hay sesión iniciada, muestra el formulario de login y valida
   contra SAP B1 Service Layer (o, en modo demo, acepta cualquier usuario).
2. Si ya hay sesión, muestra el dashboard: selector de sucursal, KPIs,
   avisos urgentes y los 7 carriles de operación.
"""
import streamlit as st
from streamlit_autorefresh import st_autorefresh

import config
from auth.sap_auth import login_to_sap, login_demo
from data.constants import LANES
from data.source import get_dashboard_items
from ui import components, styles

st.set_page_config(page_title="Centro de operaciones FORTIPAK", layout="wide")
styles.inject()

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
    st.session_state.user_name = None


def login_screen():
    st.markdown("## Centro de operaciones FORTIPAK")
    st.caption("Inicia sesión con tu usuario de SAP Business One")

    if config.DEMO_MODE:
        st.info("Modo demostración: cualquier usuario y contraseña son válidos.")

    with st.form("login_form"):
        username = st.text_input("Usuario")
        password = st.text_input("Contraseña", type="password")
        submitted = st.form_submit_button("Entrar", width='stretch')

    if submitted:
        if config.DEMO_MODE:
            result = login_demo(username, password)
        else:
            result = login_to_sap(
                service_layer_url=config.SAP_SERVICE_LAYER_URL,
                company_db=config.SAP_COMPANY_DB,
                username=username,
                password=password,
                verify_ssl=config.SAP_VERIFY_SSL,
            )

        if result.success:
            st.session_state.authenticated = True
            st.session_state.user_name = result.user_name
            st.rerun()
        else:
            st.error(result.error)


def dashboard():
    st_autorefresh(interval=config.REFRESH_INTERVAL_SECONDS * 1000, key="auto_refresh")

    header_left, header_right = st.columns([3, 2])
    with header_left:
        st.markdown(f"### Centro de operaciones FORTIPAK")
        st.markdown(
            f'<p class="fp-subtitle">Sesión: {st.session_state.user_name} '
            f'{"· modo demostración" if config.DEMO_MODE else ""}</p>',
            unsafe_allow_html=True,
        )
    with header_right:
        col_a, col_b = st.columns([4, 1])
        with col_a:
            selected_branches = components.render_branch_selector(config.BRANCHES)
        with col_b:
            st.write("")
            if st.button("🔄 Actualizar", width='stretch'):
                st.rerun()

    with st.spinner("Cargando información..."):
        items_by_lane = get_dashboard_items(selected_branches)

    components.render_urgent_banner(items_by_lane)
    components.render_kpis(items_by_lane)

    st.divider()

    for lane in LANES:
        components.render_lane(lane, items_by_lane.get(lane, []))

    with st.sidebar:
        st.markdown("#### Sesión")
        st.write(st.session_state.user_name)
        if st.button("Cerrar sesión"):
            st.session_state.authenticated = False
            st.session_state.user_name = None
            st.rerun()


if not st.session_state.authenticated:
    login_screen()
else:
    dashboard()
