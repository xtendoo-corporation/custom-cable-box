{
    "name": "Cablebox Logistics KPIs",
    "version": "1.0",
    "summary": "KPIs de pedidos pendientes/retrasados de entrega y dashboard en Tableros > Logística",
    "author": "xtendoo",
    "license": "AGPL-3",
    "category": "Sales",
    "depends": [
        "sale",
        "cablebox_gantts",
        "spreadsheet_dashboard",
    ],
    "data": [
        "data/ir_cron.xml",
        "data/dashboards.xml",
    ],
    "installable": True,
    "application": False,
}
