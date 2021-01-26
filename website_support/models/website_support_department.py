# -*- coding: utf-8 -*-
import datetime

from odoo import api, fields, models

class WebsiteSupportDepartment(models.Model):

    _name = "website.support.department"

    name = fields.Char(string="Nombre", translate=True)
    manager_ids = fields.One2many('website.support.department.contact', 'wsd_id', string="Gerentes")
    partner_ids = fields.Many2many('res.partner', string="Contactos")
    sub_category_ids = fields.One2many('website.support.department.subcategory', 'wsd_id', string="Sub Categoriqs", compute='_compute_sub_category_ids')
    sub_category_month_ids = fields.One2many('website.support.department.subcategory', 'wsd_month_id', string="Sub Categorias Mensuales", compute='_compute_sub_category_month_ids')
    sub_category_week_ids = fields.One2many('website.support.department.subcategory', 'wsd_week_id', string="Sub Categorías Semanales", compute='_compute_sub_category_week_ids')
    submit_ticket_contact_ids = fields.One2many('website.support.department.submit', 'wsd_id', string="Contactos Tickets Enviados", compute='_compute_submit_ticket_contact_ids')
    submit_ticket_contact_month_ids = fields.One2many('website.support.department.submit', 'wsd_month_id', string="Contactos Tickets Enviados Mensual", compute='_compute_submit_ticket_contact_month_ids')
    submit_ticket_contact_week_ids = fields.One2many('website.support.department.submit', 'wsd_week_id', string="Contactos Tickets Enviados Semanales", compute='_compute_submit_ticket_contact_week_ids')

    #-------------- Sub Category Stats --------------------------

    @api.one
    @api.depends('manager_ids', 'partner_ids')
    def _compute_sub_category_ids(self):

        #Unlink all existing records
        for si in self.env['website.support.department.subcategory'].search([('wsd_id', '=', self.id)]):
            si.unlink()

        extra_access = []
        for extra_permission in self.partner_ids:
            extra_access.append(extra_permission.id)

        for sub_category in self.env['website.support.ticket.subcategory'].search([]):
            count = self.env['website.support.ticket'].search_count(['|', ('partner_id','=', self.env.user.partner_id.id), ('partner_id', 'in', extra_access), ('partner_id','!=',False), ('sub_category_id','=', sub_category.id)])
            if count > 0:
                self.env['website.support.department.subcategory'].create( {'wsd_id': self.id, 'subcategory_id': sub_category.id, 'count': count} )

        self.sub_category_ids = self.env['website.support.department.subcategory'].search([('wsd_id', '=', self.id)], limit=5)

    @api.one
    @api.depends('manager_ids', 'partner_ids')
    def _compute_sub_category_month_ids(self):

        #Unlink all existing records
        for si in self.env['website.support.department.subcategory'].search([('wsd_month_id', '=', self.id)]):
            si.unlink()

        extra_access = []
        for extra_permission in self.partner_ids:
            extra_access.append(extra_permission.id)

        for sub_category in self.env['website.support.ticket.subcategory'].search([]):
            month_ago = (datetime.datetime.now() - datetime.timedelta(days=30) ).strftime("%Y-%m-%d %H:%M:%S")
            count = self.env['website.support.ticket'].search_count(['|', ('partner_id','=', self.env.user.partner_id.id), ('partner_id', 'in', extra_access), ('partner_id','!=',False), ('sub_category_id','=', sub_category.id), ('create_date','>', month_ago ) ])
            if count > 0:
                self.env['website.support.department.subcategory'].create( {'wsd_month_id': self.id, 'subcategory_id': sub_category.id, 'count': count} )

        self.sub_category_month_ids = self.env['website.support.department.subcategory'].search([('wsd_month_id', '=', self.id)], limit=5)

    @api.one
    @api.depends('manager_ids', 'partner_ids')
    def _compute_sub_category_week_ids(self):

        #Unlink all existing records
        for si in self.env['website.support.department.subcategory'].search([('wsd_week_id', '=', self.id)]):
            si.unlink()

        extra_access = []
        for extra_permission in self.partner_ids:
            extra_access.append(extra_permission.id)

        for sub_category in self.env['website.support.ticket.subcategory'].search([]):
            week_ago = (datetime.datetime.now() - datetime.timedelta(days=7) ).strftime("%Y-%m-%d %H:%M:%S")
            count = self.env['website.support.ticket'].search_count(['|', ('partner_id','=', self.env.user.partner_id.id), ('partner_id', 'in', extra_access), ('partner_id','!=',False), ('sub_category_id','=', sub_category.id), ('create_date','>', week_ago ) ])
            if count > 0:
                self.env['website.support.department.subcategory'].create( {'wsd_week_id': self.id, 'subcategory_id': sub_category.id, 'count': count} )

        self.sub_category_week_ids = self.env['website.support.department.subcategory'].search([('wsd_week_id', '=', self.id)], limit=5)

    #-------------- Ticket Submit Stats --------------------------

    @api.one
    @api.depends('manager_ids', 'partner_ids')
    def _compute_submit_ticket_contact_ids(self):

        #Unlink all existing records
        for si in self.env['website.support.department.submit'].search([('wsd_id', '=', self.id)]):
            si.unlink()

        for contact in self.partner_ids:
            count = self.env['website.support.ticket'].search_count([('partner_id','=', contact.id)])
            if count > 0:
                self.env['website.support.department.submit'].create( {'wsd_id': self.id, 'partner_id': contact.id, 'count': count} )

        self.submit_ticket_contact_ids = self.env['website.support.department.submit'].search([('wsd_id', '=', self.id)], limit=5)

    @api.one
    @api.depends('manager_ids', 'partner_ids')
    def _compute_submit_ticket_contact_month_ids(self):

        #Unlink all existing records
        for si in self.env['website.support.department.submit'].search([('wsd_month_id', '=', self.id)]):
            si.unlink()

        for contact in self.partner_ids:

            month_ago = (datetime.datetime.now() - datetime.timedelta(days=30) ).strftime("%Y-%m-%d %H:%M:%S")
            count = self.env['website.support.ticket'].search_count([('partner_id','=', contact.id), ('create_date','>', month_ago ) ])
            if count > 0:
                self.env['website.support.department.submit'].create( {'wsd_month_id': self.id, 'partner_id': contact.id, 'count': count} )

        self.submit_ticket_contact_month_ids = self.env['website.support.department.submit'].search([('wsd_month_id', '=', self.id)], limit=5)

    @api.one
    @api.depends('manager_ids', 'partner_ids')
    def _compute_submit_ticket_contact_week_ids(self):

        #Unlink all existing records
        for si in self.env['website.support.department.submit'].search([('wsd_week_id', '=', self.id)]):
            si.unlink()

        for contact in self.partner_ids:
            week_ago = (datetime.datetime.now() - datetime.timedelta(days=7) ).strftime("%Y-%m-%d %H:%M:%S")
            count = self.env['website.support.ticket'].search_count([('partner_id','=', contact.id), ('create_date','>', week_ago )])
            if count > 0:
                self.env['website.support.department.submit'].create( {'wsd_week_id': self.id, 'partner_id': contact.id, 'count': count} )

        self.submit_ticket_contact_week_ids = self.env['website.support.department.submit'].search([('wsd_week_id', '=', self.id)], limit=5)

class WebsiteSupportDepartmentContact(models.Model):

    _name = "website.support.department.contact"

    def _default_role(self):
        return self.env['ir.model.data'].get_object('website_support','website_support_department_manager')

    wsd_id = fields.Many2one('website.support.department', string="Department")
    role = fields.Many2one('website.support.department.role', string="Role", required="True", default=_default_role)
    user_id = fields.Many2one('res.users', string="User", required="True")

class WebsiteSupportDepartmentRole(models.Model):

    _name = "website.support.department.role"

    name = fields.Char(string="Name", translate=True)
    view_department_tickets = fields.Boolean(string="View Department Tickets")

class WebsiteSupportDepartmentSubcategory(models.Model):

    _name = "website.support.department.subcategory"
    _order = "count desc"

    wsd_id = fields.Many2one('website.support.department', string="Departamento")
    wsd_month_id = fields.Many2one('website.support.department', string="Departamento")
    wsd_week_id = fields.Many2one('website.support.department', string="Departamento")
    subcategory_id = fields.Many2one('website.support.ticket.subcategory', string="Sub Categoria")
    count = fields.Integer(string="Count")

class WebsiteSupportDepartmentSubmit(models.Model):

    _name = "website.support.department.submit"
    _order = "count desc"

    wsd_id = fields.Many2one('website.support.department', string="Departamento")
    wsd_month_id = fields.Many2one('website.support.department', string="Departamento")
    wsd_week_id = fields.Many2one('website.support.department', string="Departamento")
    partner_id = fields.Many2one('res.partner', string="Contact")
    count = fields.Integer(string="Conteo")