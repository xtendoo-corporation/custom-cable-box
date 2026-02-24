{
    "name": "Cablebox - Vista por Defecto Facturación",
    "summary": "Cambia la vista inicial de la app de Facturación para que abra por defecto los Pedidos a Facturar en lugar del Tablero Contable.",
    "version": "18.0.1.0.0",
    "category": "Accounting",
    "author": "Guillermo Bárcena López",
    "license": "AGPL-3",
    "depends": ["account", "sale_management"],
    "data": [
        "views/invoicing_menu_override.xml",
    ],
    "installable": True,
    "application": False,
    "auto_install": False,
}
