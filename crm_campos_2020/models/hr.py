# -*- coding: utf-8 -*-
from odoo import api, fields, models
from datetime import date
from datetime import datetime
from datetime import *
import datetime
from odoo.exceptions import UserError, ValidationError

tipo_chip = [
    ('0', 'Claro'),
    ('1', 'Tigo'),
    ('2', 'Htelondu'),
    ('3', 'Otros'),
]

class crm_add_campos(models.Model):
    _inherit = 'crm.lead'
    
    numero_id = fields.Integer("ID Representante Legal",  required=True)
    edad = fields.Char("Edad",  required=True)
    
    nombre_completo_dueno = fields.Char("Nombre Completo Dueño",  required=True)
    email_dueno = fields.Char("Email Dueño")
    numero_id_dueno = fields.Integer("ID Dueño",  required=True)


    deno_razon_social = fields.Char("Denominación  o razón social")
    email_negocio = fields.Char("Email del Negocio")
    telefono_negocio = fields.Char("Telefono del Negocio")
    antiguedad = fields.Integer("Antigüedad del negocio(Años)",  required=True) 
    valor_mensual = fields.Selection([('1', '5000-10000'),('2', '11000-20000'),('3', '21000-40000'),('4', 'Mayor a 50000')], 
                                   default="1", 
                                   string='Venta mensual')
    
    longitud = fields.Float("Longitud")
    latitud = fields.Float("Latitud")

    tiene_internet = fields.Selection([('1', 'SI'),('2', 'NO')], 
                                   default="1",
                                   string='Tiene Internet')
    
    tipo_internet = fields.Selection([('Celular', 'Celular'),('Fibra_Optica', 'Fibra Optica'),('Residencial', 'Residencial')], 
                                   default="Residencial", 
                                   string='Tipo Internet')
    
    cantidad_productos = fields.Char("Cantidad de productos en inventario") 
    empleados_negocio = fields.Selection([('1', '1-10'),('2', '10-20'),('3', '20-30'),('4', '30-40'),('5', 'Mayor a 50')], 
                                    default="1",
                                    string='Numero de empleados') 
    metodos_pago = fields.Selection([('1', 'Efectivo'),('2', 'POS'),('3', 'Otros')], 
                                    default="1",
                                    string='Metodo de Pago')

    user_creacion_ids = fields.One2many('creacion_usuarios_guip','user_creacion_id')
    tipo_chip_selec = fields.Selection(tipo_chip, string='Tipo Chip', index=True, default=tipo_chip[0][0])