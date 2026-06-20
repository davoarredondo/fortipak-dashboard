"""
data/demo_data.py
------------------
Datos de ejemplo para que el dashboard funcione y se vea completo sin
necesidad de una conexión real a SAP. Útil para probar la interfaz y para
mostrarla antes de tener la conexión SQL/Service Layer configurada.

Cada Item incluye "lines": el detalle por partida del documento, para que
desde cualquier tarjeta se pueda ver exactamente qué contiene (qué se
recibió, qué se va a entregar, qué componentes le faltan a una orden de
fabricación, etc.) sin tener que salir de la app.

Cuando DEMO_MODE=false en el .env, este módulo deja de usarse.
"""
from data.model import Item


def get_demo_items() -> dict[str, list[Item]]:
    return {
        "recepciones": [
            Item("GRPO-4821", "GRPO-4821", "Aceros SA · León", "ok", "León", {
                "Proveedor": "Aceros SA", "Código proveedor": "P-0042",
                "Almacén": "MP-LEON", "Fecha": "20-jun-2026", "Hora": "09:10",
                "Monto": "$96,400 MXN", "Referencia proveedor": "FAC-88210",
                "Comentarios": "Recepción completa",
            }, lines=[
                {"Artículo": "Lámina de acero cal. 20", "Cantidad recibida": 800,
                 "Precio unitario": "$62.00", "Almacén": "MP-LEON"},
                {"Artículo": "Lámina de acero cal. 24", "Cantidad recibida": 450,
                 "Precio unitario": "$54.50", "Almacén": "MP-LEON"},
                {"Artículo": "Solvente desengrasante", "Cantidad recibida": 60,
                 "Precio unitario": "$210.00", "Almacén": "MP-LEON"},
            ]),
            Item("GRPO-4822", "GRPO-4822", "Resinas del Bajío · Ags", "warn", "Aguascalientes", {
                "Proveedor": "Resinas del Bajío", "Código proveedor": "P-0118",
                "Almacén": "MP-AGS", "Fecha": "20-jun-2026", "Hora": "10:40",
                "Monto": "$41,200 MXN", "Referencia proveedor": "FAC-11932",
                "Comentarios": "En revisión de calidad",
            }, lines=[
                {"Artículo": "Resina PP copolímero", "Cantidad recibida": 1200,
                 "Precio unitario": "$28.30", "Almacén": "MP-AGS"},
                {"Artículo": "Pigmento negro masterbatch", "Cantidad recibida": 80,
                 "Precio unitario": "$95.00", "Almacén": "MP-AGS"},
            ]),
            Item("GRPO-4819", "GRPO-4819", "León · 2h de retraso", "danger", "León", {
                "Proveedor": "Empaques del Centro", "Código proveedor": "P-0076",
                "Almacén": "MP-LEON", "Hora estimada": "07:30",
                "Comentarios": "Aún no se presenta el transportista",
            }, lines=[
                {"Artículo": "Cartón corrugado triple", "Cantidad esperada": 2000,
                 "Precio unitario": "$8.40", "Almacén": "MP-LEON"},
                {"Artículo": "Cinta de embalaje", "Cantidad esperada": 300,
                 "Precio unitario": "$15.20", "Almacén": "MP-LEON"},
            ]),
        ],
        "produccion": [
            Item("OF-1190", "OF-1190", "León · 80%", "ok", "León", {
                "Producto": "Charola termoformada TR-220", "Código artículo": "TR-220",
                "Almacén": "PT-LEON", "Cantidad planeada": "600", "Cantidad completada": "480",
                "Avance": "80%", "Fecha compromiso": "20-jun-2026", "Comentarios": "En tiempo",
            }, lines=[
                {"Componente": "Lámina de acero cal. 20", "Planeado": 600, "Emitido": 600, "Pendiente": 0},
                {"Componente": "Resina PP copolímero", "Planeado": 240, "Emitido": 192, "Pendiente": 48},
            ]),
            Item("OF-1191", "OF-1191", "Ags · espera material", "warn", "Aguascalientes", {
                "Producto": "Empaque automotriz EA-310", "Código artículo": "EA-310",
                "Almacén": "PT-AGS", "Cantidad planeada": "400", "Cantidad completada": "120",
                "Avance": "30%", "Fecha compromiso": "20-jun-2026",
                "Comentarios": "Falta resina, ver GRPO-4822",
            }, lines=[
                {"Componente": "Resina PP copolímero", "Planeado": 480, "Emitido": 144, "Pendiente": 336},
                {"Componente": "Pigmento negro masterbatch", "Planeado": 32, "Emitido": 32, "Pendiente": 0},
            ]),
            Item("OF-1188", "OF-1188", "SLP · 45%", "ok", "SLP", {
                "Producto": "Charola ensamblada CE-115", "Código artículo": "CE-115",
                "Almacén": "PT-SLP", "Cantidad planeada": "300", "Cantidad completada": "135",
                "Avance": "45%", "Fecha compromiso": "21-jun-2026", "Comentarios": "En tiempo",
            }, lines=[
                {"Componente": "Lámina de acero cal. 24", "Planeado": 300, "Emitido": 135, "Pendiente": 165},
                {"Componente": "Separador CE-115-S", "Planeado": 300, "Emitido": 135, "Pendiente": 165},
            ]),
        ],
        "traslados": [
            Item("WTR-77", "WTR-77", "León → SLP · 2h retraso", "danger", "SLP", {
                "Origen": "León (PT-LEON)", "Destino": "SLP (PT-SLP)",
                "Solicitado": "20-jun-2026 07:00",
                "Comentarios": "Camión retrasado en ruta",
            }, lines=[
                {"Artículo": "Charola TR-220", "Cantidad": 200, "Origen": "PT-LEON", "Destino": "PT-SLP"},
                {"Artículo": "Tapa TR-220", "Cantidad": 200, "Origen": "PT-LEON", "Destino": "PT-SLP"},
                {"Artículo": "Separador CE-115-S", "Cantidad": 100, "Origen": "PT-LEON", "Destino": "PT-SLP"},
            ]),
            Item("WTR-81", "WTR-81", "Ags → León · en tránsito", "ok", "León", {
                "Origen": "Aguascalientes (PT-AGS)", "Destino": "León (PT-LEON)",
                "Solicitado": "20-jun-2026 08:15",
                "Comentarios": "Llega antes de las 14:00",
            }, lines=[
                {"Artículo": "Empaque EA-310", "Cantidad": 150, "Origen": "PT-AGS", "Destino": "PT-LEON"},
                {"Artículo": "Espuma protectora EA-310-E", "Cantidad": 150, "Origen": "PT-AGS", "Destino": "PT-LEON"},
            ]),
            Item("WTR-82", "WTR-82", "SLP → León · por confirmar", "warn", "León", {
                "Origen": "SLP (MP-SLP)", "Destino": "León (MP-LEON)",
                "Solicitado": "20-jun-2026 09:50",
                "Comentarios": "Esperando confirmación de almacén origen",
            }, lines=[
                {"Artículo": "Resina PP copolímero", "Cantidad": 300, "Origen": "MP-SLP", "Destino": "MP-LEON"},
                {"Artículo": "Lámina de acero cal. 20", "Cantidad": 250, "Origen": "MP-SLP", "Destino": "MP-LEON"},
                {"Artículo": "Solvente desengrasante", "Cantidad": 40, "Origen": "MP-SLP", "Destino": "MP-LEON"},
                {"Artículo": "Cinta de embalaje", "Cantidad": 90, "Origen": "MP-SLP", "Destino": "MP-LEON"},
            ]),
        ],
        "pedidos": [
            Item("Pedido 1021", "Pedido 1021", "Ternium · Ags · listo", "ok", "Aguascalientes", {
                "Cliente": "Ternium Aguascalientes", "Código cliente": "C-0210",
                "Vendedor": "Laura Méndez", "Almacén de necesidad": "PT-AGS",
                "Entrega comprometida": "20-jun-2026 13:30", "Monto": "$184,300 MXN",
                "Comentarios": "Ya facturado",
            }, lines=[
                {"Artículo": "Charola TR-220", "Cantidad pedida": 350, "Pendiente por entregar": 0,
                 "Stock disponible (PT-AGS)": 540, "Estatus": "🟢 Cubierto"},
                {"Artículo": "Tapa TR-220", "Cantidad pedida": 350, "Pendiente por entregar": 0,
                 "Stock disponible (PT-AGS)": 320, "Estatus": "🟢 Cubierto"},
            ]),
            Item("Pedido 1023", "Pedido 1023", "Nissan · Ags · 16:00", "warn", "Aguascalientes", {
                "Cliente": "Nissan Aguascalientes", "Código cliente": "C-0087",
                "Vendedor": "Laura Méndez", "Almacén de necesidad": "PT-AGS",
                "Entrega comprometida": "20-jun-2026 16:00", "Monto": "$67,900 MXN",
                "Comentarios": "En picking, 70% surtido",
            }, lines=[
                {"Artículo": "Empaque EA-310", "Cantidad pedida": 150, "Pendiente por entregar": 120,
                 "Stock disponible (PT-AGS)": 200, "Estatus": "🟢 Cubierto"},
                {"Artículo": "Espuma protectora EA-310-E", "Cantidad pedida": 150, "Pendiente por entregar": 80,
                 "Stock disponible (PT-AGS)": 95, "Estatus": "🟢 Cubierto"},
                {"Artículo": "Charola interior EA-310-C", "Cantidad pedida": 40, "Pendiente por entregar": 40,
                 "Stock disponible (PT-AGS)": 40, "Estatus": "🟡 Justo, sin margen"},
            ]),
            Item("Pedido 1025", "Pedido 1025", "Magna · SLP · sin picking", "danger", "SLP", {
                "Cliente": "Magna SLP", "Código cliente": "C-0305",
                "Vendedor": "Jorge Salinas", "Almacén de necesidad": "PT-SLP",
                "Entrega comprometida": "20-jun-2026 18:00", "Monto": "$112,500 MXN",
                "Comentarios": "Picking aún no generado — stock insuficiente en 1 artículo",
            }, lines=[
                {"Artículo": "Charola CE-115", "Cantidad pedida": 300, "Pendiente por entregar": 300,
                 "Stock disponible (PT-SLP)": 180, "Estatus": "🔴 Insuficiente, faltan 120"},
                {"Artículo": "Separador CE-115-S", "Cantidad pedida": 150, "Pendiente por entregar": 150,
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
                "Hora salida": "11:45", "Monto": "$58,200 MXN",
                "Pedido origen": "Pedido 1018",
                "Comentarios": "En camino, hora estimada 12:30",
            }, lines=[
                {"Artículo": "Charola TR-220", "Cantidad entregada": 60,
                 "Precio unitario": "$420.00", "Almacén": "PT-LEON"},
                {"Artículo": "Tapa TR-220", "Cantidad entregada": 60,
                 "Precio unitario": "$180.00", "Almacén": "PT-LEON"},
            ]),
            Item("DLN-903", "DLN-903", "Ags · vence 17:00", "warn", "Aguascalientes", {
                "Cliente": "Nissan Aguascalientes", "Código cliente": "C-0087",
                "Almacén": "PT-AGS", "Ruta / transportista": "Ruta 2 · Flota propia",
                "Monto": "$67,900 MXN", "Pedido origen": "Pedido 1023",
                "Comentarios": "Sale en los próximos 30 min",
            }, lines=[
                {"Artículo": "Empaque EA-310", "Cantidad entregada": 120,
                 "Precio unitario": "$310.00", "Almacén": "PT-AGS"},
                {"Artículo": "Espuma protectora EA-310-E", "Cantidad entregada": 80,
                 "Precio unitario": "$95.00", "Almacén": "PT-AGS"},
            ]),
        ],
        "facturacion": [
            Item("Factura A-5510", "Factura A-5510", "León · timbrada", "ok", "León", {
                "Cliente": "Ternium Aguascalientes", "Código cliente": "C-0210",
                "Fecha": "20-jun-2026", "Monto": "$184,300 MXN", "Saldo pendiente": "$0 MXN",
                "Entrega origen": "DLN-895", "Comentarios": "Timbrada correctamente",
            }, lines=[
                {"Artículo": "Charola TR-220", "Cantidad facturada": 350,
                 "Precio unitario": "$420.00", "Importe": "$147,000.00"},
                {"Artículo": "Tapa TR-220", "Cantidad facturada": 350,
                 "Precio unitario": "$106.57", "Importe": "$37,300.00"},
            ]),
            Item("3 entregas sin facturar", "3 entregas sin facturar", "Pendientes hoy", "warn", "Todas", {
                "Comentarios": "DLN-899, DLN-900 y DLN-901 sin factura asociada",
            }, lines=[
                {"Entrega": "DLN-899", "Cliente": "Magna SLP", "Monto": "$41,200.00"},
                {"Entrega": "DLN-900", "Cliente": "Ternium Aguascalientes", "Monto": "$28,900.00"},
                {"Entrega": "DLN-901", "Cliente": "Nissan Planta A", "Monto": "$53,100.00"},
            ]),
        ],
    }
