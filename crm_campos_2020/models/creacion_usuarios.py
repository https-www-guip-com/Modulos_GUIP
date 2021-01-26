# -*- coding: utf-8 -*-
from odoo import api, fields, models
from datetime import date
from datetime import datetime
from datetime import *
import datetime
from odoo.exceptions import UserError, ValidationError


AVAILABLE_PRIORITIES = [
    ('M', 'Masculino'),
    ('F', 'Femenino'),
    ('O', 'Otros'),
]

tipo_usuario = [
    ('tipo_1', 'Store User'),
    ('tipo_2', 'Manager'),
    ('tipo_3', 'Otros'),
]


class Creacion_User_Guip(models.Model):
    _name = "creacion_usuarios_guip"
    _description = "Creacion de usuarios"
    _rec_name = "name"

    name = fields.Char("Nombre Completo")
    user = fields.Char("Usuario")
    assigned_date = fields.Date(string='Fecha efectiva')
    genero = fields.Selection(AVAILABLE_PRIORITIES, string='Genero', index=True, default=AVAILABLE_PRIORITIES[0][0])
    correo = fields.Char("Correo")
    celular = fields.Char("Celular")
    tipo_usuario = fields.Selection(tipo_usuario, string='Tipo Usuario', index=True, default=tipo_usuario[0][0])
    user_creacion_id = fields.Many2one('crm.lead',string="Usuarios Creacion")
    