"""
data/constants.py
-------------------
Orden y etiquetas de las 7 categorías del dashboard. Vive aparte para que
tanto los datos demo como los datos reales (y la interfaz) usen la misma
fuente de verdad.
"""

LANES = [
    "recepciones",
    "produccion",
    "traslados",
    "pedidos",
    "picking",
    "entregas",
    "facturacion",
]

# clave -> (etiqueta visible, ícono Tabler)
LANE_LABELS = {
    "recepciones": ("Recepciones", "truck-delivery"),
    "produccion": ("Producción", "settings-automation"),
    "traslados": ("Traslados", "arrows-exchange"),
    "pedidos": ("Pedidos a entregar hoy", "clipboard-list"),
    "picking": ("Picking", "package"),
    "entregas": ("Entregas", "truck"),
    "facturacion": ("Facturación", "file-invoice"),
}
