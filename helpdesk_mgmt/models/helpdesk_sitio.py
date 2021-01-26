from odoo import fields, models


class HelpdeskTicketSitio(models.Model):
    _name = 'helpdesk.ticket.sitio'
    _description = 'Helpdesk Ticket Sitio'
    _order = 'name, id'

    name = fields.Char(string='Sitio', required=True, translate=True, help='Sitio donde se creo el ticket')
    active = fields.Boolean(default=True)
    company_id = fields.Many2one(
        'res.company',
        string="Compania",
        default=lambda self: self.env['res.company']._company_default_get(
            'helpdesk.ticket')
    )
