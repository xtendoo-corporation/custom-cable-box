{
    "name": "Cablebox Sale To Purchase",
    "version": "18.0.1.0.0",
    "category": "Sales",
    "summary": "Crear una compra directamente desde una venta, con un botón",
    "description": """
Añade un botón "Crear Compra" en el pedido de venta que genera un pedido de
compra con las mismas líneas de producto y cantidad.

El proveedor de la compra se determina así:

- Si hay un único proveedor conocido entre los productos, se usa directamente
  sin preguntar.
- Si hay más de un proveedor entre los productos, se pregunta cuál usar
  mediante un asistente.
""",
    "author": "Xtendoo",
    "website": "https://www.xtendoo.com",
    "license": "AGPL-3",
    "depends": ["sale", "purchase"],
    "data": [
        "security/ir.model.access.csv",
        "views/sale_order_views.xml",
        "wizards/cablebox_sale_create_purchase_wizard_views.xml",
    ],
    "installable": True,
    "application": False,
    "auto_install": False,
}
