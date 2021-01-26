# -*- coding: utf-8 -*-
{
    'name': "CRM Fonel OPeraciones",
    'summary': """
        Este modulo tiene la funcion de luego de terminar el primer flujo de venta del CRM, aprobar y que se vaya a otro flujo que es el de operaciones
        """,
    'author': "Ariel Cerrato",
    'website': "https://www.guip.com/",
    'category': 'crm',
    'version': '1.0',
    'license': 'OPL-1',
    'data': [
        'security/group_horas_supervisor.xml',
        'security/ir.model.access.csv',
        'views/crm_solicitar_vista_operaciones.xml',
        'views/crm_etapas_operaciones.xml',
        'data/mail_template.xml', 
    ],
    'depends': [ 'base_setup',
        'sales_team',
        'sale',
        'mail',
        'calendar',
        'resource',
        'fetchmail',
        'utm',
        'web_tour',
        'contacts',
        'digest',],
    'css': ['static/src/css/crm.css'],
    'installable': True,
    'auto_install': False,
    'application': True,
}