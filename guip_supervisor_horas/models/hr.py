# -*- coding: utf-8 -*-
from odoo import api, fields, models
from datetime import date
from datetime import datetime
from datetime import *
import datetime
from odoo.exceptions import UserError, ValidationError

class SupervisorHoras(models.Model):
    _name = "test_model_name"
    #Esta herencia funciona para que se pueda mostrar el pie de pagina en los formularios con las notas y poder enviar correos
    _inherit = ['mail.thread', 'mail.activity.mixin']
    
    def default_employee(self):
        return self.env['hr.employee'].search([('user_id', '=', self.env.uid)])

    employee_id = fields.Many2one('hr.employee', 
                                  string="Empleado",
                                  default=default_employee,
                                  required=True, 
                                  ondelete='cascade')

    def get_department(self):
        return self.env['hr.department'].search([('manager_id.user_id', '=', self.env.uid)])

    default_department_id = fields.Many2one('hr.department', 
                                             string='Departamento',
                                             default=get_department,
                                             ondelete='cascade') 



    fecha = fields.Date("Fecha",  required=True)
    hora_extra = fields.Integer("Horas", required=True)
    horas_vaca = fields.Boolean('Vacaciones', required=True)
    notas = fields.Text("Descripcion")
    fase_horas = fields.Selection([('valida', 'Validacion'),('enproce', 'En proceso'),('aprobado', 'Aprobado'),
                                   ('rechazada', 'Rechazado')], 
                                   default="valida",
                                   string='Estado')
    

    #CAMBIA EL ESTADO A PROCESO
    @api.multi
    def validacion_fechas2(self):
        stage = self.env['test_model_name'].search([('id', '=', self.id)], limit=1)
        
        if stage.fase_horas == 'enproce':
               raise ValidationError("Estado en Proceso")

        else:  
             stage = self.write({'fase_horas':'enproce'})

        return stage

    #CAMBIA EL ESTADO A RECHAZADO
    @api.multi
    def validacion_fechas1(self):
        stage = self.env['test_model_name'].search([('id', '=', self.id)], limit=1)
        
        if stage.fase_horas == 'rechazada':
               raise ValidationError("Horas Rechazadas")

        else:  
             stage = self.write({'fase_horas':'rechazada'})

        return stage

    #Funcion que cambia el estado de en proceso a Aprobado.
    #Reenvia las horas extras a nomina para que multipleque las horas por un precio.   
    @api.multi
    def validacion_fechas(self):
        stage = self.env['test_model_name'].search([('id', '=', self.id)], limit=1)
        mos = []
        ar = 0
        if stage.fase_horas == 'aprobado':
               raise ValidationError("Ya Esta Aprobado")

        elif stage.fase_horas == 'rechazada':
                     raise ValidationError("Estas horas estan rechazada, cambie a borrador para que las puedan aprobar")
        else:      
           fe = self.fecha
           stage = self.env['hr.attendance'].search([('employee_id.id', '=', self.employee_id.id)])
           for datum in stage:
               mos = datum['check_in']
               final = datetime.date(mos.year, mos.month, mos.day)
               if final == fe: 
                  ar = 1
                  break       
                  
           if ar == 1:
                stage = self.write({'fase_horas':'aprobado'})
           else: 
               raise ValidationError("El colaborador no trabajo ese dia")
        return stage       
            
    #Funcion que valida las fechas. 

    @api.multi
    def validacion_super(self):
        stage = self.env['test_model_name'].search([('id', '=', self.id)], limit=1)
        mos = []
        ar = 0
        fe = self.fecha
        stage = self.env['hr.attendance'].search([('employee_id.id', '=', self.employee_id.id)])
        for datum in stage:
            mos = datum['check_in']
            final = datetime.date(mos.year, mos.month, mos.day)
            if final == fe: 
                ar = 1
                break                 
        if ar == 1:
              stage = self.write({'fase_horas':'enproce'})
        else: 
            raise ValidationError("El colaborador no trabajo ese dia")
        return stage       
                       

