# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging
from datetime import datetime, timedelta, date
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, tools, SUPERUSER_ID
from odoo.tools.translate import _
from odoo.tools import email_re, email_split
from odoo.exceptions import UserError, AccessError
#from . import flujo_etapas_operaciones


AVAILABLE_PRIORITIES = [
    ('0', 'Bajo'),
    ('1', 'Medio'),
    ('2', 'Alto'),
    ('3', 'Muy alto'),
]


class Crm_Fonel_Herencia(models.Model):
    _name = "crm_flujo_nuevo_operaciones" 
    _description = "Solicitud de Operaciones"
    _rec_name = "name"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    def _get_default_stage_id(self):
        return self.env['flujo_etapas_operaciones'].search([], limit=1).id

    @api.model
    def _read_group_stage_ids(self, stages, domain, order):
        stage_ids = self.env['flujo_etapas_operaciones'].search([])
        return stage_ids
        

    name = fields.Char('Oportunidad', required=True)
    active = fields.Boolean('Activo', default=True)
    date_action_last = fields.Datetime('Última acción', readonly=True)
    email_from = fields.Char('Correo', help="Email address of the contact")  
    description = fields.Text('Notas')
    contact_name = fields.Char('Nombre de contacto')
    tag_ids = tag_ids = fields.Many2many('operaciones_lead_tag', string='Etiquetas', help="Classify and analyze your lead/opportunity categories like: Training, Service")
    #stage_id = fields.Many2one('flujo_etapas_operaciones', string='Etapa', ondelete='restrict', 
    #                            track_visibility='onchange', index=True, copy=False)

    fecha_capacitacion = fields.Datetime('Fecha Capacitacion')
    #email_capacitacion = fields.Char('Persona Capacitacion', )
    email_capacitacion = fields.Many2one('hr.employee', string='Ejecutivo Postventa(Farmer)',
                                        help="Este es campo para asignar una persona que acompañara al equipo de operaciones a capacitacion")
    
    stage_id = fields.Many2one(
        'flujo_etapas_operaciones',
        string='Etapa',
        group_expand='_read_group_stage_ids',
        default=_get_default_stage_id,
        track_visibility='onchange',
    )

   
    user_id = fields.Many2one('res.users', string='Usuario Asignado', track_visibility='onchange')
    vendedor_id = fields.Many2one('res.users', string='Vendedor Asignado', track_visibility='onchange')
    referred = fields.Char('Referido por')
    probability = fields.Float('Probability', group_operator="avg", copy=False, default=10)
    priority = fields.Selection(AVAILABLE_PRIORITIES, string='Prioridad', index=True, default=AVAILABLE_PRIORITIES[0][0])

    crm_id = fields.Many2one('crm.lead', string="Mostrar info de la oportunidad",
                                  help="Desde este campo puedes ver el inicio de la oportunidad en el CRM" ,
                                  ondelete='cascade', index=True)
    
   
    #Fecha Cierre                               
    date_deadline = fields.Date('Cierre esperado', help="Estimación de la fecha en la que se enviar a operaciones.")
    date_closed = fields.Datetime('Fecha de cierre', readonly=True, copy=False)
    date_open = fields.Datetime('Fecha de asignación', readonly=True, default=fields.Datetime.now)
    day_open = fields.Float(compute='_compute_day_open', string='Dias a asignar	', store=True)
    day_close = fields.Float(compute='_compute_day_close', string='Días para el cierre', store=True)

    codigo_dispositvio = fields.Char('Codigo Dispositivo')


    #Campos Solicitados para creacion de la empresa
    razon_social = fields.Char('Razon social')
    
    street = fields.Char('Direccion')
    street2 = fields.Char('Segunda direccion')

    codigo_zip = fields.Char('Codigo Postal', change_default=True)
    city = fields.Char('Ciudad')
    state_id = fields.Many2one("res.country.state", string='Estado')
    country_id = fields.Many2one('res.country', string='País')
    
    phone = fields.Char('Telefono', track_visibility='onchange', track_sequence=5)
    mobile = fields.Char('Movil')

    company_id = fields.Many2one(
        'res.company',
        string="Compañia",
        default=lambda self: self.env['res.company']._company_default_get('model_solicitar_proyectos')
    )

    @api.depends('date_open')
    def _compute_day_open(self):
        """ Calcular la diferencia entre la fecha de creación y la fecha de apertura """
        for lead in self.filtered(lambda l: l.date_open and l.create_date):
            date_create = fields.Datetime.from_string(lead.create_date).replace(microsecond=0)
            date_open = fields.Datetime.from_string(lead.date_open)
            lead.day_open = abs((date_open - date_create).days)

    @api.onchange('date_deadline')
    def _compute_day_close(self):
        """ Calcular la diferencia entre la fecha actual y la fecha de registro """
        for lead in self.filtered(lambda l: l.date_deadline and l.create_date):
            date_create = fields.Datetime.from_string(lead.create_date)
            date_close = fields.Datetime.from_string(lead.date_deadline)
            lead.day_close = abs((date_close - date_create).days)

    #Finalizar proceso de instalacion, notificar a farmer sobre la finalizacion de la instalacion. 
    @api.multi
    def enviar_finalizacion(self):
        self.env.ref('crm_funel_venta_guip.mail_template_finalizar_operaciones'). \
        send_mail(self.id, force_send=True)

    #enviar correo a persona para que acompañe a la capacitacion al area de operaciones 
    @api.multi
    def enviar_capacitacion_opera(self):
        self.env.ref('crm_funel_venta_guip.mail_template_capacitacion_operaciones'). \
        send_mail(self.id, force_send=True)
    

 

class Tag_Operaciones(models.Model):
    _name = "operaciones_lead_tag"
    _description = "Etiquetas de operaciones"
    
    name = fields.Char('Nombre', required=True, translate=True)
    color = fields.Integer('Color Index')

    _sql_constraints = [
        ('name_uniq', 'unique (name)', "El nombre de la etiqueta ya existe !"),
    ]

