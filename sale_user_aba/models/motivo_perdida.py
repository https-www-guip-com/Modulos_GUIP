import logging
from datetime import date
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, tools, SUPERUSER_ID
from odoo.tools.translate import _
from odoo.tools import email_re, email_split
from odoo.exceptions import UserError, AccessError, ValidationError


class MotivoPerdidaOperaciones(models.Model):
    _name = "motivo_perdida_operaciones" 
    _description = "Motivo de perdidad Operaciones"
    _rec_name = "name_perdida"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name_perdida = fields.Char("Nombre de agente atlantida")
    activo = fields.Boolean(string='Activo')