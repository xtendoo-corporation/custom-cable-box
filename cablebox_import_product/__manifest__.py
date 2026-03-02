{
    "name": "Cablebox - Poner Costes a 0",
    "summary": "Wizard para poner a 0 el coste de todos los productos",
    "version": "18.0.1.0.0",
    "category": "Inventory",
    "author": "Guillermo Barcena Lopez",
    "license": "AGPL-3",
    "depends": ["product"],
    "data": [
        "security/ir.model.access.csv",
        "wizard/import_product_wizard_views.xml",
        "views/menu.xml",
    ],
    "installable": True,
    "application": False,
}
