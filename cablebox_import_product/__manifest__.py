{
    "name": "cablebox Import Product",
    "summary": "Wizard para importar productos",
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
