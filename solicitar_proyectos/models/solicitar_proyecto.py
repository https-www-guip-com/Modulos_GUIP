# -*- coding: utf-8 -*-
from odoo import api, fields, models
from datetime import date
from datetime import datetime
from datetime import *
import datetime
from odoo.exceptions import UserError, ValidationError

class Solicitar_Proyectos_Herencia(models.Model):
    _inherit = "project.project"
    
    objetivo = fields.Char("Objetivo",  required=True)
    descrpcion_breve = fields.Char("Descripcion breve")
    descrpcion_completa = fields.Text("Descripcion Completa",  required=True)
    fecha_inicio = fields.Date("Fecha Inicio",  required=True)
    fecha_fin = fields.Date("Fecha Fin",  required=True)
    proyecto_seleccionar_id = fields.Many2one('model_solicitar_proyectos', string="Inicio Del Proyecto", 
                                  ondelete='cascade', index=True)

    #today = date.today()

    @api.multi
    def finalizar_proyecto(self):
        stage = self.env['model_solicitar_proyectos'].search([('id', '=', self.proyecto_seleccionar_id.id)], limit=1)
        if stage.fase_proyecto == '5':
           self.env.user.notify_info(message='El proyecto ya esta finalizado')
        else:
            today = date.today()
            stage.write({'fase_proyecto':'5'})
            stage.write({'fecha_fin': today})
            #Envio de correo al creador del proyecto confirmando la eliminacion del proyecto
            self.env.ref('solicitar_proyectos.mail_template_finalizacion_proyecto'). \
            send_mail(self.id, force_send=True)
            self.env.user.notify_success(message='Proyecto finalizado correctamente.')
        return stage

class Solicitar_Proyectos_Herencia_Tareas(models.Model):
    _inherit = "project.task"
    codigo_tarea = fields.Integer("Codigo Tarea SL")
    tarea_seleccionar_id = fields.Many2one('model_solicitar_tareas', string="Inicio Tarea", 
                                  ondelete='cascade', index=True) 

class Solicitar_Proyectos(models.Model):
    _name = "model_solicitar_proyectos"
    _description = "Solicitud De Proyectos"
    _rec_name = "nombre_proyec"
    
    #Esta herencia funciona para que se pueda mostrar el pie de pagina en los formularios con las notas y poder enviar correos
    _inherit = ['mail.thread', 'mail.activity.mixin']

    fase_proyecto = fields.Selection([('1', 'Borrador'),('2', 'Esperando Aprobacion'),('3', 'Aprobado'),('4', 'Rechazado'),('5', 'Finalizado')], 
                                   default="1",
                                   string='Estado')
       
    employee_id = fields.Many2one('res.users', string='Creador', default=lambda self: self.env.user, track_visibility="onchange")
    #user_id = fields.Many2one('res.users', string="Comercial", 
    #                              ondelete='cascade', index=True)
                                  
    nombre_proyec = fields.Char("Nombre Proyecto",  required=True)
    fecha_inicio = fields.Date("Fecha Inicio",  required=True)
    fecha_fin = fields.Date("Fecha Fin")
    objetivo = fields.Char("Objetivo",  required=True)
    descrpcion_breve = fields.Char("Descripcion breve")
    descrpcion_completa = fields.Text("Descripcion Completa",  required=True)
    proyecto_tareas_ids = fields.One2many('model_solicitar_tareas','proyecto_tareas_id')
    
        
    proyecto_id = fields.Many2one('project.project', string="Seguimiento Del proyecto", 
                                  help="Desde este campo puedes ver el seguimiento individual de las tareas y mirar en que etapa va el proyecto" ,
                                  ondelete='cascade', index=True)

    tag_ids = tag_ids = fields.Many2many('proyecto_lead_tag', string='Etiquetas', help="Clasifica los proyectos por categorias")
    seguidores_ids = fields.Many2many('res.users', string='Seguidores', track_visibility="onchange",
                                       help="En esta parte puedes agregar varios seguidores en el poryecto el cual miraran el proceso del proeycto")
     

    company_id = fields.Many2one(
        'res.company',
        string="Compañia",
        default=lambda self: self.env['res.company']._company_default_get('model_solicitar_proyectos')
    )

    #Funcion que valida las fechas. 

    @api.multi
    def validacion_aprobacion(self):
        stage = self.env['model_solicitar_proyectos'].search([('id', '=', self.id)], limit=1)
                         
        if self.fase_proyecto == '1':
              stage = self.write({'fase_proyecto':'2'})
              self.env.user.notify_success(message='Enviado Correctamente.')
        else: 
            self.env.user.notify_info(message='El proyecto esta en la fase '  +' ' + self.fase_proyecto ) 
        return stage       
    
    #FUNCION QUE ENVIA EL PROYECTO AL MODULO DE PROYECTO. 
    @api.multi
    def validacion_aprobacion_gerencia(self):
        stage = self.env['model_solicitar_proyectos'].search([('id', '=', self.id)], limit=1)
        if self.fase_proyecto == '1' or self.fase_proyecto == '2':
            
            stage = self.write({'fase_proyecto':'3'})
            
            project_crear = self.env['project.project']
            tareas_crear = self.env['project.task']  
            
            project_line_vals = {
                    'name':self.nombre_proyec,
                    'sequence':10,
                    'objetivo':self.objetivo,
                    'descrpcion_breve':self.descrpcion_breve,
                    'fecha_inicio':self.fecha_inicio,
                    'fecha_fin':self.fecha_fin,
                    'descrpcion_completa':self.descrpcion_completa,
                    'proyecto_seleccionar_id':self.id,
                    }
            res = project_crear.create(project_line_vals)
            

            for p_line in self.proyecto_tareas_ids: 
                #Creacion de tareas
                tareas_line_vals = {
                        'project_id':res.id,
                        'name': p_line.nombre_tarea,
                        'description': p_line.descripcion_tarea,
                        'codigo_tarea' : p_line.id,
                        'tarea_seleccionar_id.id' : p_line.id,
                        }
                tareas_crear.create(tareas_line_vals)

            #recorrer_tareas = self.env['model_solicitar_tareas'].search([('proyecto_tareas_id.id', '=', self.proyecto_tareas_ids.id)]) 
            for record in self.proyecto_tareas_ids:
                record.write({
                        'proyecto_seleccionar_id.id': record.id,
                        'codigo_tarea': record.id
                    })


            stage = self.write({'proyecto_id':res.id}) 
            #Aprobacion de correo
            self.env.ref('solicitar_proyectos.mail_template_solicitar'). \
            send_mail(self.id, force_send=True)
            #Envio de correo a seguidores para informarles que se han agregado a este proyecto
            self.send_user_mail()
            
            #self.env.ref('solicitar_proyectos.mail_template_solicitar_asignado'). \
            #send_mail(self.id, force_send=True)
            #Notificacion sistema
            self.env.user.notify_success(message='Se creo el proyecto correctamente.')
        
        elif self.fase_proyecto == '4': 
            self.env.user.notify_warning(message='El proyecto esta rechazado, cambie el proyecto a borrador')
        elif self.fase_proyecto == '3': 
            self.env.user.notify_info(message='Ya se encuentra aprobado este proyecto')
        elif self.fase_proyecto == '5':
            self.env.user.notify_info(message='El proyecto ya esta finalizado, no se puede aprobar de nuevo')   
        return stage    
    
    @api.multi
    def cancelar_aprobacion_gerencia(self):
        stage = self.env['model_solicitar_proyectos'].search([('id', '=', self.id)], limit=1)

        if self.fase_proyecto == '1' or self.fase_proyecto == '2':
           stage = self.write({'fase_proyecto':'4'}) 
           self.env.user.notify_success(message='Se rechazo correctamente')
        elif self.fase_proyecto == '3':
            self.env.user.notify_warning(message='El proyecto ya esta aprobado, no se puede rechazado')
        elif self.fase_proyecto == '4':
            self.env.user.notify_info(message='El proyecto ya esta rechazado')
        elif self.fase_proyecto == '5':
            self.env.user.notify_info(message='El proyecto ya esta finalizado, no se puede rechazar')     
       
            
        return stage

    @api.multi
    def borrador_aprobacion_gerencia(self):
        stage = self.env['model_solicitar_proyectos'].search([('id', '=', self.id)], limit=1)
                         
        if self.fase_proyecto == '4':
            stage = self.write({'fase_proyecto':'1'}) 
            self.env.user.notify_success(message='Se envio correctamente')
        else:
            self.env.user.notify_info(message='Se tiene que cancelar para pasar a borrador el proyecto') 
        return stage        

    #Actualizar Tareas despues de que ya esta creado el proyecto. 
    @api.multi
    def actualizar_tareas(self):
        
        tareas_crear = self.env['project.task']
        stage = self.env['project.project'].search([('proyecto_seleccionar_id.id', '=', self.id)], limit=1)
        total = []
        
        if self.fase_proyecto == '3':
            if self.proyecto_tareas_ids:
                n1 = 0
                for p_tareas_soli in self.proyecto_tareas_ids: 
                    if p_tareas_soli.codigo_tarea == 0:
                        #Creacion de tareas
                        n1 += 1 
                        tareas_line_vals = {
                                'project_id':self.proyecto_id.id,
                                'name': p_tareas_soli.nombre_tarea,
                                'description': p_tareas_soli.descripcion_tarea,
                                'codigo_tarea' : p_tareas_soli.id,
                                'tarea_seleccionar_id.id' : p_tareas_soli.id,
                                }
                        tareas_crear.create(tareas_line_vals)
                        
                        p_tareas_soli.write({
                                'proyecto_seleccionar_id': p_tareas_soli.id,
                                'codigo_tarea': p_tareas_soli.id
                            })
                        
                if n1 > 0:
                    #Envio de correo al responsable del poryecto diciendole que se han asignado nuevas tareas
                    self.env.ref('solicitar_proyectos.mail_template_nuevas_tareas'). \
                    send_mail(self.id, force_send=True)
                    self.env.user.notify_success(message='Tareas Nuevas Agregadas Correctamente')
                else:
                   self.env.user.notify_info(message='No hay tareas nuevas, para agregar')
            else:
                self.env.user.notify_info(message='No hay tareas agregadas para actualizar')
        else:     
            self.env.user.notify_info(message='Para actualizar sus tareas tiene que estar aprobado el proyecto')

    #Estos dos metodos sirven para enviar multiples correos a varios seguidores
    #Obtengo los correos de los seguidores
    @api.multi
    def correos_seguidores_mail(self):
        lista_correos = []
        for plp in self.seguidores_ids: 
            lista_correos.append(plp.email)
        return ",".join(lista_correos)
        
    #Envio de correos a todos los seguidores
    @api.multi
    def send_user_mail(self): 
        self.env.ref('solicitar_proyectos.mail_template_solicitar_asignado'). \
        send_mail(self.id, force_send=True)

class Tag_Proyectos(models.Model):
    _name = "proyecto_lead_tag"
    _description = "Etiquetas de proyectos"
    
    name = fields.Char('Nombre', required=True, translate=True)
    color = fields.Integer('Color Index')

    _sql_constraints = [
        ('name_uniq', 'unique (name)', "El nombre de la etiqueta ya existe !"),
    ]