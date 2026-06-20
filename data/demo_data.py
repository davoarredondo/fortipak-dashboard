"""
data/demo_data.py
------------------
Datos de ejemplo para que el dashboard funcione y se vea completo sin
necesidad de una conexión real a SAP.

Cada partida en "lines" sigue el mismo esquema en las 7 categorías, para
que el detalle se lea igual sin importar el tipo de documento:
    Artículo · Solicitado · Entregado/Recibido · Pendiente · Almacén · Stock en almacén
(en Pedidos además se incluye "Estatus" con el mensaje exacto del faltante,
en vez de dejar que se calcule de forma genérica).

Cuando DEMO_MODE=false en el .env, este módulo deja de usarse.
"""
from data.model import Item


def get_demo_items() -> dict[str, list[Item]]:
    return {
        "recepciones": [
            Item("GRPO-4821", "GRPO-4821", "Aceros SA · León", "ok", "León",
                 related="Proveedor: Aceros SA", when="Hora: 09:10", detail={
                "Proveedor": "Aceros SA", "Código proveedor": "P-0042",
                "Fecha": "20-jun-2026", "Hora": "09:10", "Monto": "$96,400 MXN",
                "Referencia proveedor": "FAC-88210", "Comentarios": "Recepción completa",
            }, lines=[
                {"Artículo": "Lámina de acero cal. 20", "Solicitado": 800, "Entregado/Recibido": 800,
                 "Pendiente": 0, "Almacén": "MP-LEON", "Stock en almacén": 1450},
                {"Artículo": "Lámina de acero cal. 24", "Solicitado": 450, "Entregado/Recibido": 450,
                 "Pendiente": 0, "Almacén": "MP-LEON", "Stock en almacén": 920},
                {"Artículo": "Solvente desengrasante", "Solicitado": 60, "Entregado/Recibido": 60,
                 "Pendiente": 0, "Almacén": "MP-LEON", "Stock en almacén": 140},
            ]),
            Item("GRPO-4822", "GRPO-4822", "Resinas del Bajío · Ags", "warn", "Aguascalientes",
                 related="Proveedor: Resinas del Bajío", when="Hora: 10:40", detail={
                "Proveedor": "Resinas del Bajío", "Código proveedor": "P-0118",
                "Fecha": "20-jun-2026", "Hora": "10:40", "Monto": "$41,200 MXN",
                "Referencia proveedor": "FAC-11932", "Comentarios": "Recepción parcial, en revisión de calidad",
            }, lines=[
                {"Artículo": "Resina PP copolímero", "Solicitado": 1500, "Entregado/Recibido": 1200,
                 "Pendiente": 300, "Almacén": "MP-AGS", "Stock en almacén": 1200},
                {"Artículo": "Pigmento negro masterbatch", "Solicitado": 80, "Entregado/Recibido": 80,
                 "Pendiente": 0, "Almacén": "MP-AGS", "Stock en almacén": 80},
            ]),
            Item("GRPO-4819", "GRPO-4819", "León · 2h de retraso", "danger", "León",
                 related="Proveedor: Empaques del Centro", when="Esperado: 07:30", detail={
                "Proveedor": "Empaques del Centro", "Código proveedor": "P-0076",
                "Hora estimada": "07:30", "Comentarios": "Aún no se presenta el transportista",
            }, lines=[
                {"Artículo": "Cartón corrugado triple", "Solicitado": 2000, "Entregado/Recibido": 0,
                 "Pendiente": 2000, "Almacén": "MP-LEON", "Stock en almacén": 150},
                {"Artículo": "Cinta de embalaje", "Solicitado": 300, "Entregado/Recibido": 0,
                 "Pendiente": 300, "Almacén": "MP-LEON", "Stock en almacén": 40},
            ]),
        ],
        "produccion": [
            Item("OF-1190", "OF-1190", "León · 80%", "ok", "León",
                 related="Producto: Charola termoformada TR-220", when="Compromiso: 20-jun-2026", detail={
                "Producto": "Charola termoformada TR-220", "Código artículo": "TR-220",
                "Cantidad planeada": "600", "Cantidad completada": "480",
                "Avance": "80%", "Fecha compromiso": "20-jun-2026", "Comentarios": "En tiempo",
            }, lines=[
                {"Artículo": "Lámina de acero cal. 20", "Solicitado": 600, "Entregado/Recibido": 600,
                 "Pendiente": 0, "Almacén": "MP-LEON", "Stock en almacén": 850},
                {"Artículo": "Resina PP copolímero", "Solicitado": 240, "Entregado/Recibido": 192,
                 "Pendiente": 48, "Almacén": "MP-LEON", "Stock en almacén": 300},
            ]),
            Item("OF-1191", "OF-1191", "Ags · espera material", "warn", "Aguascalientes",
                 related="Producto: Empaque automotriz EA-310", when="Compromiso: 20-jun-2026", detail={
                "Producto": "Empaque automotriz EA-310", "Código artículo": "EA-310",
                "Cantidad planeada": "400", "Cantidad completada": "120",
                "Avance": "30%", "Fecha compromiso": "20-jun-2026",
                "Comentarios": "Falta resina, ver GRPO-4822",
            }, lines=[
                {"Artículo": "Resina PP copolímero", "Solicitado": 480, "Entregado/Recibido": 144,
                 "Pendiente": 336, "Almacén": "MP-AGS", "Stock en almacén": 120},
                {"Artículo": "Pigmento negro masterbatch", "Solicitado": 32, "Entregado/Recibido": 32,
                 "Pendiente": 0, "Almacén": "MP-AGS", "Stock en almacén": 48},
            ]),
            Item("OF-1188", "OF-1188", "SLP · 45%", "ok", "SLP",
                 related="Producto: Charola ensamblada CE-115", when="Compromiso: 21-jun-2026", detail={
                "Producto": "Charola ensamblada CE-115", "Código artículo": "CE-115",
                "Cantidad planeada": "300", "Cantidad completada": "135",
                "Avance": "45%", "Fecha compromiso": "21-jun-2026", "Comentarios": "En tiempo",
            }, lines=[
                {"Artículo": "Lámina de acero cal. 24", "Solicitado": 300, "Entregado/Recibido": 135,
                 "Pendiente": 165, "Almacén": "MP-SLP", "Stock en almacén": 400},
                {"Artículo": "Separador CE-115-S", "Solicitado": 300, "Entregado/Recibido": 135,
                 "Pendiente": 165, "Almacén": "PT-SLP", "Stock en almacén": 200},
            ]),
        ],
        "traslados": [
            Item("WTR-77", "WTR-77", "León → SLP · 2h retraso", "danger", "SLP",
                 related="Almacén: PT-LEON → PT-SLP", when="Solicitado: 07:00", detail={
                "Origen": "León (PT-LEON)", "Destino": "SLP (PT-SLP)",
                "Solicitado el": "20-jun-2026 07:00", "Comentarios": "Camión retrasado en ruta",
            }, lines=[
                {"Artículo": "Charola TR-220", "Solicitado": 200, "Entregado/Recibido": 0,
                 "Pendiente": 200, "Almacén": "PT-LEON (origen)", "Stock en almacén": 540},
                {"Artículo": "Tapa TR-220", "Solicitado": 200, "Entregado/Recibido": 0,
                 "Pendiente": 200, "Almacén": "PT-LEON (origen)", "Stock en almacén": 320},
                {"Artículo": "Separador CE-115-S", "Solicitado": 100, "Entregado/Recibido": 0,
                 "Pendiente": 100, "Almacén": "PT-LEON (origen)", "Stock en almacén": 90},
            ]),
            Item("WTR-81", "WTR-81", "Ags → León · en tránsito", "ok", "León",
                 related="Almacén: PT-AGS → PT-LEON", when="Solicitado: 08:15", detail={
                "Origen": "Aguascalientes (PT-AGS)", "Destino": "León (PT-LEON)",
                "Solicitado el": "20-jun-2026 08:15", "Comentarios": "Llega antes de las 14:00",
            }, lines=[
                {"Artículo": "Empaque EA-310", "Solicitado": 150, "Entregado/Recibido": 0,
                 "Pendiente": 150, "Almacén": "PT-AGS (origen)", "Stock en almacén": 200},
                {"Artículo": "Espuma protectora EA-310-E", "Solicitado": 150, "Entregado/Recibido": 0,
                 "Pendiente": 150, "Almacén": "PT-AGS (origen)", "Stock en almacén": 95},
            ]),
            Item("WTR-82", "WTR-82", "SLP → León · por confirmar", "warn", "León",
                 related="Almacén: MP-SLP → MP-LEON", when="Solicitado: 09:50", detail={
                "Origen": "SLP (MP-SLP)", "Destino": "León (MP-LEON)",
                "Solicitado el": "20-jun-2026 09:50",
                "Comentarios": "Esperando confirmación de almacén origen",
            }, lines=[
                {"Artículo": "Resina PP copolímero", "Solicitado": 300, "Entregado/Recibido": 0,
                 "Pendiente": 300, "Almacén": "MP-SLP (origen)", "Stock en almacén": 280},
                {"Artículo": "Lámina de acero cal. 20", "Solicitado": 250, "Entregado/Recibido": 0,
                 "Pendiente": 250, "Almacén": "MP-SLP (origen)", "Stock en almacén": 600},
                {"Artículo": "Solvente desengrasante", "Solicitado": 40, "Entregado/Recibido": 0,
                 "Pendiente": 40, "Almacén": "MP-SLP (origen)", "Stock en almacén": 55},
                {"Artículo": "Cinta de embalaje", "Solicitado": 90, "Entregado/Recibido": 0,
                 "Pendiente": 90, "Almacén": "MP-SLP (origen)", "Stock en almacén": 70},
            ]),
        ],
        "pedidos": [
            Item("Pedido 1021", "Pedido 1021", "Ternium · Ags · listo", "ok", "Aguascalientes",
                 related="Cliente: Ternium Aguascalientes", when="Entrega: 13:30", detail={
                "Cliente": "Ternium Aguascalientes", "Código cliente": "C-0210",
                "Vendedor": "Laura Méndez", "Entrega comprometida": "20-jun-2026 13:30",
                "Monto": "$184,300 MXN", "Comentarios": "Ya facturado",
            }, lines=[
                {"Artículo": "Charola TR-220", "Solicitado": 350, "Entregado/Recibido": 350,
                 "Pendiente": 0, "Almacén": "PT-AGS", "Stock en almacén": 540, "Estatus": "🟢 Cubierto"},
                {"Artículo": "Tapa TR-220", "Solicitado": 350, "Entregado/Recibido": 350,
                 "Pendiente": 0, "Almacén": "PT-AGS", "Stock en almacén": 320, "Estatus": "🟢 Cubierto"},
            ]),
            Item("Pedido 1023", "Pedido 1023", "Nissan · Ags · 16:00", "warn", "Aguascalientes",
                 related="Cliente: Nissan Aguascalientes", when="Entrega: 16:00", detail={
                "Cliente": "Nissan Aguascalientes", "Código cliente": "C-0087",
                "Vendedor": "Laura Méndez", "Entrega comprometida": "20-jun-2026 16:00",
                "Monto": "$67,900 MXN", "Comentarios": "En picking, 70% surtido",
            }, lines=[
                {"Artículo": "Empaque EA-310", "Solicitado": 150, "Entregado/Recibido": 30,
                 "Pendiente": 120, "Almacén": "PT-AGS", "Stock en almacén": 200, "Estatus": "🟢 Cubierto"},
                {"Artículo": "Espuma protectora EA-310-E", "Solicitado": 150, "Entregado/Recibido": 70,
                 "Pendiente": 80, "Almacén": "PT-AGS", "Stock en almacén": 95, "Estatus": "🟢 Cubierto"},
                {"Artículo": "Charola interior EA-310-C", "Solicitado": 40, "Entregado/Recibido": 0,
                 "Pendiente": 40, "Almacén": "PT-AGS", "Stock en almacén": 40, "Estatus": "🟡 Justo, sin margen"},
            ]),
            Item("Pedido 1025", "Pedido 1025", "Magna · SLP · sin picking", "danger", "SLP",
                 related="Cliente: Magna SLP", when="Entrega: 18:00", detail={
                "Cliente": "Magna SLP", "Código cliente": "C-0305",
                "Vendedor": "Jorge Salinas", "Entrega comprometida": "20-jun-2026 18:00",
                "Monto": "$112,500 MXN",
                "Comentarios": "Picking aún no generado — stock insuficiente en 1 artículo",
            }, lines=[
                {"Artículo": "Charola CE-115", "Solicitado": 300, "Entregado/Recibido": 0,
                 "Pendiente": 300, "Almacén": "PT-SLP", "Stock en almacén": 180,
                 "Estatus": "🔴 Insuficiente, faltan 120"},
                {"Artículo": "Separador CE-115-S", "Solicitado": 150, "Entregado/Recibido": 0,
                 "Pendiente": 150, "Almacén": "PT-SLP", "Stock en almacén": 150, "Estatus": "🟡 Justo, sin margen"},
            ]),
        ],
        "picking": [
            Item("PKL-330", "PKL-330", "León · lista para surtir", "ok", "León",
                 related="Almacén: PT-LEON", when="Pedido: 1018", detail={
                "Pedido asociado": "Pedido 1018", "Comentarios": "Lista, esperando surtidor",
            }, lines=[
                {"Artículo": "Charola TR-220", "Solicitado": 60, "Entregado/Recibido": 0,
                 "Pendiente": 60, "Almacén": "PT-LEON", "Stock en almacén": 540},
            ]),
            Item("PKL-331", "PKL-331", "Ags · surtiendo 70%", "warn", "Aguascalientes",
                 related="Almacén: PT-AGS", when="Pedido: 1023", detail={
                "Pedido asociado": "Pedido 1023", "Comentarios": "En proceso",
            }, lines=[
                {"Artículo": "Empaque EA-310", "Solicitado": 120, "Entregado/Recibido": 90,
                 "Pendiente": 30, "Almacén": "PT-AGS", "Stock en almacén": 200},
                {"Artículo": "Espuma protectora EA-310-E", "Solicitado": 80, "Entregado/Recibido": 50,
                 "Pendiente": 30, "Almacén": "PT-AGS", "Stock en almacén": 95},
            ]),
            Item("PKL-332", "PKL-332", "SLP · sin iniciar", "danger", "SLP",
                 related="Almacén: PT-SLP", when="Pedido: 1025", detail={
                "Pedido asociado": "Pedido 1025",
                "Comentarios": "Sin surtidor asignado — revisar stock antes de iniciar",
            }, lines=[
                {"Artículo": "Charola CE-115", "Solicitado": 300, "Entregado/Recibido": 0,
                 "Pendiente": 300, "Almacén": "PT-SLP", "Stock en almacén": 180},
            ]),
        ],
        "entregas": [
            Item("DLN-902", "DLN-902", "León · ruta 1", "ok", "León",
                 related="Cliente: Nissan Planta A", when="Salida: 11:45", detail={
                "Cliente": "Nissan Planta A", "Código cliente": "C-0091",
                "Ruta / transportista": "Ruta 1 · Transportes Bajío", "Hora salida": "11:45",
                "Monto": "$58,200 MXN", "Pedido origen": "Pedido 1018",
                "Comentarios": "En camino, hora estimada 12:30",
            }, lines=[
                {"Artículo": "Charola TR-220", "Solicitado": 60, "Entregado/Recibido": 60,
                 "Pendiente": 0, "Almacén": "PT-LEON", "Stock en almacén": 480},
                {"Artículo": "Tapa TR-220", "Solicitado": 60, "Entregado/Recibido": 60,
                 "Pendiente": 0, "Almacén": "PT-LEON", "Stock en almacén": 260},
            ]),
            Item("DLN-903", "DLN-903", "Ags · vence 17:00", "warn", "Aguascalientes",
                 related="Cliente: Nissan Aguascalientes", when="Sale antes de: 17:00", detail={
                "Cliente": "Nissan Aguascalientes", "Código cliente": "C-0087",
                "Ruta / transportista": "Ruta 2 · Flota propia", "Monto": "$67,900 MXN",
                "Pedido origen": "Pedido 1023", "Comentarios": "Sale en los próximos 30 min",
            }, lines=[
                {"Artículo": "Empaque EA-310", "Solicitado": 120, "Entregado/Recibido": 120,
                 "Pendiente": 0, "Almacén": "PT-AGS", "Stock en almacén": 80},
                {"Artículo": "Espuma protectora EA-310-E", "Solicitado": 80, "Entregado/Recibido": 80,
                 "Pendiente": 0, "Almacén": "PT-AGS", "Stock en almacén": 15},
            ]),
        ],
        "facturacion": [
            Item("Factura A-5510", "Factura A-5510", "León · timbrada", "ok", "León",
                 related="Cliente: Ternium Aguascalientes", when="Fecha: 20-jun-2026", detail={
                "Cliente": "Ternium Aguascalientes", "Código cliente": "C-0210",
                "Fecha": "20-jun-2026", "Monto": "$184,300 MXN", "Saldo pendiente": "$0 MXN",
                "Entrega origen": "DLN-895", "Comentarios": "Timbrada correctamente",
            }, lines=[
                {"Artículo": "Charola TR-220", "Solicitado": 350, "Entregado/Recibido": 350,
                 "Pendiente": 0, "Almacén": "—", "Stock en almacén": "—"},
                {"Artículo": "Tapa TR-220", "Solicitado": 350, "Entregado/Recibido": 350,
                 "Pendiente": 0, "Almacén": "—", "Stock en almacén": "—"},
            ]),
            Item("3 entregas sin facturar", "3 entregas sin facturar", "Pendientes hoy", "warn", "Todas",
                 related="Varios clientes", when="Pendiente desde: hoy", detail={
                "Comentarios": "DLN-899, DLN-900 y DLN-901 sin factura asociada",
            }, lines=[
                {"Entrega": "DLN-899", "Cliente": "Magna SLP", "Monto": "$41,200.00"},
                {"Entrega": "DLN-900", "Cliente": "Ternium Aguascalientes", "Monto": "$28,900.00"},
                {"Entrega": "DLN-901", "Cliente": "Nissan Planta A", "Monto": "$53,100.00"},
            ]),
        ],
    }
