{
    "name": "Cablebox Sale Order Report",
    "summary": "Custom Cablebox Sale Order Report",
    "version": "18.0.1.0.0",
    "category": "Sale",
    "author": "Xtendoo",
    "license": "AGPL-3",
    "depends": ["sale", "sale_management", "mail", "web_responsive", "sale_stock"],
    "data": [
        "views/cablebox_report_sale_order.xml",
        "views/sale_order.xml",
        "views/sale_order_line.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "cablebox_sale_order_report/static/src/chatter/chatter.xml",
            "cablebox_sale_order_report/static/src/widgets/qty_at_date_widget_patch.js",
            "cablebox_sale_order_report/static/src/widgets/qty_at_date_widget_patch.xml",
        ],
        "web.report_assets_pdf": [
            "cablebox_sale_order_report/static/src/css/report_styles.css",
        ],
    },
    "installable": True,
    "application": True,
}
