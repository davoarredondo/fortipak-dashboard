"""
data/demo_data.py
------------------
Datos de ejemplo para que el dashboard funcione y se vea completo sin
necesidad de una conexión real a SAP. Útil para probar la interfaz y para
mostrarla antes de tener la conexión SQL/Service Layer configurada.

Cuando DEMO_MODE=false en el .env, este módulo deja de usarse.
"""
from data.model import Item


def get_demo_items() -> dict[str, list[Item]]:
    return {
        "recepciones": [
            Item("GRPO-4821", "GRPO-4821", "Aceros SA · León", "ok", "León",
                 {"Proveedor": "Aceros SA", "Almacén": "MP-LEON", "Hora": "09:10",
                  "Partidas": "12", "Comentarios": "Recepción completa"}),
            Item("GRPO-4822", "GRPO-4822", "Resinas del Bajío · Ags", "warn", "Aguascalientes",
                 {"Proveedor": "Resinas del Bajío", "Almacén": "MP-AGS", "Hora": "10:40",
                  "Partidas": "5", "Comentarios": "En revisión de calidad"}),
            Item("GRPO-4819", "GRPO-4819", "León · 2h de retraso", "danger", "León",
                 {"Proveedor": "Empaques del Centro", "Almacén": "MP-LEON",
                  "Hora estimada": "07:30", "Comentarios": "Aún no se presenta el transportista"}),
        ],
        "produccion": [
            Item("OF-1190", "OF-1190", "León · 80%", "ok", "León",
                 {"Producto": "Charola termoformada TR-220", "Avance": "80%",
                  "Fecha compromiso": "20-jun-2026", "Comentarios": "En tiempo"}),
            Item("OF-1191", "OF-1191", "Ags · espera material", "warn", "Aguascalientes",
                 {"Producto": "Empaque automotriz EA-310", "Avance": "30%",
                  "Fecha compromiso": "20-jun-2026", "Comentarios": "Falta resina, ver GRPO-4822"}),
            Item("OF-1188", "OF-1188", "SLP · 45%", "ok", "SLP",
                 {"Producto": "Charola ensamblada CE-115", "Avance": "45%",
                  "Fecha compromiso": "21-jun-2026", "Comentarios": "En tiempo"}),
        ],
        "traslados": [
            Item("WTR-77", "WTR-77", "León → SLP · 2h retraso", "danger", "SLP",
                 {"Origen": "León", "Destino": "SLP", "Solicitado": "07:00",
                  "Comentarios": "Camión retrasado en ruta"}),
            Item("WTR-81", "WTR-81", "Ags → León · en tránsito", "ok", "León",
                 {"Origen": "Aguascalientes", "Destino": "León", "Solicitado": "08:15",
                  "Comentarios": "Llega antes de las 14:00"}),
            Item("WTR-82", "WTR-82", "SLP → León · por confirmar", "warn", "León",
                 {"Origen": "SLP", "Destino": "León", "Solicitado": "09:50",
                  "Comentarios": "Esperando confirmación de almacén origen"}),
        ],
        "pedidos": [
            Item("Pedido 1021", "Pedido 1021", "Ternium · Ags · listo", "ok", "Aguascalientes",
                 {"Cliente": "Ternium Aguascalientes", "Entrega": "13:30",
                  "Partidas": "6", "Comentarios": "Ya facturado"}),
            Item("Pedido 1023", "Pedido 1023", "Nissan · Ags · 16:00", "warn", "Aguascalientes",
                 {"Cliente": "Nissan Aguascalientes", "Entrega": "16:00",
                  "Partidas": "3", "Comentarios": "En picking, 70% surtido"}),
            Item("Pedido 1025", "Pedido 1025", "Magna · SLP · sin picking", "danger", "SLP",
                 {"Cliente": "Magna SLP", "Entrega": "18:00",
                  "Partidas": "2", "Comentarios": "Picking aún no generado"}),
        ],
        "picking": [
            Item("PKL-330", "PKL-330", "León · lista para surtir", "ok", "León",
                 {"Pedido asociado": "Pedido 1018", "Almacén": "PT-LEON",
                  "Comentarios": "Lista, esperando surtidor"}),
            Item("PKL-331", "PKL-331", "Ags · surtiendo 70%", "warn", "Aguascalientes",
                 {"Pedido asociado": "Pedido 1023", "Almacén": "PT-AGS",
                  "Comentarios": "En proceso"}),
            Item("PKL-332", "PKL-332", "SLP · sin iniciar", "danger", "SLP",
                 {"Pedido asociado": "Pedido 1025", "Almacén": "PT-SLP",
                  "Comentarios": "Sin surtidor asignado"}),
        ],
        "entregas": [
            Item("DLN-902", "DLN-902", "León · ruta 1", "ok", "León",
                 {"Cliente": "Nissan Planta A", "Ruta": "Ruta 1",
                  "Comentarios": "En camino, hora estimada 12:30"}),
            Item("DLN-903", "DLN-903", "Ags · vence 17:00", "warn", "Aguascalientes",
                 {"Cliente": "Nissan Aguascalientes", "Ruta": "Ruta 2",
                  "Comentarios": "Sale en los próximos 30 min"}),
        ],
        "facturacion": [
            Item("Factura A-5510", "Factura A-5510", "León · timbrada", "ok", "León",
                 {"Cliente": "Ternium Aguascalientes", "Monto": "$184,300 MXN",
                  "Comentarios": "Timbrada correctamente"}),
            Item("3 entregas sin facturar", "3 entregas sin facturar", "Pendientes hoy", "warn", "Todas",
                 {"Comentarios": "DLN-899, DLN-900 y DLN-901 sin factura asociada"}),
        ],
    }
