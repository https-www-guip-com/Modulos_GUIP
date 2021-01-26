from odoo import fields, models


AVAILABLE_PRIORITIES = [
    ('24', '24 Horas'),
    ('48', '48 Horas'),
    ('72', '72 Horas'),
]

class HelpdeskCategory(models.Model):

    _name = 'helpdesk.ticket.category'
    _description = 'Helpdesk Ticket Category'

    active = fields.Boolean(string='Active', default=True)
    name = fields.Char(string='Name', required=True)
    company_id = fields.Many2one(
        'res.company',
        string="Company",
        default=lambda self: self.env['res.company']._company_default_get(
            'helpdesk.ticket')
    )
    
    sla_tiempo = fields.Selection(AVAILABLE_PRIORITIES, string='Tiempo respuesta', index=True, default=AVAILABLE_PRIORITIES[0][0])
    #sla_tiempo = fields.Float(string="Tiempo respuesta", translate=True)

    _sql_constraints = [
        ('name_uniq', 'unique (name)', "El nombre de la categoria ya existe !"),
    ]
