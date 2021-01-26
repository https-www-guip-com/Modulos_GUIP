# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging
from datetime import datetime, timedelta, date
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, tools, SUPERUSER_ID
from odoo.tools.translate import _
from odoo.tools import email_re, email_split
from odoo.exceptions import UserError, AccessError, ValidationError
#from . import flujo_etapas_sistemas
#from odoo.exceptions import UserError, ValidationError

AVAILABLE_PRIORITIES = [
    ('0', 'Bajo'),
    ('1', 'Medio'),
    ('2', 'Alto'),
    ('3', 'Muy alto'),
]

class Funel_inherint_operaciones(models.Model):
    _inherit = 'crm_flujo_nuevo_operaciones'

    operaciones_sistemas_id = fields.Many2one('crm_flujo_nuevo_sistemas', string="Mostrar info del area de plataforma",
                                  help="Desde este campo puedes ver el proceso del area de plataforma" ,
                                  ondelete='cascade', index=True)

    
class Crm_Fonel_Sistemas_Herencia(models.Model):
    _name = "crm_flujo_nuevo_sistemas" 
    _description = "Solicitud de Sistemas"
    _rec_name = "name"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    def _get_default_stage_id(self):
        return self.env['flujo_etapas_sistemas'].search([], limit=1).id

    @api.model
    def _read_group_stage_ids(self, stages, domain, order):
        stage_ids = self.env['flujo_etapas_sistemas'].search([])
        return stage_ids
        

    name = fields.Char('Oportunidad', required=True)
    active = fields.Boolean('Activo', default=True)
    date_action_last = fields.Datetime('Última acción', readonly=True)
    email_from = fields.Char('Correo', help="Email address of the contact")  
    description = fields.Text('Notas')
    contact_name = fields.Char('Nombre de contacto')

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

    tag_ids = tag_ids = fields.Many2many('sistemas_lead_tag', string='Etiquetas', help="Classify and analyze your lead/opportunity categories like: Training, Service")
    #stage_id = fields.Many2one('flujo_etapas_sistemas', string='Etapa', ondelete='restrict', 
    #                            track_visibility='onchange', index=True, copy=False)

    stage_id = fields.Many2one(
        'flujo_etapas_sistemas',
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

    operaciones_id = fields.Many2one('crm_flujo_nuevo_operaciones', string="Mostrar info del area de operaciones",
                                  help="Desde este campo puedes ver el proceso del area de operaciones" ,
                                  ondelete='cascade', index=True)
    
    company_id = fields.Many2one(
        'res.company',
        string="Compañia",
        default=lambda self: self.env['res.company']._company_default_get('crm_flujo_nuevo_sistemas')
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

    @api.multi
    def enviar_sistemas_a_plataforma(self):
        
        operaciones_crear = self.env['crm_flujo_nuevo_operaciones']
        today = date.today()
        now = datetime.strftime(today, '%Y-%m-%d %H:%M:%S')
        project_line_vals = {
                    'operaciones_sistemas_id':self.id,
                    'name':self.name,
                    'email_from':self.email_from,
                    'description': self.description,
                    'active': self.active,
                    'stage_id': '1',
                    'date_open': now,
                    'crm_id': self.crm_id.id,
                    'vendedor_id': self.vendedor_id.id
                    }
        
        res = operaciones_crear.create(project_line_vals)
        #Relacion sistemas - operaciones
        self.write({'operaciones_id':res.id})
        #relacion crm - operaciones
        stage2 = self.env['crm.lead'].search([('id', '=', self.crm_id.id)], limit=1)
        stage2 = self.write({'crm_operaciones_id':res.id})
        #Envio de correo al vendedor asignado
        self.env.ref('crm_funel_venta_sistemas.mail_template_finalizar_plataforma'). \
        send_mail(self.id, force_send=True)
        self.env.user.notify_success(message='Se envio correctamente a operaciones.')

    @api.multi
    def mostar_info(self):
        stage = self.env['crm.lead'].search([('id', '=', self.crm_id.id)], limit=1)
        raise ValidationError(stage.name)
    

    #Mostrar Seguimiento Plataforma
    #Boton de seguimiento operaciones
    @api.multi
    def document_ver_plataforma(self):
        self.ensure_one()
        domain = [
            ('operaciones_sistemas_id', '=', self.id)]
        return {
            'name': _('Plataforma'),
            'domain': domain,
            'res_model': 'crm_flujo_nuevo_operaciones',
            'type': 'ir.actions.act_window',
            'view_id': False,
            'view_mode': 'kanban,tree,form',
            'view_type': 'kanban',
            'help': _('''<p class="oe_view_nocontent_create">
                           Click para crear un nuevo 
                        </p>'''),
            'limit': 80,
            'context': "{'default_employee_ref': '%s'}" % self.id
        }
    
    document_contador_operaciones = fields.Char(string='Plataforma')
    
    @api.multi
    def write(self, vals):
        for ticket in self:
            if vals.get('stage_id'):
                stage_obj = self.env['flujo_etapas_sistemas'].browse([vals['stage_id']])                
                if stage_obj.sequence == 1:
                    vals['probability'] = '10'
                if stage_obj.sequence == 2:
                    vals['probability'] = '50'    
                if stage_obj.sequence == 3:
                    if not ticket.codigo_dispositvio:
                       raise ValidationError("Codigo del dispositvo vacio, no se puede avanzar hasta que operaciones agregue el codigo")
                    else:
                        vals['probability'] = '70'

                if stage_obj.sequence == 4 and stage_obj.closed == True:
                    if not ticket.codigo_dispositvio:
                       raise ValidationError("Codigo del dispositvo vacio, no se puede avanzar hasta que operaciones agregue el codigo")
                    else:
                        vals['probability'] = '100'

        res = super(Crm_Fonel_Sistemas_Herencia, self).write(vals)

        return res


class Tag_Sistemas(models.Model):
    _name = "sistemas_lead_tag"
    _description = "Etiquetas Sistemas"
    
    name = fields.Char('Nombre', required=True, translate=True)
    color = fields.Integer('Color Index')

    _sql_constraints = [
        ('name_uniq', 'unique (name)', "El nombre de la etiqueta ya existe !"),
    ]

