"""
data/source.py
----------------
Punto único que usa la interfaz para pedir los datos del dashboard.
Decide internamente si usar datos de demostración o consultar SAP de verdad,
según DEMO_MODE en el archivo .env. El resto de la app no necesita saberlo.
"""
import config
from data.demo_data import get_demo_items
from data.model import Item


def get_dashboard_items(branches: list[str]) -> dict[str, list[Item]]:
    if config.DEMO_MODE:
        all_items = get_demo_items()
    else:
        from data.queries import get_live_items  # import diferido: evita requerir pyodbc en modo demo
        all_items = get_live_items(branches)

    # Filtra por sucursal (en modo demo también, para que el filtro se sienta real)
    filtered = {}
    for lane, items in all_items.items():
        filtered[lane] = [it for it in items if it.branch in branches or it.branch == "Todas"]
    return filtered
