import logging
from datetime import date
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, tools, SUPERUSER_ID
from odoo.tools.translate import _
from odoo.tools import email_re, email_split
from odoo.exceptions import UserError, AccessError



class SaleOrderAba(models.Model):
    _inherit = "sale.order"

    usuarios_aba_ids = fields.One2many('creacion_usuarios_aba','usuarios_aba_id')
    #numero_orden = fields.Char("# Orden de instalacion")

    crm_sistemas_id = fields.Many2one('crm_flujo_nuevo_sistemas', string="Mostrar Seguimiento Plataforma",
                                  help="Desde este campo puedes ver el seguimiento de la oportunidad desde el lado de la plataforma" ,
                                  ondelete='cascade', index=True)
    
    crm_operaciones_id = fields.Many2one('crm_flujo_nuevo_operaciones', string="Mostrar Seguimiento Operaciones",
                                  help="Desde este campo puedes ver el seguimiento de la oportunidad desde el lado de la plataforma" ,
                                  ondelete='cascade', index=True)
    
    creado_en = fields.Boolean('Creado', default=False)
    funciona_aba = fields.Boolean('Solicitud ABA', default=False)

    #Boton de seguimiento Plataforma
    @api.multi
    def document_view_sistemas(self):
        self.ensure_one()
        domain = [
            ('sale_id', '=', self.id)]
        return {
            'name': _('Plataforma'),
            'domain': domain,
            'res_model': 'crm_flujo_nuevo_sistemas',
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
    
    document_count_sistemas = fields.Char(string='Plataforma')

    #Boton de seguimiento operaciones
    @api.multi
    def document_view_operaciones(self):
        self.ensure_one()
        domain = [
            ('sale_id', '=', self.id)]
        return {
            'name': _('Operaciones'),
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
    
    document_count_operaciones = fields.Char(string='Operaciones')
    
    #Enviar a plataforma y operaciones desde sale.order
    #CAMBIAR ESTA FUNCION A PLATAFORMA QUE ENVIE PRIMERO
    @api.multi
    def enviar_sistemas(self):
        stage = self.env['sale.order'].search([('id', '=', self.id)], limit=1)
        plataforma_crear = self.env['crm_flujo_nuevo_sistemas']
        #QUEDA PENDIENTE LA CREACION DE USUARIOS 
        #user_creartor = self.env['creacion_usuarios_guip_sistemas']
        
        today = date.today()
        now = datetime.strftime(today, '%Y-%m-%d %H:%M:%S')

        if self.creado_en == False:
            project_line_vals = {
                        'sale_id':self.id,
                        'crm_id':self.opportunity_id.id,
                        'name':self.opportunity_id.name,
                        'email_from':self.opportunity_id.email_from,
                        'description': self.opportunity_id.description,
                        'active': self.opportunity_id.active,
                        'stage_id': '1',
                        'date_open': now,
                        'vendedor_id': self.opportunity_id.user_id.id,

                        'razon_social': self.opportunity_id.deno_razon_social,
                        'street': self.opportunity_id.street,
                        'street2': self.opportunity_id.street2,
                        'codigo_zip': self.opportunity_id.zip,
                        'city': self.opportunity_id.city,
                        'state_id': self.opportunity_id.state_id.id,
                        'country_id': self.opportunity_id.country_id.id,
                        'phone': self.opportunity_id.phone,
                        'mobile': self.opportunity_id.telefono_negocio,
                        }
            
            res = plataforma_crear.create(project_line_vals)
            #Union CRM AND PLATAFORMA
            stage = self.write({'crm_sistemas_id':res.id})

            #Creacion de operaciones
            operaciones_crear = self.env['crm_flujo_nuevo_operaciones']
            operaciones_line_vals = {
                        'operaciones_sistemas_id':res.id,
                        'crm_id':self.opportunity_id.id,
                        'sale_id':self.id,
                        'name':self.opportunity_id.name,
                        'email_from':self.opportunity_id.email_from,
                        'description': self.opportunity_id.description,
                        'active': self.opportunity_id.active,
                        'stage_id': '1',
                        'date_open': now,
                        'vendedor_id': self.opportunity_id.user_id.id,

                        'razon_social': self.opportunity_id.deno_razon_social,
                        'street': self.opportunity_id.street,
                        'street2': self.opportunity_id.street2,
                        'codigo_zip': self.opportunity_id.zip,
                        'city': self.opportunity_id.city,
                        'state_id': self.opportunity_id.state_id.id,
                        'country_id': self.opportunity_id.country_id.id,
                        'phone': self.opportunity_id.phone,
                        'mobile': self.opportunity_id.telefono_negocio,
                        }
            pes = operaciones_crear.create(operaciones_line_vals)
            #Union PLATAFORMA - OPERACIONES
            plataforma_crear = self.write({'operaciones_id':pes.id})
            self.envio_correo_notifi()
            stage = self.write({'creado_en':True})
            self.env.user.notify_success(message='Creacion de orden de venta Dilo creada correctamente')
        else:
            self.env.user.notify_warning(message='No se puede enviar ya que esta creado en plataforma y operaciones') 


    #Enviar funcion para Operaciones
    @api.multi
    def enviar_proceso_aba(self):
        stage = self.env['sale.order'].search([('id', '=', self.id)], limit=1)
        
        today = date.today()
        now = datetime.strftime(today, '%Y-%m-%d %H:%M:%S')
        
        if self.creado_en == False:
            #Creacion de operaciones
            operaciones_crear = self.env['crm_flujo_nuevo_operaciones']
            
            for aba_campos in self.usuarios_aba_ids:

                operaciones_line_vals = {
                            'sale_id':self.id,
                            'name':aba_campos.name_agente_atlantida,
                            'email_from':self.partner_id.email,
                            'description': self.note,
                            'stage_id': '1',
                            'date_open': now,
                            'vendedor_id': self.user_id.id,

                            'name_agente_atlantida': aba_campos.name_agente_atlantida,
                            'codigo': aba_campos.codigo,
                            'terminal': aba_campos.terminal,
                            'name_contacto': aba_campos.name_contacto,
                            'rtn': aba_campos.rtn,
                            'tipo_chip_selec': aba_campos.tipo_chip_selec,
                            'usuario': aba_campos.usuario,
                            'recibe_gestion': aba_campos.recibe_gestion,
                            'description': aba_campos.comentarios,
                            'token': aba_campos.token,
                            'tipo_terminal': aba_campos.tipo_terminal,
                            }
                operaciones_crear.create(operaciones_line_vals)
                   
            self.env.user.notify_warning(message='Creacion de orden de venta ABA creada correctamente') 
        else:
            self.env.user.notify_warning(message='Ya esta creada esta orden de venta ABA') 
        
  


    #Modifico el boton de confirmar el pedido en el modulo de ventas sale_order.
    @api.multi
    def action_confirm(self):
        if self._get_forbidden_state_confirm() & set(self.mapped('state')):
            raise UserError(_(
                'It is not allowed to confirm an order in the following states: %s'
            ) % (', '.join(self._get_forbidden_state_confirm())))

        for order in self.filtered(lambda order: order.partner_id not in order.message_partner_ids):
            order.message_subscribe([order.partner_id.id])
        self.write({
            'state': 'sale',
            'confirmation_date': fields.Datetime.now()
        })
        self._action_confirm()

        if self.funciona_aba == True:
            self.enviar_proceso_aba()
        else:
            self.enviar_sistemas()
        
        if self.env['ir.config_parameter'].sudo().get_param('sale.auto_done_setting'):
            self.action_done()
        return True 


    #Obtengo los correos de los seguidores
    @api.multi
    def correos_notificar_mail(self):
        lista_correos = []
        ventas = 'ventas@dilo.hn'
        operaciones = 'soporte_doc@dilo.hn'
        plataforma = 'soporte_pla@dilo.hn'
        
        lista_correos.append(ventas)
        lista_correos.append(operaciones)
        lista_correos.append(plataforma)
        #for plp in self.seguidores_ids: 
        #    lista_correos.append(plp.email)
        return ",".join(lista_correos)

    #Metodo para enviar correos
    #Envio de correo al vendedor asignado
    @api.multi
    def envio_correo_notifi(self):
        self.env.ref('sale_user_aba.mail_template_notificacion_presupuesto'). \
        send_mail(self.id, force_send=True)