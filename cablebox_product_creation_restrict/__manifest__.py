{
    'name': 'Cablebox Product Creation Restrict',
    'version': '18.0.1.0.0',
    'category': 'Inventory/Inventory',
    'summary': 'Restringe la creación de productos a un usuario específico.',
    'description': """
        Este módulo permite configurar un único usuario que tendrá permisos para crear productos.
        El resto de los usuarios no podrá crear productos.
    """,
    'author': 'Cablebox',
    'depends': ['product', 'stock'],
    'data': [
        'views/res_config_settings_views.xml',
    ],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}

