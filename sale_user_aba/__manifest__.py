# -*- coding: utf-8 -*-
###################################################################################
#
#    DILO HN.
#    Copyright (C) 2020
#    Author: ARIEL CERRATO
###################################################################################

{
    'name': 'Usuarios ABA',
    'version': '12.0.1.1.0',
    'category': 'Sales Management',
    'summary': "Creacion de usuario ABA herencia",
    'author': 'Ariel Cerrato',
    'company': 'Dilo hn',
    'website': 'http://www.dilo.hn',
    'description': """

Sale userr aba
=======================
Module to manage sale aba user
""",
    'depends': ['sale',
                'sale_management',
                'account'
                ],
    'data': [
        'security/ir.model.access.csv',
        'views/inherint_aba_usuarios.xml',
        'views/inherint_sale.xml',
        'views/inherint_operaciones_aba.xml',
        'views/vista_motivo_perdida.xml',
        'views/inherint contract.xml',
        'data/mail_template.xml',
    ],
    'demo': [
    ],
    'images': ['static/description/Recurso 7Logo DILO.png'],
    'license': 'AGPL-3',
    'application': True,
    'installable': True,
    'auto_install': False,
}
