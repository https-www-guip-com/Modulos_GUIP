import logging
from datetime import date
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, tools, SUPERUSER_ID
from odoo.tools.translate import _
from odoo.tools import email_re, email_split
from odoo.exceptions import UserError, AccessError

class Crm_inherint_operaciones(models.Model):
    _inherit = 'crm.lead'
    
    #Este de sistemas
    crm_sistemas_id = fields.Many2one('crm_flujo_nuevo_sistemas', string="Mostrar Seguimiento Plataforma",
                                  help="Desde este campo puedes ver el seguimiento de la oportunidad desde el lado de la plataforma" ,
                                  ondelete='cascade', index=True)
   
    #Campo para que cuando se cree no se vuelva a crear la oportunidad
    creado_en = fields.Boolean('Creado', default=False)

    #CAMBIAR ESTA FUNCION A PLATAFORMA QUE ENVIE PRIMERO
    @api.multi
    def enviar_sistemas(self):
        stage = self.env['crm.lead'].search([('id', '=', self.id)], limit=1)
        plataforma_crear = self.env['crm_flujo_nuevo_sistemas']
        #QUEDA PENDIENTE LA CREACION DE USUARIOS 
        #user_creartor = self.env['creacion_usuarios_guip_sistemas']
        
        today = date.today()
        now = datetime.strftime(today, '%Y-%m-%d %H:%M:%S')

        if self.creado_en == False:
            project_line_vals = {
                        'crm_id':self.id,
                        'name':self.name,
                        'email_from':self.email_from,
                        'description': self.description,
                        'active': self.active,
                        'stage_id': '1',
                        'date_open': now,
                        'vendedor_id': self.user_id.id,

                        'razon_social': self.deno_razon_social,
                        'street': self.street,
                        'street2': self.street2,
                        'codigo_zip': self.zip,
                        'city': self.city,
                        'state_id': self.state_id.id,
                        'country_id': self.country_id.id,
                        'phone': self.phone,
                        'mobile': self.telefono_negocio,
                        }
            
            res = plataforma_crear.create(project_line_vals)
            #Union CRM AND PLATAFORMA
            stage = self.write({'crm_sistemas_id':res.id})

            #Creacion de operaciones
            operaciones_crear = self.env['crm_flujo_nuevo_operaciones']
            operaciones_line_vals = {
                        'operaciones_sistemas_id':res.id,
                        'crm_id':self.id,
                        'name':self.name,
                        'email_from':self.email_from,
                        'description': self.description,
                        'active': self.active,
                        'stage_id': '1',
                        'date_open': now,
                        'vendedor_id': self.user_id.id,

                        'razon_social': self.deno_razon_social,
                        'street': self.street,
                        'street2': self.street2,
                        'codigo_zip': self.zip,
                        'city': self.city,
                        'state_id': self.state_id.id,
                        'country_id': self.country_id.id,
                        'phone': self.phone,
                        'mobile': self.telefono_negocio,
                        }
            pes = operaciones_crear.create(operaciones_line_vals)
            #Union PLATAFORMA - OPERACIONES
            plataforma_crear = self.write({'operaciones_id':pes.id})
            stage = self.write({'creado_en':True})
            self.env.user.notify_success(message='Se envio correctamente a plataforma y operaciones.')
        else:
            self.env.user.notify_warning(message='No se puede enviar ya que esta creado en plataforma y operaciones') 
        

        

    #Boton de seguimiento Plataforma
    @api.multi
    def document_view_sistemas(self):
        self.ensure_one()
        domain = [
            ('crm_id', '=', self.id)]
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
            ('crm_id', '=', self.id)]
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
    
