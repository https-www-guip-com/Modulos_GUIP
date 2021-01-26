from odoo import _, api, fields, models, tools
from email.utils import getaddresses


AVAILABLE_PRIORITIES = [
    ('24', '24 Horas'),
    ('48', '48 Horas'),
    ('72', '72 Horas'),
]

class HelpdeskTicket(models.Model):

    _name = 'helpdesk.ticket'
    _description = 'Helpdesk Ticket'
    _rec_name = 'number'
    _order = 'priority desc, sequence, number desc'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']

    def _get_default_stage_id(self):
        return self.env['helpdesk.ticket.stage'].search([], limit=1).id

    active = fields.Boolean(default=True)
    number = fields.Char(string='Ticket number', default="/",
                         readonly=True)
    name = fields.Char(string='Title', required=True)
    description = fields.Html(required=True, sanitize_style=True)
    user_id = fields.Many2one(
        'res.users',
        string='Assigned user',)

    user_ids = fields.Many2many(
        comodel_name='res.users',
        related='team_id.user_ids',
        string='Users')

    @api.model
    def _read_group_stage_ids(self, stages, domain, order):
        stage_ids = self.env['helpdesk.ticket.stage'].search([])
        return stage_ids

    stage_id = fields.Many2one(
        'helpdesk.ticket.stage',
        string='Stage',
        group_expand='_read_group_stage_ids',
        default=_get_default_stage_id,
        track_visibility='onchange',
    )
    partner_id = fields.Many2one('res.partner')
    partner_name = fields.Char()
    partner_email = fields.Char()


    employee_name = fields.Char()
    employee_email = fields.Char()

    last_stage_update = fields.Datetime(
        string='Last Stage Update',
        default=fields.Datetime.now,
    )
    assigned_date = fields.Datetime(string='Assigned Date')
    closed_date = fields.Datetime(string='Closed Date')
    closed = fields.Boolean(related='stage_id.closed')
    unattended = fields.Boolean(related='stage_id.unattended', store=True)
    tag_ids = fields.Many2many('helpdesk.ticket.tag')
    company_id = fields.Many2one(
        'res.company',
        string="Company",
        default=lambda self: self.env['res.company']._company_default_get(
            'helpdesk.ticket')
    )
    channel_id = fields.Many2one(
        'helpdesk.ticket.channel',
        required = True,
        string='Canal Solicitante',
        help='Channel indicates where the source of a ticket'
             'comes from (it could be a phone call, an email...)',
    )
    category_id = fields.Many2one('helpdesk.ticket.category',
                                    required = True,
                                  string='Category')
    
    subcategory_id = fields.Many2one('helpdesk.ticket.subcategory',
                                     required = True,
                                     string='Subcategoria')

    team_id = fields.Many2one('helpdesk.ticket.team', required = True)
    priority = fields.Selection(selection=[
        ('0', _('Low')),
        ('1', _('Medium')),
        ('2', _('High')),
        ('3', _('Very High')),
    ], string='Priority', default='1')
    color = fields.Integer(string='Color Index')
    kanban_state = fields.Selection([
        ('normal', 'Default'),
        ('done', 'Ready for next stage'),
        ('blocked', 'Blocked')], string='Kanban State')
    sequence = fields.Integer(
        string='Sequence', index=True, default=10,
        help="Gives the sequence order when displaying a list of tickets.")

    #Codigo Agregado
    employee_id = fields.Many2one('res.users', required=True, string='Informado ', default=lambda self: self.env.user, track_visibility="onchange")

    seguidores_ids = fields.Many2many('res.users', string='Seguidores', help="En esta parte puedes agregar varios seguidores en el poryecto el cual miraran el proceso del proeycto")
    

    #CODIGO SLA 
    sla_id = fields.Many2one('website.support.sla', string="SLA")
    sla_timer = fields.Float(string="Tiempo restante de SLA")
    sla_timer_format = fields.Char(string="Formato de temporizador SLA", compute="_compute_sla_timer_format")
    sla_active = fields.Boolean(string="SLA Activo")
    sla_fallo = fields.Boolean(string="SLA Fallo",
                               help="Si el SLA no se resolvio en el plazo establecido se marca como que no se puedo cumplir a tiempo y deja un check de que no se logro resolver a tiempo")

    sla_rule_id = fields.Many2one('website.support.sla.rule', string="SLA Reglas")
    sla_alert_ids = fields.Many2many('website.support.sla.alert', string="SLA Alertas",
                                     help="Keep record of SLA alerts sent so we do not resend them")
    sla_cat = fields.Selection(AVAILABLE_PRIORITIES, string='Tiempo de respuesta', index=True, default=AVAILABLE_PRIORITIES[0][0])

    #Sitios 
    sitio_id = fields.Many2one('helpdesk.ticket.sitio', string="Sitio")

    #Funcion que trae el SLA, de acuerdo a la categoria. 
    @api.onchange('category_id')
    def _onchange_sla_id(self):
        if self.category_id:
           sla_search = self.env['website.support.sla'].search([('category_id.id', '=', self.category_id.id)], limit=1)
           self.sla_id = sla_search.id
           self.sla_timer = sla_search.sla_tiempo
           self.sla_active = True
           self.sla_cat = sla_search.sla_cat
           
           for rec in self:
               return {'domain': {'subcategory_id': [('category_id.id', '=', rec.category_id.id)]}}

    @api.one
    @api.depends('sla_timer')
    def _compute_sla_timer_format(self):
        # Display negative hours in a positive format
        self.sla_timer_format = '{0:02.0f}:{1:02.0f}'.format(*divmod(abs(self.sla_timer) * 60, 60))

    @api.model
    def update_sla_timer(self):
        # Subtract 1 minute from the timer of all active SLA tickets, this includes going into negative
        for active_sla_ticket in self.env['helpdesk.ticket'].search([('sla_active','=',True),('sla_id','!=',False)]):
            active_sla_ticket.sla_timer -= 1/60

            #Send Email 24 hrs ---
            if  active_sla_ticket.sla_timer_format == '00:00' and active_sla_ticket.self.sla_cat == '24':
                self.env.ref('helpdesk_mgmt.created_ticket_template_sla_24hrs'). \
                send_mail(active_sla_ticket.id, force_send=True)
                self.sla_fallo = True

            #Send Email 48 hrs ---
            if  active_sla_ticket.sla_timer_format == '00:00' and active_sla_ticket.self.sla_cat == '48':
                self.env.ref('helpdesk_mgmt.created_ticket_template_sla_48hrs'). \
                send_mail(active_sla_ticket.id, force_send=True)
                self.sla_fallo = True

            #Send Email 72 hrs ---
            if  active_sla_ticket.sla_timer_format == '00:00' and active_sla_ticket.self.sla_cat == '72':
                self.env.ref('helpdesk_mgmt.created_ticket_template_sla_72hrs'). \
                send_mail(active_sla_ticket.id, force_send=True)
                self.sla_fallo = True    

    

    def pause_sla(self):
        self.sla_active = False

    def resume_sla(self):
        self.sla_active = True




    #CODIGO DE LAS OTRAS FUNCIONES 

    #Asignacion de empleado
    def send_user_mail(self):
        self.env.ref('helpdesk_mgmt.assignment_email_template'). \
            send_mail(self.id, force_send=True)

    def send_cierre_ticket(self):
        self.env.ref('helpdesk_mgmt.closed_ticket_template'). \
            send_mail(self.id, force_send=True)

    def send_partner_mail(self):
        self.env.ref('helpdesk_mgmt.created_ticket_template'). \
            send_mail(self.id, force_send=True)

    def assign_to_me(self):
        self.write({'user_id': self.env.user.id})

    def _compute_access_url(self):
        super(HelpdeskTicket, self)._compute_access_url()
        for ticket in self:
            ticket.access_url = '/my/ticket/%s' % (ticket.id)

    def partner_can_access(self):
        if not self.partner_id:
            return False
        user = self.env['res.users'].sudo().search([
            ('partner_id', '=', self.partner_id.id)])
        if not user:
            return False
        if not self.sudo(user.id).check_access_rights('read', raise_exception=False):
            return False
        else:
            return True

    def get_access_link(self):
        # _notify_get_action_link is not callable from email template
        return self._notify_get_action_link('view')

    @api.multi
    def _notify_get_groups(self, message, groups):
        groups = super(HelpdeskTicket, self)._notify_get_groups(message, groups)
        self.ensure_one()
        for group_name, group_method, group_data in groups:
            if group_name == 'portal':
                group_data['has_button_access'] = True
        return groups

    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        if self.partner_id:
            self.partner_name = self.partner_id.name
            self.partner_email = self.partner_id.email


    @api.onchange('employee_id')
    def _onchange_employee_id(self):
        if self.employee_id:
            self.employee_name = self.employee_id.name
            self.employee_email = self.employee_id.email


    @api.multi
    @api.onchange('team_id', 'user_id')
    def _onchange_dominion_user_id(self):
        if self.user_id:
            if self.user_id and self.user_ids and \
                    self.user_id not in self.user_ids:
                self.update({
                    'user_id': False
                })
                return {'domain': {'user_id': []}}
        if self.team_id:
            return {'domain': {'user_id': [('id', 'in', self.user_ids.ids)]}}
        else:
            return {'domain': {'user_id': []}}

    # ---------------------------------------------------
    # CRUD
    # ---------------------------------------------------

    @api.model
    def create(self, vals):
        
        if vals.get('number', '/') == '/':
            vals["number"] = self._prepare_ticket_number(vals)

        
        if vals.get("employee_id") and ("employee_name" not in vals or "employee_email" not in vals):
            partner = self.env["res.users"].browse(vals["employee_id"])
            vals.setdefault("employee_name", partner.name)
            vals.setdefault("employee_email", partner.email)

        if self.env.context.get('fetchmail_cron_running') and not vals.get('channel_id'):
            vals['channel_id'] = self.env.ref('helpdesk_mgmt.helpdesk_ticket_channel_email').id

        res = super().create(vals)


        # Check if mail to the user has to be sent
        if vals.get('user_id') and res:
            res.send_user_mail()
            res.message_subscribe(partner_ids=res.user_id.partner_id.ids)
        if  vals.get('team_id') and res:
            res.send_partner_mail()
            #if res.partner_id:
            #    res.message_subscribe(partner_ids=res.partner_id.ids)
        return res

    @api.multi
    def copy(self, default=None):
        self.ensure_one()
        if default is None:
            default = {}
        if "number" not in default:
            default["number"] = self._prepare_ticket_number(default)
        res = super(HelpdeskTicket, self).copy(default)
        return res

    @api.multi
    def write(self, vals):
        for ticket in self:
            now = fields.Datetime.now()
            if vals.get('stage_id'):
                stage_obj = self.env['helpdesk.ticket.stage'].browse([vals['stage_id']])
                vals['last_stage_update'] = now
                #Asignacion de cierre del ticket
                if stage_obj.closed:
                    vals['closed_date'] = now
                    #Envio de plantilla de correo de cierre
                    ticket.send_cierre_ticket()
                    #Se pausa el SLA
                    ticket.pause_sla()
            
            if vals.get('user_id'):
                vals['assigned_date'] = now

        res = super(HelpdeskTicket, self).write(vals)

        # Check if mail to the user has to be sent
        for ticket in self:
            if vals.get('user_id'):
                ticket.send_user_mail()
                ticket.message_subscribe(partner_ids=ticket.user_id.partner_id.ids)
        return res

    def _prepare_ticket_number(self, values):
        seq = self.env["ir.sequence"]
        if "company_id" in values:
            seq = seq.with_context(force_company=values["company_id"])
        return seq.next_by_code("helpdesk.ticket.sequence") or "/"

    # ---------------------------------------------------
    # Mail gateway
    # ---------------------------------------------------

    @api.multi
    def _track_template(self, tracking):
        res = super(HelpdeskTicket, self)._track_template(tracking)
        test_task = self[0]
        changes, tracking_value = tracking[test_task.id]
        if "stage_id" in changes and test_task.stage_id.mail_template_id:
            res['stage_id'] = (test_task.stage_id.mail_template_id,
                               {"composition_mode": "mass_mail"})

        return res

    @api.model
    def message_new(self, msg, custom_values=None):
        """ Override message_new from mail gateway so we can set correct
        default values.
        """
        if custom_values is None:
            custom_values = {}
        defaults = {
            'name': msg.get('subject') or _("No Subject"),
            'description': msg.get('body'),
            'partner_id': msg.get('author_id')
        }
        res = getaddresses([msg.get('from', '')])
        if res:
            defaults['partner_name'] = res[0][0]
            defaults['partner_email'] = res[0][1]
        defaults.update(custom_values)

        # Write default values coming from msg
        ticket = super().message_new(msg, custom_values=defaults)

        # Use mail gateway tools to search for partners to subscribe
        email_list = tools.email_split(
            (msg.get('to') or '') + ',' + (msg.get('cc') or '')
        )
        partner_ids = [p for p in ticket._find_partner_from_emails(
            email_list, force_create=False
        ) if p]
        ticket.message_subscribe(partner_ids)

        return ticket

    @api.multi
    def message_update(self, msg, update_vals=None):
        """ Override message_update to subscribe partners """
        email_list = tools.email_split(
            (msg.get('to') or '') + ',' + (msg.get('cc') or '')
        )
        partner_ids = [p for p in self._find_partner_from_emails(
            email_list, force_create=False
        ) if p]
        self.message_subscribe(partner_ids)
        return super().message_update(msg, update_vals=update_vals)

    @api.multi
    def message_get_suggested_recipients(self):
        recipients = super().message_get_suggested_recipients()

        for ticket in self:
            reason = _('Partner Email') \
                if ticket.partner_id and ticket.partner_id.email \
                else _('Partner Id')

            if ticket.partner_id and ticket.partner_id.email:
                ticket._message_add_suggested_recipient(
                    recipients,
                    partner=ticket.partner_id,
                    reason=reason
                )
            elif ticket.partner_email:
                ticket._message_add_suggested_recipient(
                    recipients,
                    email=ticket.partner_email,
                    reason=reason
                )
        return recipients
