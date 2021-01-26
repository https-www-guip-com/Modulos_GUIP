import logging
from datetime import date
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, tools, SUPERUSER_ID
from odoo.tools.translate import _
from odoo.tools import email_re, email_split
from odoo.exceptions import UserError, AccessError

tipo_chip = [
    ('1', 'Claro'),
    ('2', 'Tigo'),
    ('3', 'Hondutel'),
    ('4', 'Otros'),
]

tipo_terminales = [
    ('1', 'Terminal 1'),
    ('2', 'Terminal 2'),
    ('3', 'Otros'),
]

class SaleOrderOperaciones(models.Model):
    _inherit = "crm_flujo_nuevo_operaciones"

    sale_id = fields.Many2one('sale.order', string="Mostrar info de la oportunidad",
                                  help="Desde este campo puedes ver el inicio de la oportunidad en el CRM" ,
                                  ondelete='cascade', index=True)

    name_agente_atlantida = fields.Char("Nombre de agente atlantida")
    codigo = fields.Integer("Codigo Completo")
    terminal = fields.Integer("Terminal")
    #street = fields.Char('Direccion')
    #street2 = fields.Char('Segunda direccion')
    #codigo_zip = fields.Char('Codigo Postal', change_default=True)
    #city = fields.Char('Ciudad')
    #state_id = fields.Many2one("res.country.state", string='Departamento')
    #country_id = fields.Many2one('res.country', string='País')
    #phone = fields.Char('Telefono', track_visibility='onchange', track_sequence=5)
    
    name_contacto = fields.Char("Nombre de contacto")
    rtn = fields.Char("RTN")
    tipo_chip_selec = fields.Selection(tipo_chip, string='Tipo Chip', index=True, default=tipo_chip[0][0])
    usuario = fields.Char("Usuarios")
    recibe_gestion = fields.Char("Recibe gestion")
    comentarios = fields.Text("Comentarios adicionales")
    token = fields.Integer("Token")
    tipo_terminal = fields.Selection(tipo_terminales, string='Tipo de terminal', index=True, default=tipo_terminales[0][0])
    usuarios_aba_id = fields.Many2one('sale.order',string="Usuarios Creacion")


    purchase_aba_id = fields.Many2one('purchase.order', string="Mostrar info de la compra",
                                  help="Desde este campo puedes ver la relacion de la compra" ,
                                  ondelete='cascade', index=True)
    
    @api.multi
    def enviar_compras_aba(self):
        operaciones_crear = self.env['purchase.order']
        order_linea_crear = self.env['purchase.order.line']

        today = date.today()
        now = datetime.strftime(today, '%Y-%m-%d %H:%M:%S')

        operaciones_line_vals = {
                            'partner_id':self.sale_id.partner_id.id,
                            'date_order': now,
                            'user_id': self.user_id.id,
                            }

        res = operaciones_crear.create(operaciones_line_vals)
        # Orden de compra order_line

        for ventas in self.sale_id.order_line:

            linea_productos_vals = {
                                'order_id': res.id,
                                'product_id':ventas.product_id.id,
                                'name': ventas.name,
                                'date_planned': self.sale_id.confirmation_date,
                                'product_qty': ventas.product_uom_qty,
                                'product_uom': ventas.product_uom.id,
                                'price_unit': ventas.price_unit,
                                }

            order_linea_crear.create(linea_productos_vals)
        self.env.user.notify_warning(message='Se creo la orden de compra') 


class SaleOrderPlataforma(models.Model):
    _inherit = "crm_flujo_nuevo_sistemas"

    sale_id = fields.Many2one('sale.order', string="Mostrar info de la oportunidad",
                                  help="Desde este campo puedes ver el inicio de la oportunidad en el CRM" ,
                                  ondelete='cascade', index=True)


class Operaciones_Compras(models.Model):
    _inherit = "purchase.order"

    purchase_aba_id = fields.Many2one('crm_flujo_nuevo_operaciones', string="Mostrar info de las oportunidades",
                                  help="Desde este campo puedes ver el inicio de la oportunidad en el CRM" ,
                                  ondelete='cascade', index=True)