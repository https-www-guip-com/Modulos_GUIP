# -*- coding: utf-8 -*-
import datetime
import logging
_logger = logging.getLogger(__name__)

from odoo.exceptions import UserError
from odoo import api, fields, models

AVAILABLE_PRIORITIES = [
    ('24', '24 Horas'),
    ('48', '48 Horas'),
    ('72', '72 Horas'),
]

class WebsiteSupportSLA(models.Model):

    _name = "website.support.sla"

    name = fields.Char(string="Nombre", translate=True)
    description = fields.Text(string="Descripcion", translate=True)
    #category_id = fields.Many2one('helpdesk.ticket.category', string="Categoria")
    category_id = fields.Many2many('helpdesk.ticket.category', string="Categoria")
    sla_tiempo = fields.Float(string="Tiempo restante de SLA", translate=True)
    sla_cat = fields.Selection(AVAILABLE_PRIORITIES, string='Tiempo de respuesta', index=True, default=AVAILABLE_PRIORITIES[0][0])


    @api.onchange('sla_cat')
    def _onchange_sla_tiempo_id(self):
        if self.sla_cat:
           self.sla_tiempo = self.sla_cat

    correo_template_id = fields.Many2one(
        'mail.template',
        string='Plantilla Correo',
        domain=[('model', '=', 'helpdesk.ticket')],
        help="If set an email will be sent to the "
             "customer when the ticket"
             "reaches this step.")
    
class WebsiteSupportSLARule(models.Model):

    _name = "website.support.sla.rule"
    _order = "response_time asc"

    vsa_id = fields.Many2one('website.support.sla', string="SLA")
    name = fields.Char(string="Nombre", required="True")
    condition_ids = fields.One2many('website.support.sla.rule.condition', 'wssr_id', string="Condiciones", help="All conditions have to be fulfilled for the rule to apply, e.g. priority='High' AND category='Tech Support'", required="True")
    response_time = fields.Float(string="Tiempo de respuesta", required="True", help="If the support ticket matches the conditions then it has to be completed within this amount of time, e.g. high priority tech support ticket within 1 hour")
    countdown_condition = fields.Selection([('business_only','Solo negocios'), ('24_hour','24 Horas')], default="24_hour", required="True", help="During what time do we start counting down the SLA timer")

class WebsiteSupportSLARuleCondition(models.Model):

    _name = "website.support.sla.rule.condition"

    wssr_id = fields.Many2one('website.support.sla.rule', string="SLA Reglas")
    type = fields.Selection([('category','Category'), ('priority','Priority')], string="Tipo", required="True")
    display_value = fields.Char(string="Display Value", compute="_compute_display_value")
    category_id = fields.Many2one('helpdesk.ticket.category', string="Categoria")
    #subcategory_id = fields.Many2one('website.support.ticket.subcategory', string="Sub Categoria")
    priority_id = fields.Many2one('website.support.ticket.priority', string="Prioridad")

    @api.one
    @api.depends('type','category_id','priority_id')
    def _compute_display_value(self):
        if self.type == "category":
            self.display_value = self.category_id.name
        #elif self.type == "subcategory":
        #    self.display_value = self.subcategory_id.name
        elif self.type == "priority":
            self.display_value = self.priority_id.name

class WebsiteSupportSLAAlert(models.Model):

    _name = "website.support.sla.alert"
    _order = "alert_time desc"

    vsa_id = fields.Many2one('website.support.sla', string="SLA")
    alert_time = fields.Float(string="Tiempo de alerta", help="Number of hours before or after SLA expiry to send alert")
    type = fields.Selection([('email','Email')], default="email", string="Tipo")