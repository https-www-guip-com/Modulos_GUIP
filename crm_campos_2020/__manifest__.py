# -*- coding: utf-8 -*-
{
    'name': "Campos nuevos en el CRM",
    'summary': """
        Este modulo agrega nuevo campos en el CRM.
        """,
    'author': "Ariel Cerrato",
    'website': "https://www.bintell.net/",
    'category': 'Sales',
    'version': '1.0',
    'license': 'OPL-1',
    'data': [
        'security/ir.model.access.csv',
        'views/crm_add_campos.xml',
        'views/empleados_guip.xml',
    ],
    'depends': ['crm'],
    'installable': True,
    'auto_install': False,
    'application': True,
}