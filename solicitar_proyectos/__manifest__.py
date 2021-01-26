# -*- coding: utf-8 -*-
{
    'name': "Solicitar Proyectos",
    'summary': """
        Este modulo tiene la funcion de solicitar proyectos a realizar y que sean aprobados.
        """,
    'author': "Ariel Cerrato",
    'website': "https://www.guip.com/",
    'category': 'project',
    'version': '1.0',
    'license': 'OPL-1',
    'data': [
        'security/group_horas_supervisor.xml',
        'security/ir.model.access.csv',
        'views/solicitar_proyectos_vista.xml',
        'views/proyectos.xml',
        'views/tareas_proyectos.xml',
        'data/mail_template.xml',
    ],
    'depends': ['project'],
    'installable': True,
    'auto_install': False,
    'application': True,
}