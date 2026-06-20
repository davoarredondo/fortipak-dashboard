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

# clave -> color de acento, fondo claro y color de texto sobre ese fondo.
# Un color distinto por categoría (no por urgencia) para que las secciones
# se distingan entre sí de un vistazo, incluso antes de leer el contenido.
LANE_COLORS = {
    "recepciones": {"accent": "#1d4ed8", "bg": "#eff6ff", "text": "#1e3a8a"},
    "produccion":  {"accent": "#7c3aed", "bg": "#f5f3ff", "text": "#4c1d95"},
    "traslados":   {"accent": "#0d9488", "bg": "#f0fdfa", "text": "#0f766e"},
    "pedidos":     {"accent": "#b45309", "bg": "#fffbeb", "text": "#92400e"},
    "picking":     {"accent": "#be185d", "bg": "#fdf2f8", "text": "#9d174d"},
    "entregas":    {"accent": "#15803d", "bg": "#f0fdf4", "text": "#166534"},
    "facturacion": {"accent": "#475569", "bg": "#f8fafc", "text": "#334155"},
}
