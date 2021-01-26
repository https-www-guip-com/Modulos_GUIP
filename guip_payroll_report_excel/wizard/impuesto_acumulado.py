# -*- coding: utf-8 -*-
###################################################################################
# ARIEL CERRATO
# arielcerrato6@hotmail.com
###################################################################################

from datetime import datetime, date, timedelta
from odoo import models, fields, api, _
from odoo.exceptions import Warning



class contrato_nue(models.Model):
    _inherit = 'hr.contract'
    meses_seguro = fields.Integer(string='IHSS Meses', required=True)
    cole_monto = fields.Float(string='Monto Mensual Colegiacion')
    meses_cole = fields.Integer(string='Meses Colegiacion' ) 
    pensiones_monto = fields.Float(string='Monto Mensual Pensiones')
    pensiones_cole = fields.Integer(string='Pensiones Meses')

class HrEmployeeAcumulado(models.Model):
    _name = 'hr.employee.impuesto'
    _description = 'Impuesto Acumulado'
    
    fecha = fields.Date(string='Fecha Inicial', required=True)
    monto_lps = fields.Float(string='Monto Quincenal', required=True) 

    def default_employee2(self):
        return self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
     
    employee_id = fields.Many2one('hr.employee', string="Empleado", 
                                  default=default_employee2, required=True, 
                                  ondelete='cascade', index=True)

class HrEmployeeAcumulado(models.Model):
    _inherit = 'hr.employee'

    @api.multi
    def _document_count(self):
        for each in self:
            document_ids = self.env['hr.employee.impuesto'].search([('employee_id', '=', each.id)])
            each.document_count = len(document_ids)

    @api.multi
    def document_view(self):
        self.ensure_one()
        domain = [
            ('employee_id', '=', self.id)]
        return {
            'name': _('Impuestos'),
            'domain': domain,
            'res_model': 'hr.employee.impuesto',
            'type': 'ir.actions.act_window',
            'view_id': False,
            'view_mode': 'tree,form',
            'view_type': 'form',
            'help': _('''<p class="oe_view_nocontent_create">
                           Click para crear un nuevo acumulado
                        </p>'''),
            'limit': 80,
            'context': "{'default_employee_ref': '%s'}" % self.id
        }

    document_count = fields.Integer(compute='_document_count', string='# ISR')


class HrEmployeeSueldos(models.Model):
    _name = 'hr.employee.sueldos'
    _description = 'Sueldo Acumulado'
    
    fecha_sueldo = fields.Date(string='Fecha Pago', required=True)
    monto_sueldo = fields.Float(string='Monto en LPS', required=True) 
    #aguinaldo_sueldo = fields.Boolean(string='Aguinaldo', required=True) 
    aguinaldo_sueldo = fields.Boolean('Aguinaldo', default=False, track_visibility=True)
    year_sueldo = fields.Integer(string='Año', required=True) 

    def default_employee2(self):
        return self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
     
    employee_id = fields.Many2one('hr.employee', string="Empleado", 
                                  default=default_employee2, required=True, 
                                  ondelete='cascade', index=True)

class HrEmployeeSueldos(models.Model):
    _inherit = 'hr.employee'

    @api.multi
    def _document_count_sueldo(self):
        for each in self:
            document_ids = self.env['hr.employee.sueldos'].search([('employee_id', '=', each.id)])
            each.document_count_sueldo = len(document_ids)

    @api.multi
    def document_view_sueldo(self):
        self.ensure_one()
        domain = [
            ('employee_id', '=', self.id)]
        return {
            'name': _('Sueldos'),
            'domain': domain,
            'res_model': 'hr.employee.sueldos',
            'type': 'ir.actions.act_window',
            'view_id': False,
            'view_mode': 'tree,form',
            'view_type': 'form',
            'help': _('''<p class="oe_view_nocontent_create">
                           Click para crear un nuevo sueldo mensual
                        </p>'''),
            'limit': 80,
            'context': "{'default_employee_ref': '%s'}" % self.id
        }

    document_count_sueldo = fields.Integer(compute='_document_count_sueldo', string='# Sueldos')


