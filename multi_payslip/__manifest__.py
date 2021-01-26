{
    'name': 'Multiple Payslip',
    'version': '12.0.1.0.0',
    'author': 'Ariel Cerrrato',
    'website': 'http://www.bintell.com',
    'summary': 'Cree varios recibos de pago al mismo tiempo.',
    'category': 'Generic Modules/Human Resources',
    'license': 'AGPL-3',
    'depends': ['hr_payroll'],
    'data': [
            'wizard/mutli_payslip_view.xml',
            'wizard/multi_payslip_confirm.xml',
    ],
    'description': """
       Este módulo es para crear recibos de pago múltiples al mismo 
       tiempo....

    """,

    'images': ['static/description/banner.jpg'],
    'auto_install': False,
    'installable': True,
}
