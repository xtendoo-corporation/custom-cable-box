{
    'name': 'Cablebox Gantts',
    'version': '18.0.1.0.0',
    'category': 'Sales',
    'summary': 'Visualización Gantt para el Estado de Entrega',
    'description': """
        Añade una vista Gantt para las líneas de pedido de venta en Informes de Ventas.
        Muestra la relación entre el pedido SAP, el pedido de Odoo y los productos.
    """,
    'author': 'Xtendoo',
    'depends': ['sale', 'web_timeline', 'sale_stock'],
    'data': [
        'views/sale_order_line_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'cablebox_gantts/static/src/views/timeline/timeline_arch_parser_extension.js',
            'cablebox_gantts/static/src/views/timeline/timeline_model_extension.js',
            'cablebox_gantts/static/src/views/timeline/timeline_renderer_extension.js',
            'cablebox_gantts/static/src/views/timeline/xml/timeline_renderer_extension.xml',
        ],
    },
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}
