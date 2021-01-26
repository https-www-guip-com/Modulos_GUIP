# -*- coding: utf-8 -*-
{
    'name': "Suma Total Vacaciones Automatico",
    'summary': """Suma de vacaciones automaticas""",
    'author': "Ariel Cerrato",
    'website': "https://www.bintell.net/",
    'category': 'payroll',
    'version': '1.0',
    'license': 'OPL-1',
    'data': [
        'views/add_horas_precio.xml',
        'views/res_config_settings_views.xml',
        'data/vacaciones_cron.xml',
    ],
    'depends': ['hr','hr_payroll','hr_attendance','hr_contract'],
    'installable': True,
    'auto_install': False,
    'application': True,
}