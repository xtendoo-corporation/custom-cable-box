{
    "name": "Cablebox Order Confirmation",
    "version": "1.0",
    "summary": "Importar confirmaciones de pedido (PDF) y extraer fechas DATE OF READINESS por línea",
    "author": "xtendoo",
    "license": "AGPL-3",
    "category": "Sales",
    "depends": [
        "sale",
        "base",
        "cablebox_gantts",
    ],
    "data": [
        "security/ir.model.access.csv",
        "data/sequence_data.xml",
        "views/sale_order_views.xml",
    ],
    "installable": True,
    "application": False,
}

