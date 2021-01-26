# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models

AVAILABLE_PRIORITIES = [
    ('0', 'Low'),
    ('1', 'Medium'),
    ('2', 'High'),
    ('3', 'Very High'),
]

SECUENCIA_PRIORITIES = [
    ('0', '1'),
    ('1', '2'),
    ('2', '3'),
    ('3', '4'),
    ('4', '5'),
    ('5', '6'),
    ('6', '7'),
    ('7', '8'),
    ('8', '9'),
    ('9', '10'),
    ('10', '11'),
    ('11', '12'),
    ('12', '13'),
    ('13', '14'),
    ('14', '15'),
]


class Etapas_flujo_Sistemas(models.Model):
    """ Model for case stages. This models the main stages of a document
        management flow. Main CRM objects (leads, opportunities, project
        issues, ...) will now use only stages, instead of state and stages.
        Stages are for example used to display the kanban view of records.
    """
    _name = "flujo_etapas_sistemas"
    _description = "Etapas Sistemas"
    _rec_name = 'name'
    _order = "sequence"

    name = fields.Char('Nombre Etapa', required=True, translate=True)
    sequence = fields.Selection(SECUENCIA_PRIORITIES, string='Secuencia', index=True, default=SECUENCIA_PRIORITIES[0][0])
    probability = fields.Float('Probabilidad (%)', required=True, default=10.0, help="This percentage depicts the default/average probability of the Case for this stage to be a success")
    on_change = fields.Boolean('Change Probabilidad Automatically', help="Setting this stage will change the probability automatically on the opportunity.")
    requirements = fields.Text('Requirements', help="Enter here the internal requirements for this stage (ex: Offer sent to customer). It will appear as a tooltip over the stage's name.")
    #team_id = fields.Many2one('crm.team', string='Sales Team', ondelete='set null',
    #    help='Specific team that uses this stage. Other teams will not be able to see or use this stage.')
    
    legend_priority = fields.Text('Priority Management Explanation', translate=True,
        help='Explanation text to help users using the star and priority mechanism on stages or issues that are in this stage.')
    
    #fold = fields.Boolean('Folded in Pipeline',
    #    help='This stage is folded in the kanban view when there are no records in that stage to display.')

    description = fields.Html(translate=True, sanitize_style=True)
    #sequence = fields.Integer(default=1)
    active = fields.Boolean(default=True)
    unattended = fields.Boolean(
        string='Unattended')
    closed = fields.Boolean(
        string='Cerrado')
    portal_user_can_close = fields.Boolean()
    mail_template_id = fields.Many2one(
        'mail.template',
        string='Email Template',
        domain=[('model', '=', 'helpdesk.ticket')],
        help="If set an email will be sent to the "
             "customer when the ticket"
             "reaches this step.")
    fold = fields.Boolean(
        string='Folded in Kanban',
        help="This stage is folded in the kanban view.")
    company_id = fields.Many2one(
        'res.company',
        string="Company",
        default=lambda self: self.env['res.company']._company_default_get(
            'helpdesk.ticket')
    )
    