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
    #crm_operaciones_id = fields.Many2one('crm_flujo_nuevo_sistemas', string="Mostrar Seguimiento Plataforma",
    #                              help="Desde este campo puedes ver el seguimiento de la oportunidad desde el lado de la plataforma" ,
    #                              ondelete='cascade', index=True)
    #Este es de operaciones
    
    crm_operaciones_id = fields.Many2one('crm_flujo_nuevo_operaciones', string="Mostrar Seguimiento Operaciones",
                                  help="Desde este campo puedes ver el seguimiento de la oportunidad desde el lado de la plataforma" ,
                                  ondelete='cascade', index=True)
    
    #CAMBIAR ESTA FUNCION A PLATAFORMA QUE ENVIE PRIMERO
    @api.multi
    def enviar_operaciones(self):
        stage = self.env['crm.lead'].search([('id', '=', self.id)], limit=1)
        operaciones_crear = self.env['crm_flujo_nuevo_operaciones']
        today = date.today()
        now = datetime.strftime(today, '%Y-%m-%d %H:%M:%S')
        project_line_vals = {
                    'crm_id':self.id,
                    'name':self.name,
                    'email_from':self.email_from,
                    'description': self.description,
                    'active': self.active,
                    'stage_id': '1',
                    'date_open': now,
                    }
        
        res = operaciones_crear.create(project_line_vals)
        stage = self.write({'crm_operaciones_id':res.id})
        self.env.user.notify_success(message='Se envio correctamente a plataforma.')
        

    #Boton de seguimiento operaciones
    @api.multi
    def document_view_operaciones(self):
        self.ensure_one()
        domain = [
            ('id', '=', self.crm_operaciones_id.id)]
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