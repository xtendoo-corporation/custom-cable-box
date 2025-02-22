{
    "name": "Cablebox Import Sale Order",
    "summary": "Cablebox Import Sale Order",
    "version": "16.0.1.0.0",
    "category": "Sale order",
    "author": "Manuel Calero, Xtendoo",
    "license": "LGPL-3",
    "application": True,
    "depends": [
        "sale",
    ],
    "data": [
        "wizard/import_sale_order_wizard.xml",
        "views/import_sale_order_view.xml",
        "security/ir.model.access.csv",
    ],
    "installable": True,
}
