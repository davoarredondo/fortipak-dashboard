"""
data/model.py
-------------
Estructura común que usa toda la app para representar una tarjeta del
dashboard (una recepción, un pedido, una orden de fabricación, etc.),
sin importar si el dato viene de SAP real o de los datos de demostración.
"""
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Item:
    id: str            # Identificador a mostrar, ej. "GRPO-4821"
    title: str          # Texto principal de la tarjeta
    subtitle: str        # Texto secundario corto (usado dentro del detalle)
    status: str          # "ok" | "warn" | "danger"
    branch: str           # "León" | "Aguascalientes" | "SLP"
    related: str = ""      # Quién/qué está relacionado: "Cliente: X" / "Proveedor: X" / "Almacén: X"
    when: str = ""          # Dato de tiempo más relevante: hora de entrega, fecha compromiso, etc.
    detail: dict = field(default_factory=dict)  # Pares clave-valor para el detalle
    lines: Optional[list[dict]] = None  # Detalle por partida (ej. partidas de un pedido
                                          # con pendiente por entregar vs. stock disponible)

    @property
    def status_icon(self) -> str:
        return {"ok": "🟢", "warn": "🟡", "danger": "🔴"}.get(self.status, "⚪")
