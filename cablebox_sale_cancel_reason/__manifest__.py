{
    "name": "Cablebox - Motivo de Cancelación de Presupuesto",
    "version": "18.0.1.0.0",
    "category": "Sales",
    "summary": "Añade motivo de cancelación obligatorio y contadores en el tablero de ventas",
    "description": """
        Al cancelar un presupuesto/pedido de venta, se requiere seleccionar un motivo:
        - PERDIDA
        - CADUCADA SIN INFORMACIÓN
        - PEDIDO POR OTRO CLIENTE

        En el tablero de ventas se muestran contadores de:
        - Nº Ofertas Totales
        - Nº Ofertas Ganadas
        - Nº Ofertas Canceladas (Perdidas)
        - Ratio de Conversión
    """,
    "author": "Cablebox",
    "depends": ["sale"],
    "data": [
        "security/ir.model.access.csv",
        "wizard/sale_cancel_reason_wizard_views.xml",
        "views/sale_order_views.xml",
        "views/crm_team_views.xml",
    ],
    "installable": True,
    "application": False,
    "license": "LGPL-3",
}
