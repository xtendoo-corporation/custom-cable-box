{
    "name": "Cablebox Import Pricelist",
    "summary": "Importa tarifas desde Excel a listas de precios de Odoo",
    "version": "18.0.1.0.0",
    "category": "Sales",
    "author": "Xtendoo",
    "license": "LGPL-3",
    "application": False,
    "depends": [
        "sale",
    ],
    "data": [
        "security/ir.model.access.csv",
        "wizard/import_pricelist_wizard_views.xml",
        "views/menu.xml",
    ],
    "installable": True,
}

