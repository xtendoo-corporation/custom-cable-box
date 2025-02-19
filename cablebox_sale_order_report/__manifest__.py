{
    "name": "Cablebox Sale Order Report",
    "summary": "Custom Cablebox Sale Order Report",
    "version": "16.0.1.0.0",
    "category": "Sale",
    "author": "Xtendoo",
    "license": "AGPL-3",
    "depends": ["sale"],
    "data": ["views/cablebox_report_sale_order.xml"],
    'assets': {
        'web.report_assets_pdf': [
            'cablebox_sale_order_report/static/src/css/report_styles.css',
        ],
    },
    "installable": True,
    'application': True,
}
