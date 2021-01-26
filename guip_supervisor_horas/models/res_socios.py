# -*- coding: utf-8 -*-
from odoo import api, fields, models
from datetime import date
from datetime import datetime
from datetime import *
import datetime
from odoo.exceptions import UserError, ValidationError


class SociosNominas(models.Model):
    _inherit = "hr.employee"
    
    socios_id = fields.Many2one('res.partner', string="Vincular Empresa",  
                                  ondelete='cascade', index=True)
    
   