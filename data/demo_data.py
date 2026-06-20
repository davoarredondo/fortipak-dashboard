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
            Item("GRPO-4821", "GRPO-4821", "Aceros SA · León", "ok", "León", {
                "Proveedor": "Aceros SA", "Código proveedor": "P-0042",
                "Almacén": "MP-LEON", "Fecha": "20-jun-2026", "Hora": "09:10",
                "Partidas": "12", "Monto": "$96,400 MXN",
                "Referencia proveedor": "FAC-88210",
                "Comentarios": "Recepción completa",
            }),
            Item("GRPO-4822", "GRPO-4822", "Resinas del Bajío · Ags", "warn", "Aguascalientes", {
                "Proveedor": "Resinas del Bajío", "Código proveedor": "P-0118",
                "Almacén": "MP-AGS", "Fecha": "20-jun-2026", "Hora": "10:40",
                "Partidas": "5", "Monto": "$41,200 MXN",
                "Referencia proveedor": "FAC-11932",
                "Comentarios": "En revisión de calidad",
            }),
            Item("GRPO-4819", "GRPO-4819", "León · 2h de retraso", "danger", "León", {
                "Proveedor": "Empaques del Centro", "Código proveedor": "P-0076",
                "Almacén": "MP-LEON", "Hora estimada": "07:30",
                "Partidas": "8", "Comentarios": "Aún no se presenta el transportista",
            }),
        ],
        "produccion": [
            Item("OF-1190", "OF-1190", "León · 80%", "ok", "León", {
                "Producto": "Charola termoformada TR-220", "Código artículo": "TR-220",
                "Almacén": "PT-LEON", "Cantidad planeada": "600", "Cantidad completada": "480",
                "Avance": "80%", "Fecha compromiso": "20-jun-2026", "Comentarios": "En tiempo",
            }),
            Item("OF-1191", "OF-1191", "Ags · espera material", "warn", "Aguascalientes", {
                "Producto": "Empaque automotriz EA-310", "Código artículo": "EA-310",
                "Almacén": "PT-AGS", "Cantidad planeada": "400", "Cantidad completada": "120",
                "Avance": "30%", "Fecha compromiso": "20-jun-2026",
                "Comentarios": "Falta resina, ver GRPO-4822",
            }),
            Item("OF-1188", "OF-1188", "SLP · 45%", "ok", "SLP", {
                "Producto": "Charola ensamblada CE-115", "Código artículo": "CE-115",
                "Almacén": "PT-SLP", "Cantidad planeada": "300", "Cantidad completada": "135",
                "Avance": "45%", "Fecha compromiso": "21-jun-2026", "Comentarios": "En tiempo",
            }),
        ],
        "traslados": [
            Item("WTR-77", "WTR-77", "León → SLP · 2h retraso", "danger", "SLP", {
                "Origen": "León (PT-LEON)", "Destino": "SLP (PT-SLP)",
                "Solicitado": "20-jun-2026 07:00", "Días transcurridos": "0 (2h tarde vs. lo previsto)",
                "Partidas": "3", "Comentarios": "Camión retrasado en ruta",
            }),
            Item("WTR-81", "WTR-81", "Ags → León · en tránsito", "ok", "León", {
                "Origen": "Aguascalientes (PT-AGS)", "Destino": "León (PT-LEON)",
                "Solicitado": "20-jun-2026 08:15", "Partidas": "2",
                "Comentarios": "Llega antes de las 14:00",
            }),
            Item("WTR-82", "WTR-82", "SLP → León · por confirmar", "warn", "León", {
                "Origen": "SLP (MP-SLP)", "Destino": "León (MP-LEON)",
                "Solicitado": "20-jun-2026 09:50", "Partidas": "4",
                "Comentarios": "Esperando confirmación de almacén origen",
            }),
        ],
        "pedidos": [
            Item("Pedido 1021", "Pedido 1021", "Ternium · Ags · listo", "ok", "Aguascalientes", {
                "Cliente": "Ternium Aguascalientes", "Código cliente": "C-0210",
                "Vendedor": "Laura Méndez", "Almacén de necesidad": "PT-AGS",
                "Entrega comprometida": "20-jun-2026 13:30", "Monto": "$184,300 MXN",
                "Comentarios": "Ya facturado",
            }, lines=[
                {"Artículo": "Charola TR-220", "Pendiente por entregar": 0,
                 "Stock disponible (PT-AGS)": 540, "Estatus": "🟢 Cubierto"},
                {"Artículo": "Tapa TR-220", "Pendiente por entregar": 0,
                 "Stock disponible (PT-AGS)": 320, "Estatus": "🟢 Cubierto"},
            ]),
            Item("Pedido 1023", "Pedido 1023", "Nissan · Ags · 16:00", "warn", "Aguascalientes", {
                "Cliente": "Nissan Aguascalientes", "Código cliente": "C-0087",
                "Vendedor": "Laura Méndez", "Almacén de necesidad": "PT-AGS",
                "Entrega comprometida": "20-jun-2026 16:00", "Monto": "$67,900 MXN",
                "Comentarios": "En picking, 70% surtido",
            }, lines=[
                {"Artículo": "Empaque EA-310", "Pendiente por entregar": 120,
                 "Stock disponible (PT-AGS)": 200, "Estatus": "🟢 Cubierto"},
                {"Artículo": "Espuma protectora EA-310-E", "Pendiente por entregar": 80,
                 "Stock disponible (PT-AGS)": 95, "Estatus": "🟢 Cubierto"},
                {"Artículo": "Charola interior EA-310-C", "Pendiente por entregar": 40,
                 "Stock disponible (PT-AGS)": 40, "Estatus": "🟡 Justo, sin margen"},
            ]),
            Item("Pedido 1025", "Pedido 1025", "Magna · SLP · sin picking", "danger", "SLP", {
                "Cliente": "Magna SLP", "Código cliente": "C-0305",
                "Vendedor": "Jorge Salinas", "Almacén de necesidad": "PT-SLP",
                "Entrega comprometida": "20-jun-2026 18:00", "Monto": "$112,500 MXN",
                "Comentarios": "Picking aún no generado — stock insuficiente en 1 artículo",
            }, lines=[
                {"Artículo": "Charola CE-115", "Pendiente por entregar": 300,
                 "Stock disponible (PT-SLP)": 180, "Estatus": "🔴 Insuficiente, faltan 120"},
                {"Artículo": "Separador CE-115-S", "Pendiente por entregar": 150,
                 "Stock disponible (PT-SLP)": 150, "Estatus": "🟡 Justo, sin margen"},
            ]),
        ],
        "picking": [
            Item("PKL-330", "PKL-330", "León · lista para surtir", "ok", "León", {
                "Pedido asociado": "Pedido 1018", "Almacén": "PT-LEON",
                "Comentarios": "Lista, esperando surtidor",
            }, lines=[
                {"Artículo": "Charola TR-220", "A surtir": 60, "Ya surtido": 0, "Pendiente": 60},
            ]),
            Item("PKL-331", "PKL-331", "Ags · surtiendo 70%", "warn", "Aguascalientes", {
                "Pedido asociado": "Pedido 1023", "Almacén": "PT-AGS",
                "Comentarios": "En proceso",
            }, lines=[
                {"Artículo": "Empaque EA-310", "A surtir": 120, "Ya surtido": 90, "Pendiente": 30},
                {"Artículo": "Espuma protectora EA-310-E", "A surtir": 80, "Ya surtido": 50, "Pendiente": 30},
            ]),
            Item("PKL-332", "PKL-332", "SLP · sin iniciar", "danger", "SLP", {
                "Pedido asociado": "Pedido 1025", "Almacén": "PT-SLP",
                "Comentarios": "Sin surtidor asignado — revisar stock antes de iniciar",
            }, lines=[
                {"Artículo": "Charola CE-115", "A surtir": 300, "Ya surtido": 0, "Pendiente": 300},
            ]),
        ],
        "entregas": [
            Item("DLN-902", "DLN-902", "León · ruta 1", "ok", "León", {
                "Cliente": "Nissan Planta A", "Código cliente": "C-0091",
                "Almacén": "PT-LEON", "Ruta / transportista": "Ruta 1 · Transportes Bajío",
                "Hora salida": "11:45", "Partidas": "4", "Monto": "$58,200 MXN",
                "Pedido origen": "Pedido 1018",
                "Comentarios": "En camino, hora estimada 12:30",
            }),
            Item("DLN-903", "DLN-903", "Ags · vence 17:00", "warn", "Aguascalientes", {
                "Cliente": "Nissan Aguascalientes", "Código cliente": "C-0087",
                "Almacén": "PT-AGS", "Ruta / transportista": "Ruta 2 · Flota propia",
                "Partidas": "3", "Monto": "$67,900 MXN", "Pedido origen": "Pedido 1023",
                "Comentarios": "Sale en los próximos 30 min",
            }),
        ],
        "facturacion": [
            Item("Factura A-5510", "Factura A-5510", "León · timbrada", "ok", "León", {
                "Cliente": "Ternium Aguascalientes", "Código cliente": "C-0210",
                "Fecha": "20-jun-2026", "Monto": "$184,300 MXN", "Saldo pendiente": "$0 MXN",
                "Entrega origen": "DLN-895", "Comentarios": "Timbrada correctamente",
            }),
            Item("3 entregas sin facturar", "3 entregas sin facturar", "Pendientes hoy", "warn", "Todas", {
                "Comentarios": "DLN-899, DLN-900 y DLN-901 sin factura asociada",
            }),
        ],
    }
