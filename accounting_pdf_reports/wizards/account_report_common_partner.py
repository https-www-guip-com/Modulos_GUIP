# -*- coding: utf-8 -*-

from odoo import fields, models


class AccountingCommonPartnerReport(models.TransientModel):
    _name = 'account.common.partner.report'
    _description = 'Account Common Partner Report'
    _inherit = "account.common.report"

    result_selection = fields.Selection([('customer', 'Cuentas por cobrar'),
                                         ('supplier', 'Cuentas por pagar'),
                                         ('customer_supplier', 'Cuentas por cobrar y por pagar')
                                         ], string="Socios", required=True, default='customer')

    def pre_print_report(self, data):
        data['form'].update(self.read(['result_selection'])[0])
        return data
