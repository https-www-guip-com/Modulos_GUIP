# -*- coding: utf-8 -*-
from odoo import api, fields, models
from datetime import date
from datetime import datetime
from datetime import *
import datetime
from odoo.tools.float_utils import float_round
from odoo.exceptions import UserError, ValidationError

class VacacionesOps(models.Model):
    _inherit = 'hr.contract'
    
    emple_perma = fields.Boolean(string="¿Empleado Permanente?")
    fecha_ingreso = fields.Date(string='Fecha Ingreso Real', help="Fecha de ingreso en la cual el empleado inicio con la empresa", required=True)
    hora_contractual = fields.Selection([('4', '4 horas'),('5', '5 horas'), ('6', '6 Horas'), ('8', '8 Horas'),('Permanente', 'Permanente')], string='Hora Contractual', required=True, default='4')

    #FUNCION QUE SE EJECUTARA UNA VEZ AL MES. A FINAL DE MES SE EJECUTARA
    @api.multi
    def validacion_vacaciones(self):
        estado = "open"
        perma = True
        ma = 0
        mos =  []
        zk_attendance = self.env['hr.leave.allocation']
        stage = self.env['hr.contract'].search([('state', '=', estado), ('emple_perma', '=', perma)])
        conf_val = self.env['res.config.settings'].search([], order='id desc', limit=1)
        leave_allocations = self.env['hr.leave.type'].search([('id', '=', conf_val.holiday_status_id.id)])
        #Fecha actual
        ha = datetime.datetime.now()
        fina = datetime.date(ha.year, ha.month, ha.day)
        for eta in stage:
            # Calculamos la diferencia de los días
            dias_totales = (fina - eta['fecha_ingreso']).days 
            total = 365 / dias_totales
            to2 = float_round(total, precision_digits=2)
            if dias_totales > 365 and dias_totales < 730:
               #primer = 10 * to2 
               for leave_allocation in leave_allocations:
                                zk_attendance.create({
                                        'name': leave_allocation.name,
                                        'holiday_status_id':leave_allocation.id,
                                        'number_of_days':0.83,
                                        'state': 'validate',
                                        'holiday_type': 'employee',
                                        'employee_id': eta['employee_id'].id})
            #Empleado Mayor a 2 años
            if dias_totales > 730 and dias_totales < 1095:
               for leave_allocation in leave_allocations:
                                zk_attendance.create({
                                        'name': leave_allocation.name,
                                        'holiday_status_id':leave_allocation.id,
                                        'number_of_days':1,
                                        'state': 'validate',
                                        'holiday_type': 'employee',
                                        'employee_id': eta['employee_id'].id})
            #Empleado Mayor a 3 años
            if dias_totales > 1095 and dias_totales < 1460:
               for leave_allocation in leave_allocations:
                                zk_attendance.create({
                                        'name': leave_allocation.name,
                                        'holiday_status_id':leave_allocation.id,
                                        'number_of_days':1.25,
                                        'state': 'validate',
                                        'holiday_type': 'employee',
                                        'employee_id': eta['employee_id'].id})
            #Empleado Mayor a 4 años
            if dias_totales > 1460:
               for leave_allocation in leave_allocations:
                                zk_attendance.create({
                                        'name': leave_allocation.name,
                                        'holiday_status_id':leave_allocation.id,
                                        'number_of_days':1.66,
                                        'state': 'validate',
                                        'holiday_type': 'employee',
                                        'employee_id': eta['employee_id'].id})
            
        #raise ValidationError(mos)

    @api.multi
    def validacion_vacaciones2(self):
        estado = "open"
        perma = True
        ma = 0
        mos =  []
        zk_attendance = self.env['hr.leave.allocation']
        stage = self.env['hr.contract'].search([('state', '=', estado), ('emple_perma', '=', perma)])
        conf_val = self.env['res.config.settings'].search([], order='id desc', limit=1)
        leave_allocations = self.env['hr.leave.type'].search([('id', '=', conf_val.holiday_status_id.id)])
        #for eta in stage:      
        #Fecha actual  - fecha ingreso
        hasta = datetime.datetime.now()
        final = datetime.date(hasta.year, hasta.month, hasta.day)
        #to = float_round(porce_dias, precision_digits=2)

        raise ValidationError(final)   





