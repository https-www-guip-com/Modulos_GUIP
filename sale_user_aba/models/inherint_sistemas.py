import logging
from datetime import date
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, tools, SUPERUSER_ID
from odoo.tools.translate import _
from odoo.tools import email_re, email_split
from odoo.exceptions import UserError, AccessError, ValidationError

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

    sale_id = fields.Many2one('sale.order', string="Orden de venta",
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
    

    elegir_proveedor_id = fields.Many2one('res.partner', string="Seleccionar proveedor",
                                  help="Seleccione al proveedor el cual se le creara una orden de compra" ,
                                  ondelete='cascade', index=True)


    #Estos campos booleanos son para llevar un control de que no se mueva de etapa de envio aprobacion y de envio a compras y las demas si no se ha hecho bien el proceso
    enviado_apro = fields.Boolean(string='Enviado Aprobacion', default=False )
    enviado_compra = fields.Boolean(string='Enviado a compras', default=False)
    instalado_aba = fields.Boolean(string='Instalado', default=False)

    @api.multi
    def enviar_compras_aba(self):

        stage = self.env['crm_flujo_nuevo_operaciones'].search([('id', '=', self.id)], limit=1)
        if self.elegir_proveedor_id.email: 
        
            operaciones_crear = self.env['purchase.order']
            order_linea_crear = self.env['purchase.order.line']
           
            today = date.today()
            now = datetime.strftime(today, '%Y-%m-%d %H:%M:%S')

            operaciones_line_vals = {
                                'partner_id':self.elegir_proveedor_id.id,
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
        
            self.envio_correo_instalacion_proveedor()
            stage = self.write({'probability': '70'})
            stage = self.write({'enviado_compra': True})
            stage = self.write({'stage_id': '5'})
            self.env.user.notify_success(message='Se creo la orden de compra, y se envio la orden de instalacion al proveedor') 
        else:
            self.env.user.notify_warning(message='No tiene agregado al proveedor al que se le enviara la orden de instalacion') 

        return stage  

    #Envio de correo al vendedor asignado
    @api.multi
    def envio_correo_instalacion_proveedor(self):
        self.env.ref('sale_user_aba.mail_template_notificacion_instalacion_d2mini'). \
        send_mail(self.id, force_send=True)
        
    #Perfil que se encarga de aprobar para que envie a instalacion
    @api.multi
    def envio_aprobacion(self):
        stage = self.env['crm_flujo_nuevo_operaciones'].search([('id', '=', self.id)], limit=1)
                         
        if self.stage_id.envio_aprobacion == False:
                #Cambiar estatus aqui cuando se pase a produccion verificar este paso
            stage = self.write({'stage_id': '4'})
            stage = self.write({'probability': '50'})
            stage = self.write({'enviado_apro': True})
            self.env.user.notify_success(message='Se envio aprobacion correctamente.')
        else: 
            self.env.user.notify_info(message='Ya se envio aprobacion') 
        return stage   

    
    #Metodos ORM
    @api.multi
    def write(self, vals):
        for ticket in self:
            
            if vals.get('stage_id'):
                
                stage_obj = self.env['flujo_etapas_operaciones'].browse([vals['stage_id']])                
                
                if stage_obj.sequence == '0':
                    if ticket.enviado_apro == False:
                       vals['probability'] = '10'
                    else:
                        raise ValidationError("Esta instalacion ya se envio aprobacion, no se puede regresar una instalacion que ya paso por la etapada de aprobacion")
                    
                if stage_obj.sequence == '1':
                        if self.enviado_apro == False:
                            vals['probability'] = '20'
                        else:
                            raise ValidationError("Esta instalacion ya se envio aprobacion, no se puede regresar una instalacion que ya paso por la etapada de aprobacion")
                    
                if stage_obj.sequence == '2':
                        if self.enviado_apro == False:
                            vals['probability'] = '40'
                        else:
                            raise ValidationError("Esta instalacion ya se envio aprobacion, no se puede regresar una instalacion que ya paso por la etapada de aprobacion")
                
                if stage_obj.sequence == '3':  
                #   raise ValidationError("Para enviar esta etapa se tiene que hacer por medio de los botones de funcion de enviar aprobacion")
                    if self.enviado_apro == False:
                        vals['probability'] = '50'
                        vals['enviado_apro'] = True
                    else:
                       raise ValidationError("Esta instalacion ya se envio aprobacion, no se puede regresar una instalacion que ya paso por la etapada de aprobacion") 
                if stage_obj.sequence == '4':
                    raise ValidationError("En esta etapa se tiene que enviar por medio de una orden de compra llevando el flujo establecido")

                if stage_obj.sequence == '5':
                    if self.enviado_apro == False:
                       raise ValidationError("Se tiene que enviar aprobacion ")
                    
                    if self.enviado_compra == False:
                       raise ValidationError("En esta etapa se tiene que enviar por medio de una orden de compra llevando el flujo establecido")

                    vals['probability'] = '100'
                    vals['instalado_aba'] = True

                if stage_obj.sequence == '6':
                    raise ValidationError("Esta instalacion se devolvio")

                if stage_obj.sequence == '7':
                    raise ValidationError("Esta instalacion esta en otros")
        res = super(SaleOrderOperaciones, self).write(vals)

        return res


    
    #Boton de seguimiento Plataforma
    @api.multi
    def document_view_compras(self):
        self.ensure_one()
        domain = [
            ('purchase_aba_id', '=', self.id)]
        return {
            'name': _('Compras'),
            'domain': domain,
            'res_model': 'purchase.order',
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
    
    document_count_compras = fields.Char(string='Plataforma')


    #Generar la orden para que se agrege el contrato permanente
    @api.multi
    def contrato_recurrente(self):
        #Modulo para buscar el contrato segun el proveedor
        operaciones_crear = self.env['contract.contract'].search([('partner_id', '=', self.sale_id.partner_id.id),('contract_aba', '=', True)  ], limit=1) 
        #Moddelo para generar el item de contrato recurrente al empleado
        linea_contrato_crear = self.env['contract.line']
        #Buscar el producto de arrendamiento
        producto_buscar = self.env['product.template'].search([('default_code', '=', 'servicio-arrend2')], limit=1) 


        #raise ValidationError(producto_buscar.name)
        if operaciones_crear:
            
            linea_productos_vals = {
                                    'contract_id': operaciones_crear.id,
                                    'purchase_aba_id': self.id,
                                    'product_id': producto_buscar.id,
                                    'name': self.name,
                                    'quantity': 1,
                                    'date_start': self.sale_id.confirmation_date,
                                    'price_unit': producto_buscar.list_price,
                                    'recurring_interval': 1,
                                    'recurring_rule_type': 'monthly',
                                    'recurring_invoicing_type': 'pre-paid',
                                    }

            linea_contrato_crear.create(linea_productos_vals)
        
            self.env.user.notify_success(message='Se genero la orden para facturacion recurrente')               
                
        else:
            self.env.user.notify_success(message='No hay un contrato creado para el cliente principal, revisar la orden de venta y verificar que ese cliente tenga un contrato recurrente creado y que este activado el check de arrendamiento d2mini')
        



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

class Operaciones_Contratos(models.Model):
    _inherit = "contract.contract"

    purchase_aba_id = fields.Many2one('crm_flujo_nuevo_operaciones', string="Mostrar info de las oportunidades",
                                  help="Desde este campo puedes ver el inicio de la oportunidad en el CRM" ,
                                  ondelete='cascade', index=True)
    
    contract_aba = fields.Boolean(string='Contrato Arrendamiento D2mini')


class Operaciones_Contratos_Line(models.Model):
    _inherit = "contract.line"

    purchase_aba_id = fields.Many2one('crm_flujo_nuevo_operaciones', string="Mostrar info de las oportunidades",
                                  help="Desde este campo puedes ver el inicio de la oportunidad en el CRM" ,
                                  ondelete='cascade', index=True)
    
   