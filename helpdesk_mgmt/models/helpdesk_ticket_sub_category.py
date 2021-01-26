from odoo import fields, models

class HelpdeskSubCategory(models.Model):

    _name = 'helpdesk.ticket.subcategory'
    _description = 'Helpdesk Ticket Sub-Category'

    active = fields.Boolean(string='Active', default=True)
    name = fields.Char(string='Name', required=True)
    company_id = fields.Many2one(
        'res.company',
        string="Company",
        default=lambda self: self.env['res.company']._company_default_get(
            'helpdesk.ticket')
    )
    
    category_id = fields.Many2one('helpdesk.ticket.category',
                                    required = True,
                                  string='Category')
    
    _sql_constraints = [
        ('name_uniq', 'unique (name)', "El nombre de la categoria ya existe !"),
    ]
