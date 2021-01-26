# -*- coding: utf-8 -*-
from odoo import api, fields, models

class MailTemplateSupportTicket(models.Model):

    _inherit = "mail.template"

    built_in = fields.Boolean(string="Construido en", help="Separa las plantillas de correo electrónico creadas por módulos y las creadas por usuarios")