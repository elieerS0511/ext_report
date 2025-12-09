{
    'name': "extension",
    'version': '18.0.0.1.3',
    'category': 'Sales/Reporting',
    'summary': 'extension para mostrar estado de la facutra del modulo de compras.',
    'description': """
        Módulo para extender el reporte en PDF de clientes que incluyesus datos basicos
        y el estado de la factura""",
    'author': "ESGD",
    'depends': ['base', 'account', 'purchase'],
    'data': [
        'views/report_purchase_order.xml',
    ],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}