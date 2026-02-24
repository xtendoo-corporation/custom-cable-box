{
    "name": "Cablebox - Gestión de Filtros por Defecto",
    "summary": "Permite al usuario gestionar sus filtros por defecto en Compras, Ventas, Facturación e Inventario.",
    "version": "18.0.1.0.0",
    "category": "Tools",
    "author": "Guillermo Bárcena López",
    "license": "AGPL-3",
    "depends": ["base", "purchase", "sale_management", "account", "stock"],
    "data": [
        "views/cablebox_default_filters_views.xml",
        "views/cablebox_default_filters_menu.xml",
    ],
    "installable": True,
    "application": False,
}
