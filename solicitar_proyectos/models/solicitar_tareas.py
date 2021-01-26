# -*- coding: utf-8 -*-
from odoo import api, fields, models
from datetime import date
from datetime import datetime
from datetime import *
import datetime
from odoo.exceptions import UserError, ValidationError

class Solicitar_Proyectos_Tareas(models.Model):
    _name = "model_solicitar_tareas"
    _description = "Solicitud De Tareas"
    _rec_name = "nombre_tarea"

    nombre_tarea = fields.Char("Nombre Tarea",  required=True)
    descripcion_tarea = fields.Text("Descripcion",  required=True)
    proyecto_tareas_id = fields.Many2one('model_solicitar_proyectos',string="Tareas Proyectoss")
    codigo_tarea = fields.Integer("Codigo") 
    tarea_seleccionar_id = fields.Many2one('project.task', string="Seguimiento Tarea", 
                                  ondelete='cascade', index=True) 
  