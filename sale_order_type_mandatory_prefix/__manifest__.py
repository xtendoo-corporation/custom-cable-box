# Copyright 2026 Xtendoo
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Sale Order Type - Mandatory Prefix",
    "summary": "Adds a setting to make the sequence prefix mandatory on Sale Order Types",
    "version": "18.0.1.0.0",
    "category": "Sales Management",
    "author": "Xtendoo",
    "license": "AGPL-3",
    "depends": ["sale_order_type"],
    "data": [
        "views/res_config_settings_views.xml",
        "views/sale_order_type_views.xml",
    ],
    "installable": True,
    "application": False,
}

