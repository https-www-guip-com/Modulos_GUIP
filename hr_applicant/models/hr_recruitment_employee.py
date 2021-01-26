# See LICENSE file for full copyright and licensing details.

from datetime import datetime
from odoo import api, fields, models
from odoo.exceptions import ValidationError
from odoo.tools.translate import _
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT


class Employee(models.Model):
    _inherit = "hr.employee"

    @api.depends('medical_ids')
    def _compute_no_of_medical(self):
        for rec in self:
            rec.no_of_medical = len(rec.medical_ids.ids)

    @api.depends('prev_occu_ids')
    def _compute_no_of_prev_occu(self):
        for rec in self:
            rec.no_of_prev_occu = len(rec.prev_occu_ids.ids)

    @api.depends('relative_ids')
    def _compute_no_of_relative(self):
        for rec in self:
            rec.no_of_relative = len(rec.relative_ids.ids)

    @api.depends('education_ids')
    def _compute_no_of_education(self):
        for rec in self:
            rec.no_of_education = len(rec.education_ids.ids)

    @api.depends('prev_travel_ids')
    def _compute_no_of_prev_travel(self):
        for rec in self:
            rec.no_of_prev_travel = len(rec.prev_travel_ids.ids)

    @api.depends('lang_ids')
    def _compute_no_of_lang(self):
        for rec in self:
            rec.no_of_lang = len(rec.lang_ids.ids)

    medical_ids = fields.One2many(
        'hr.employee.medical.details', 'employee_id', 'Medical Ref.')
    no_of_medical = fields.Integer(
        'No of Medical Detials', compute='_compute_no_of_medical',
        readonly=True)
    prev_occu_ids = fields.One2many(
        'employee.previous.occupation', 'employee_id', 'Prev. Occupacion Ref.')
    no_of_prev_occu = fields.Integer(
        'No of Prev. Occupation', compute='_compute_no_of_prev_occu',
        readonly=True)
    relative_ids = fields.One2many(
        'employee.relative', 'employee_id', 'Relative Ref.')
    no_of_relative = fields.Integer(
        'No of Relative', compute='_compute_no_of_relative', readonly=True)
    education_ids = fields.One2many(
        'employee.education', 'employee_id', 'Educacion Ref.')
    no_of_education = fields.Integer(
        'No of Education', compute='_compute_no_of_education', readonly=True)
    prev_travel_ids = fields.One2many(
        'employee.previous.travel', 'employee_id', 'Previous Travel Ref.')
    no_of_prev_travel = fields.Integer(
        'No of Previous Travel', compute='_compute_no_of_prev_travel',
        readonly=True)
    lang_ids = fields.One2many(
        'employee.language', 'employee_id', 'Languaje Ref.')
    no_of_lang = fields.Integer(
        'No of Language', compute='_compute_no_of_lang', readonly=True)


class EmployeeMedicalDetails(models.Model):

    _name = "hr.employee.medical.details"
    _description = "Employee Medical Details"
    _rec_name = 'medical_examination'

    comentarios = fields.Char('Comentarios')
    medical_examination = fields.Char('Examenes Medicos')
    vital_sign = fields.Char('Signos Vitales')
    date = fields.Date(
        'Fecha', default=fields.Date.context_today, readonly=True)
    doc_comment = fields.Char('Comentarios del Doctor')

    head_face_scalp = fields.Selection(
        [('Abnormal', 'Abnormal'), ('Normal', 'Normal')], 'Cabeza, Cara, Cuero cabelludo')
    nose_sinuses = fields.Selection(
        [('Abnormal', 'Abnormal'), ('Normal', 'Normal')], 'Nariz/Senos')
    mouth_throat = fields.Selection(
        [('Abnormal', 'Abnormal'), ('Normal', 'Normal')], 'Boca/Garganta')
    ears_tms = fields.Selection(
        [('Abnormal', 'Abnormal'), ('Normal', 'Normal')], 'Orejas/TMs')
    eyes_pupils_ocular = fields.Selection(
        [('Abnormal', 'Abnormal'), ('Normal', 'Normal')],
        'Ojos/Pupilas/Motilidad ocular')
    heart_vascular_system = fields.Selection(
        [('Abnormal', 'Abnormal'), ('Normal', 'Normal')],
        'Corazón/Sistema vascular')
    lungs = fields.Selection(
        [('Abnormal', 'Abnormal'), ('Normal', 'Normal')], 'Pulmones')
    abdomen_hernia = fields.Selection(
        [('Abnormal', 'Abnormal'), ('Normal', 'Normal')], 'Abdomen/Hernia')
    msk_strengh = fields.Selection(
        [('Abnormal', 'Abnormal'), ('Normal', 'Normal')], 'MSK-Strength')
    neurological = fields.Selection(
        [('Abnormal', 'Abnormal'), ('Normal', 'Normal')],
        'Neurológico (reflejos, sensación)')
    glasses_needed = fields.Boolean('¿Necesita Lentes?')
    urine_drug_serene = fields.Selection(
        [('Negetivo', 'Negativo'), ('Positivo', 'Positivo')],
        '¿Padece de alguna enfermedad actualmente?')
    fit_for_full_duty = fields.Boolean('¿Enfermedad Congenita/Hereditaria?')

    good_health = fields.Boolean('¿Toma algún medicamento de uso permanente?')
    serious_illness = fields.Boolean('¿Ha tenido alguna cirugía u operación ya sea por una enfermedad o accidente?')
    broken_bones = fields.Boolean('¿Huesos rotos?')
    medications = fields.Boolean('¿Medicamentos en este momento?')
    serious_wound = fields.Boolean('¿Herida seria?')
    allergic = fields.Boolean('¿Alérgico a cualquier medicamento?')
    epilepsy = fields.Boolean('Epilepsia')
    history_drug_use = fields.Boolean('¿Alguna historia de uso de drogas?')

    employee_id = fields.Many2one(
        'hr.employee', 'Employee Ref', ondelete='cascade')
    active = fields.Boolean(string='Activo', default=True)
    blood_name = fields.Selection(
        [('A', 'A'), ('B', 'B'), ('O', 'O'), ('AB', 'AB')], "Tipo Sangre")
    blood_type = fields.Selection([('+', '+'), ('-', '-')], 'Tipo Sangre')

    @api.model
    def create(self, vals):
        if (self._context.get('active_model') == 'hr.employee' and
                self._context.get('active_id')):
            vals.update({'employee_id': self._context.get('active_id')})
        return super(EmployeeMedicalDetails, self).create(vals)


class EmployeePreviousOccupation(models.Model):

    _name = "employee.previous.occupation"
    _description = "Recruite Previous Occupation"
    _order = 'to_date desc'
    _rec_name = 'position'

    from_date = fields.Date(string='Fecha Inicial', required=True)
    to_date = fields.Date(string='Fecha Fin', required=True)
    position = fields.Char(string='Posicion', required=True)
    organization = fields.Char(string='Organizacion')
    ref_name = fields.Char(string='Nombre de Referencia')
    ref_position = fields.Char(string='Posición de Referencia')
    ref_phone = fields.Char(string='Tel Referencia')
    active = fields.Boolean(string='Activo', default=True)
    employee_id = fields.Many2one(
        'hr.employee', 'Employee Ref', ondelete='cascade')
    email = fields.Char('Correo Electronico')

    @api.model
    def create(self, vals):
        if (self._context.get('active_model') == 'hr.employee' and
                self._context.get('active_id')):
            vals.update({'employee_id': self._context.get('active_id')})
        return super(EmployeePreviousOccupation, self).create(vals)


class EmployeeRelative(models.Model):

    _name = 'employee.relative'
    _description = "Employee Relatives"
    _rec_name = 'name'

    relative_type = fields.Selection([('Tia', 'Tia'),
                                      ('Hermano', 'Hermano'),
                                      ('Hija', 'Hija'),
                                      ('Padre', 'Padre'),
                                      ('Esposo', 'Esposo'),
                                      ('Madre', 'Madre'),
                                      ('Hermana', 'Hermana'),
                                      ('Hijo', 'Hijo'), ('Tio', 'Tio'),
                                      ('Esposa', 'Esposa'), ('Otros', 'Otros')],
                                     string='Tipo Parientes', required=True)
    name = fields.Char(string='Nombre', size=128, required=True)
    birthday = fields.Date(string='Fecha Nacimiento')
    place_of_birth = fields.Char(string='Lugar de nacimiento', size=128)
    occupation = fields.Char(string='Ocupacion', size=128)
    gender = fields.Selection([('Masculino', 'Masculino'), 
                               ('Femenino', 'Femenino')], 
                               string='Genero',
                               required=False)
    active = fields.Boolean(string='Activo', default=True)
    employee_id = fields.Many2one(
        'hr.employee', 'Employee Ref', ondelete='cascade')

    @api.model
    def create(self, vals):
        if (self._context.get('active_model') == 'hr.employee' and
                self._context.get('active_id')):
            vals.update({'employee_id': self._context.get('active_id')})
        return super(EmployeeRelative, self).create(vals)


class EmployeeEducation(models.Model):
    _name = "employee.education"
    _description = "Employee Education"
    _rec_name = "from_date"
    _order = "from_date"

    from_date = fields.Date(string='Fecha Inicial')
    to_date = fields.Date(string='Fecha Final')
    education_rank = fields.Selection(
        [('1', 'Licenciatura en Derecho'), ('2', 'Licenciatura en Periodismo'), ('3', 'Licenciatura en Psicologia'), ('4', 'Licenciatura en Lenguas Extranjeras '), 
        ('5', 'Licenciatura en Mercadotecnia'), ('6', 'Licenciatura en Informatica Administrativa'), 
        ('7', 'Licenciatura en Comercio Internacional'), ('8', 'Licenciatura en Economia'), 
        ('9', 'Licenciatura en Administración de Empresas'), ('10', 'Licenciatura en Letras'),
        ('11', 'Licenciatura en Diseño Gráfico'), ('12', 'Licenciatura en Recursos Humanos'),
        ('13', 'Licenciatura en Periodismo'), ('14', 'Licenciatura en Derecho'), 
        ('15', 'Ingenieria en Informatica'), ('16', 'Ingenieria Forestal'), 
        ('17', 'Ingenieria en Gestión Logística'), ('18', 'Ingenieria en Electrónica'),('19', 'Ingenieria Mecanica Industrial'),
        ('20', 'Ingenieria Civil'), ('21', 'Ingenieria Industrial'), ('22', 'Ingenieria en Sistemas'), 
        ('23', 'Maestria en Gestión del Riesgo y Manejo de Desastres'), 
        ('24', 'Maestria en Matematica con orientación en Ingenieria Matematica y Estadistica Matematica'), ('25', 'Maestria en Fisica'),
        ('26', 'Maestria en Derechos Humanos y Desarrollo'),('27', 'Maestria en Gestión Informatica'),
        ('28', 'Maestria en Mercadotecnia con Enfasis en Negocios Internacionales'),('29', 'Maestria en Gestión de Tecnologias de Informacion'),
        ('30', 'Maestria en Gestion de Operaciones y Logistica'), ('31', 'Maestria en Administración de Proyectos'),
        ('32', 'Maestria en Dirección Empresarial'), ('33', 'Maestria en Finanzas'), ('34', 'Maestria en Dirección de Recursos Humanos'),
        ('35', 'Maestria en Derecho empresarial'),('36', 'Otros')
         ],  string='Carrera',
        default="1")

    estudiante_sigue = fields.Boolean('Sigue Estudiando(a)')

    school_name = fields.Char(string='Nombre Institucion', size=256)
    grade =  fields.Selection(
        [('1', 'Secundaria Completa'), ('2', 'Secundaria Incompleta'), ('3', 'Pregrado completo'), ('4', 'Pregrado Incompleto'), 
        ('5', 'Maestria o Doctorado Completo'), ('6', 'Maestria o Doctorado Incompleto')],  string='Nivel de estudio',
        default="3")
    field = fields.Char(string='Titulo Obtenido', size=128)
    illiterate = fields.Boolean('Analfabeta')
    active = fields.Boolean(string='Activo', default=True)
    employee_id = fields.Many2one(
        'hr.employee', 'Employee Ref', ondelete='cascade')
    edu_type = fields.Selection(
        [('Local', 'Local'), ('Extranjera', 'Extranjera')], 'Ubicacion Institucion',
        default="Local")
    country_id = fields.Many2one('res.country', 'País')
    state_id = fields.Many2one('res.country.state', 'Departamento')
    province = fields.Char("Municipio")

    @api.onchange('edu_type')
    def onchange_edu_type(self):
        for rec in self:
            if rec.edu_type == 'Local':
                rec.abroad_country_id = False
            else:
                rec.local_province_id = False
                rec.local_district_id = False

    @api.onchange('estudiante_sigue')
    def sigue_estudiando(self):
        for rec in self:
            rec.to_date = False
            
    @api.onchange('illiterate')
    def onchange_illiterate(self):
        for rec in self:
            rec.from_date = False
            rec.to_date = False
            rec.education_rank = ''
            rec.school_name = ''
            rec.grade = ''
            rec.field = ''
            rec.edu_type = ''
            rec.country_id = False
            rec.state_id = False
            rec.province = ''

    @api.model
    def create(self, vals):
        if (self._context.get('active_model') == 'hr.employee' and
                self._context.get('active_id')):
            vals.update({'employee_id': self._context.get('active_id')})
        return super(EmployeeEducation, self).create(vals)

    


class EmployeePreviousTravel(models.Model):
    _name = "employee.previous.travel"
    _description = "Employee Previous Travel"
    _rec_name = "from_date"
    _order = "from_date"

    from_date = fields.Date(string='Fecha Inicial', required=True)
    to_date = fields.Date(string='Fecha Fin', required=True)
    location = fields.Char(string='ubicación', size=128, required=True)
    reason = fields.Char('Razón', required=True)
    active = fields.Boolean(string='Activo', default=True)
    employee_id = fields.Many2one(
        'hr.employee', 'Employee Ref', ondelete='cascade')

    @api.model
    def create(self, vals):
        if (self._context.get('active_model') == 'hr.employee' and
                self._context.get('active_id')):
            vals.update({'employee_id': self._context.get('active_id')})
        return super(EmployeePreviousTravel, self).create(vals)


class EmployeeLanguage(models.Model):
    _name = "employee.language"
    _description = "Employee Language"
    _rec_name = "language"
    _order = "id desc"

    language = fields.Char('Lenguaje', required=True)
    read_lang = fields.Selection(
        [('Excelente', 'Excelente'), ('Bueno', 'Bueno'), ('Pobre', 'Pobre')],
        string='Read')
    write_lang = fields.Selection(
        [('Excelente', 'Excelente'), ('Bueno', 'Bueno'), ('Pobre', 'Pobre')],
        string='Write')
    speak_lang = fields.Selection(
        [('Excelente', 'Excelente'), ('Bueno', 'Bueno'), ('Pobre', 'Pobre')],
        string='Speak')
    active = fields.Boolean(string='Active', default=True)
    employee_id = fields.Many2one(
        'hr.employee', 'Employee Ref', ondelete='cascade')
    mother_tongue = fields.Boolean('Lengua materna')

    @api.constrains('mother_tongue')
    def _check_mother_tongue(self):
        self.ensure_one()
        if self.mother_tongue and self.employee_id:
            language_rec = self.search([
                ('employee_id', '=', self.employee_id.id),
                ('mother_tongue', '=', True), ('id', '!=', self.id)],
                limit=1)
            if language_rec:
                raise ValidationError(_("If you want to set '%s' \
                    as a mother tongue, first you have to uncheck mother \
                    tongue in '%s' language.") % (
                    self.language, language_rec.language))

    @api.model
    def create(self, vals):
        if self._context.get('active_model') == 'hr.employee' and \
                self._context.get('active_id'):
            vals.update({'employee_id': self._context.get('active_id')})
        return super(EmployeeLanguage, self).create(vals)
