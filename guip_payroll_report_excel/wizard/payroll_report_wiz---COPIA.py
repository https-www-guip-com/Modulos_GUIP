
import base64
import os
from datetime import date
from datetime import datetime
from datetime import *
import datetime
from odoo.tools.float_utils import float_round
from dateutil.relativedelta import relativedelta

from io import BytesIO
import xlsxwriter
from PIL import Image as Image
from odoo import fields, models, api, _
from odoo.exceptions import ValidationError
from xlsxwriter.utility import xl_rowcol_to_cell

    
#CODIGO AGREGADO POR ARIEL CERRRATO CODIGO BUENO.


class payroll_report_excel(models.TransientModel):
    _name = 'payroll.report.excel'

    name = fields.Char('File Name', size=256, readonly=True)
    file_download = fields.Binary('Download payroll', readonly=True)

class Rule(models.Model):
    _inherit = 'hr.salary.rule'

    add_rule_ids = fields.Many2many('hr.salary.rule',
                                    relation='add_rule_tbl',
                                    column1='r_id',
                                    column2='r1_id',
                                    string='Add Rules')
    sub_rule_ids = fields.Many2many('hr.salary.rule',
                                    relation='sub_rule_tbl',
                                    column1='r_id',
                                    column2='r1_id',
                                    string='Sub Rules')

class hr_payslip(models.Model):
    _inherit = 'hr.payslip'
    
    
    @api.one
    def get_amount_from_rule_code(self, rule_code):
        line = self.env['hr.payslip.line'].search([('slip_id', '=', self.id), ('code', '=', rule_code)])
        if line:
            return round(line.total, 2)
        else:
            return 0.0

    @api.one
    def update_sheet(self):
        for slip_line in self.env['hr.payslip.line'].search([('slip_id', '=', self.id)]):
            final_total = 0
            if slip_line.salary_rule_id.add_rule_ids or slip_line.salary_rule_id.sub_rule_ids:
                for add_line in slip_line.salary_rule_id.add_rule_ids:
                    line = self.env['hr.payslip.line'].search([('slip_id', '=', self.id),
                                 ('salary_rule_id', '=', add_line.id)])
                    if line:
                        final_total += line.rate * line.amount * line.quantity / 100
                for sub_line in line.salary_rule_id.sub_rule_ids:
                    line = self.search([('slip_id', '=', self.id),
                                 ('salary_rule_id', '=', sub_line.id)])
                    if line:
                        final_total -= line.rate * line.amount * line.quantity / 100
                slip_line.amount = final_total

   
    @api.one
    def compute_sheet(self):
        if not self.line_ids:
            super(hr_payslip, self).compute_sheet()
        self.update_sheet()
        return True

class PayslipBatches(models.Model):
    _inherit = 'hr.payslip.run'
    
    #Esta variable son para cobrar el aguinaldo o el catorceavo del sueldo proporcional
    aguinaldo = fields.Boolean('Aguinaldo')
    catorceavo = fields.Boolean('Catorceavo')
    #name = fields.Char('File Name', size=256, readonly=True)
    file_data = fields.Binary('File')


    @api.multi
    def get_all_columns(self):
        result = {}
        all_col_list_seq = []
        if self.slip_ids:
            for line in self.env['hr.payslip.line'].search([('slip_id', 'in', self.slip_ids.ids)], order="sequence"):
                if line.code not in all_col_list_seq:
                    all_col_list_seq.append(line.code)
                if line.code not in result.keys():
                    result[line.code] = line.name
        return [result, all_col_list_seq]

    #Suma de las horas extras que esten validadas y que tenga como fechas la de inicio y al del fin
    @api.multi
    def duracion_fechas(self):
        mos = self.slip_ids.employee_id.date_start
        final = mos.month
        raise ValidationError(final) 

        #for netu in vaca_validacion:
        #    if netu.code == 'NET':
        #        result = super(PayslipBatches, self).write({'amount': to})
        
   #ULTIMOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOO
    @api.multi
    def get_nomi_data(self):
        file_name = _(self.name +'.xlsx')
        fp = BytesIO()

        workbook = xlsxwriter.Workbook(fp)
        heading_format = workbook.add_format({'align': 'center',
                                              'valign': 'vcenter',
                                              'bold': True, 
                                              'size': 12,
                                              'font_color': 'white',
                                              'bg_color' : 'red'
                                              })
        cell_text_format_n = workbook.add_format({'align': 'left',
                                                  'bold': True, 'size': 13,
                                                  })
        cell_text_format = workbook.add_format({'align': 'center',
                                                'bold': True, 'size': 9,
                                                })

        cell_text_format.set_border()
        cell_text_format_new = workbook.add_format({'align': 'center',
                                                    'size': 9,
                                                    })
        cell_text_format_new.set_border()
        cell_number_format = workbook.add_format({'align': 'left',
                                                  'bold': False, 'size': 9,
                                                  'num_format': 'L         #,##0.00'})
        cell_number_format.set_border()
        worksheet = workbook.add_worksheet('payroll report.xlsx')
        
        normal_num_bold = workbook.add_format({'align': 'left', 'bold': True, 'num_format': 'L         #,##0.00', 'size': 9, })
        normal_num_bold.set_border()

        worksheet.set_column('A:A', 20)
        worksheet.set_column('B:B', 20)
        worksheet.set_column('C:C', 20)
        worksheet.set_column('D:D', 20)
        worksheet.set_column('E:E', 20)
        worksheet.set_column('F:F', 20)
        worksheet.set_column('G:G', 20)
        worksheet.set_column('H:H', 20)
        worksheet.set_column('I:I', 20)
        worksheet.set_column('J:J', 20)
        worksheet.set_column('K:K', 20)
        worksheet.set_column('L:L', 20)
        worksheet.set_column('M:M', 20)
        worksheet.set_column('N:N', 20)

        #date_2 = datetime.strftime(self.date_end, '%Y-%m-%d %H:%M:%S')
        #date_1= datetime.strftime(self.from_date, '%Y-%m-%d %H:%M:%S')
        #payroll_month = self.from_date.strftime("%B")

        #worksheet.merge_range('A1:F2', 'Payroll For %s %s' % (payroll_month, self.from_date.year), heading_format)
        #INSERTAR IMAGEN DEL LOGO EN EL DOCUMENTO DE EXCEL, AMTES DE REALIZAR TIENE QUE ESTAR EL LOGO
        logo = self.env.user.company_id.logo
        buf_image= BytesIO(base64.b64decode(logo))
        x_scale = 0.43
        y_scale = 0.15
        worksheet.insert_image('A1', "any_name.png", {'image_data': buf_image, 'y_scale': y_scale, 'x_scale': x_scale, 'object_position':4})

        row = 2
        column = 0
        
        ini = str(self.date_start)
        fini = str(self.date_end)
        nombre_empre = str(self.env.user.company_id.name)
        #worksheet.merge_range('B5:D5', '%s' % (self.env.user.company_id.name), cell_text_format_n)    
        worksheet.write('E1',  'Empresa',  cell_text_format_n)
        worksheet.write('F1',  nombre_empre)
        row += 1
        worksheet.write('E2', 'Fecha Inicial',  cell_text_format_n)
        worksheet.write('F2', ini)
        row += 1
        worksheet.write('E3', 'Fecha Final', cell_text_format_n)
        worksheet.write('F3', fini)
        row += 2
        res=self.get_all_columns()
        all_col_nombre = res[0]
        all_col_codigo = res[1]

        row = 6

        worksheet.write(row, 0, 'REFERENCIA', heading_format)
        worksheet.write(row, 1, 'CODIGO', heading_format)
        worksheet.write(row, 2, 'NOMBRE COMPLETO', heading_format)
        worksheet.write(row, 3, 'CARGO QUE DESEMPEÑA', heading_format)
        worksheet.write(row, 4, 'DEPARTAMENTO', heading_format)
        worksheet.write(row, 5, 'FECHA INGRESO', heading_format)
        worksheet.write(row, 6, 'DIAS LABORADOS', heading_format)
        worksheet.write(row, 7, 'HORAS EXTRAS', heading_format)
        worksheet.write(row, 8,'SUEDO POR HORA', heading_format)
        worksheet.write(row, 9,'TOTAL HORAS', heading_format)
        worksheet.write(row, 10,'DIAS NO TRABAJADOS', heading_format)
        #worksheet.write(row, 11,'SUELDO QUINCENAL', heading_format)
       
        row_set = row
        column = 11
        #Nombre de las reglas salariales como titulo
        for vals in all_col_codigo:
            worksheet.write(row, column, all_col_nombre[vals], heading_format)
            column += 1

        row = 7

        #VARIABLES PARA LOS TOTALES
        # Dias no trabajados total
        total_diasnotrabajo = 0.0
        # Total Dinero pagado por horas extras 
        total_dinero_horas_extr = 0.0
        #Total suma de sueldos variable
        total_todod = 0.0
        #Ingresos
        total_sueldo_mensul = 0.0
        total_sueldo_quince = 0.0
        
        total_comi = 0.0
        total_boni = 0.0
        total_aguinaldo = 0.0
        total_combusti = 0.0
        total_plan_cel = 0.0
        total_otros_ingre = 0.0
        total_bono_educa = 0.0
        total_ingres = 0.0
        #DEDUCCIONES
        total_seguro = 0.0
        total_rap_sumafinal = 0.0
        total_vecinal = 0.0
        total_plan_cel_dedu = 0.0
        total_seguro_medi = 0.0
        total_otras_dedu = 0.0
        total_impuesto_renta = 0.0
        total_dedu_fin = 0.0 

        
        for slip in self.slip_ids:
            worksheet.write(row, 0, str(slip.number), cell_text_format)
            worksheet.write(row, 1, str(slip.employee_id.id), cell_text_format)
            worksheet.write(row, 2, str(slip.employee_id.name), cell_text_format)
            cargo = slip.employee_id.job_id.name or None
            worksheet.write(row, 3, str(cargo), cell_text_format)
            dept_nm = slip.employee_id.department_id and slip.employee_id.department_id.name or None
            job_nm = slip.employee_id.work_email or None
            worksheet.write(row, 4, dept_nm, cell_text_format)
          

            #Suma del total de dias * las horas de extras aprobadas
            total_horas = 0.0
            total_horas_arre = {}
            #VARIABLES DE VALIDACION DEL TOTAL DE HORAS TRABAJADAS 
            total_horas_asis = 0.0
            total_horas_asisten = {}
            #total deducciones
            total_deducciones = {}
            nombre_deducciones = {}
            #total INGRESOS
            total_ingresos = {}
            nombre_ingresos = {}
            #Agarra si el empleado es permanente o por hora
            tipo_emple = {}
            hora_4 = 4.0
            hora_5 = 5.0
            hora_6 = 6.0
            hora_8 = 8.0

            hasta = self.date_end
            desde = self.date_start
            # Calculamos la diferencia de los días
            dias_totales = (hasta - desde).days
            total_d = int(dias_totales) + 1 
            
            #CALCULO DE VACACIONES PAGADAS E INPAGADAS
            pagadas = 0.0
            inpagadas = 0.0
            total_dias_trabajados = {}
            total_dias_no_trabajo = {}
            lista = []
            tr = True
            fecha_ingreso_calculo_rap = 0

            vaca_validacion = self.env['hr.leave'].search([('employee_id.id', '=', slip.employee_id.id),('state', '=', 'validate')]) 
            for natu in vaca_validacion:
                for days in range(dias_totales + 1): 
                    fecha = desde + relativedelta(days=days)
                    if natu['request_date_from'] == fecha:
                        if natu.holiday_status_id.unpaid == tr: 
                           inpagadas += natu['number_of_days']
                        else:
                           pagadas += natu['number_of_days']
                total_dias_trabajados[slip.employee_id.id] = pagadas
                total_dias_no_trabajo[slip.employee_id.id] = inpagadas
            
            #TOTAL HORAS
            contrato_validacion = self.env['hr.contract'].search([('employee_id', '=', slip.employee_id.id), ('emple_perma', '=', tr), ('state', '=', 'open')])
            paga = total_dias_trabajados.get(slip.employee_id.id) or 0.0
            inpa = total_dias_no_trabajo.get(slip.employee_id.id) or 0.0
            #DIAS NO PAGADOS
            total_diasnotrabajo += inpa
            worksheet.write(row, 10, str(inpa), cell_text_format)
            dias_comple = (total_d - inpa)
            worksheet.write(row, 6, str(dias_comple), cell_number_format)
            
            valor_final  = 0.0               
            contrato_hora = self.env['hr.contract'].search([('employee_id.id', '=', slip.employee_id.id), ('state', '=', 'open')])
            asistencia = self.env['hr.attendance'].search([('employee_id.id', '=', slip.employee_id.id)])
            saba = ''
            sap = 'SÁBADO'
            
            #FECHA INGRESO
            ihss_mes_calcular = contrato_hora.meses_seguro
            fecha_inn = contrato_hora.fecha_ingreso
            fecha_ingreso_calculo_rap = fecha_inn
            fecha_real_in = contrato_hora.date_start
            worksheet.write(row, 5, str(fecha_real_in), cell_text_format)
            
            

            for datum in asistencia:
                mos = datum['check_in']
                hora_entrada = datetime.date(mos.year, mos.month, mos.day)
                saba = hora_entrada.strftime('%A').upper()
                for contra in contrato_hora:
                    tipo_emple[slip.employee_id.id] = contra['emple_perma']
                    if contra['hora_contractual'] == '4': 
                        for days in range(dias_totales + 1): 
                            fecha = desde + relativedelta(days=days)
                            if hora_entrada == fecha:
                                if datum['worked_hours'] >= 4:
                                        total_horas_asis += hora_4  
                                else:
                                    total_horas_asis += datum['worked_hours']
                        total = float(paga) * float(hora_4)
                        total1 = float(inpa) * float(hora_4)
                        valor_final = float(total_horas_asis) + float(total) - float(total1)
                    if contra['hora_contractual'] == '6': 
                        for days in range(dias_totales + 1): 
                            fecha = desde + relativedelta(days=days)
                            if hora_entrada == fecha:
                                if saba == sap: 
                                    if datum['worked_hours'] >= 4:
                                            total_horas_asis += hora_4  
                                    else:
                                        total_horas_asis += datum['worked_hours']
                                else: 
                                    if datum['worked_hours'] >= 5:
                                            total_horas_asis += hora_5  
                                    else:
                                        total_horas_asis += datum['worked_hours']
                        total = float(paga) * float(hora_5)
                        total1 = float(inpa) * float(hora_5)
                        valor_final = float(total_horas_asis) + float(total) - float(total1)
                    if contra['hora_contractual'] == '6': 
                        for days in range(dias_totales + 1): 
                            fecha = desde + relativedelta(days=days)
                            if hora_entrada == fecha:
                                if saba == sap: 
                                    if datum['worked_hours'] >= 4:
                                            total_horas_asis += hora_4  
                                    else:
                                        total_horas_asis += datum['worked_hours']
                                else: 
                                    if datum['worked_hours'] >= 6:
                                            total_horas_asis += hora_6  
                                    else:
                                        total_horas_asis += datum['worked_hours']
                        total = float(paga) * float(hora_6)
                        total1 = float(inpa) * float(hora_6)
                        valor_final = float(total_horas_asis) + float(total) - float(total1)
                    if contra['hora_contractual'] == '8': 
                        for days in range(dias_totales + 1): 
                            fecha = desde + relativedelta(days=days)
                            if hora_entrada == fecha:
                                if saba == sap: 
                                    if datum['worked_hours'] >= 4:
                                            total_horas_asis += hora_4  
                                    else:
                                        total_horas_asis += datum['worked_hours']
                                else: 
                                    if datum['worked_hours'] >= 8:
                                            total_horas_asis += hora_8  
                                    else:
                                        total_horas_asis += datum['worked_hours']
                        total = float(paga) * float(hora_8)
                        total1 = float(inpa) * float(hora_8)
                        valor_final = float(total_horas_asis) + float(total) - float(total1)
                    if contra['hora_contractual'] == 'Permanente': 
                        for days in range(dias_totales + 1): 
                            fecha = desde + relativedelta(days=days)
                            if hora_entrada == fecha:
                                if saba == sap: 
                                    if datum['worked_hours'] >= 4:
                                            total_horas_asis += hora_4  
                                    else:
                                        total_horas_asis += datum['worked_hours']
                                else: 
                                    if datum['worked_hours'] >= 8:
                                            total_horas_asis += hora_8  
                                    else:
                                        total_horas_asis += datum['worked_hours']
                        total = float(paga) * float(hora_8)
                        total1 = float(inpa) * float(hora_8)
                        valor_final = float(total_horas_asis) + float(total) - float(total1)
                total_horas_asisten[slip.employee_id.id] = valor_final
                
            tot_sueld = 0.0
            ace = 'aprobado'
            #Variables hora normal
            ace2 = True
            tinormal = 'horanormal'
            hora_normal = self.env['test_model_precio'].search([('horas_activo', '=', ace2),('tipo_hora', '=', tinormal)], limit=1)
            #Variable hora vacaciones
            tivacaciones = 'vacaciones'
            hora_vacacio = self.env['test_model_precio'].search([('horas_activo', '=', ace2),('tipo_hora', '=', tivacaciones)], limit=1)
            stage_asisten = self.env['test_model_name'].search([('employee_id', '=', slip.employee_id.id),('fase_horas', '=', ace)]) 
            vacio = 0.0
            for workline in slip.worked_days_line_ids:       
                if stage_asisten:
                    for datum in stage_asisten:
                        for days in range(dias_totales + 1): 
                            fecha = desde + relativedelta(days=days)
                            if datum['fecha'] == fecha: 
                               total_horas += datum['hora_extra']
                        worksheet.write(row, 7, str(total_horas), cell_number_format)
                        total_ex_tr = float(total_horas) + float(valor_final)
                        total_dinero_horas_extr += total_ex_tr
                        worksheet.write(row, 9, total_ex_tr, cell_text_format)
                            #Calculo del total de horas * precio de hora
                        if datum['horas_vaca'] == True:
                            tocon = float(total_horas) * float(hora_vacacio['hora_lps'])
                            worksheet.write(row, 8, hora_normal['hora_lps'], cell_number_format)
                            pal = float_round(tocon, precision_digits=2)                      
                            total_horas_arre[slip.employee_id.id] = pal
                        else:
                            tocon = float(total_horas) * float(hora_normal['hora_lps'])
                            worksheet.write(row, 8, hora_normal['hora_lps'], cell_number_format)                      
                            pal = float_round(tocon, precision_digits=2)
                            total_horas_arre[slip.employee_id.id] = pal   
                else:
                    worksheet.write(row, 7, str(total_horas), cell_number_format)
                    total_ex_tr = float(total_horas) + float(valor_final)
                    total_dinero_horas_extr += total_ex_tr
                    worksheet.write(row, 9, str(total_ex_tr), cell_text_format)
                    worksheet.write(row, 8, hora_normal['hora_lps'], cell_number_format)
                    #worksheet.write(row, 10, str(vacio), cell_number_format)
            if contrato_validacion:
               total_hor = total_horas_asisten.get(slip.employee_id.id)
               total_extra = total_horas_arre.get(slip.employee_id.id)
               tot_sueld = contrato_validacion.wage
               sueldo_neto = (contrato_validacion.wage/2)
               t1 = float(sueldo_neto) + float(total_extra or 0.0)
               worksheet.write(row, 11, tot_sueld, cell_number_format) 
               worksheet.write(row, 12, t1, cell_number_format) 
            else:
               total_hor = total_horas_asisten.get(slip.employee_id.id)
               total_extra = total_horas_arre.get(slip.employee_id.id)
               tot_sueld = contrato_validacion.wage
               sueldo_neto = float(total_hor) * float(hora_normal['hora_lps'])
               t1 = float(sueldo_neto) + float(total_extra or 0.0)
               worksheet.write(row, 11, tot_sueld, cell_number_format) 
               worksheet.write(row, 12, t1, cell_number_format) 
            code_col = 13

           
            
            
            #Ingresos
            
            #Día actual
            today = date.today()
            year_actual = today.year
            month_actual = today.month

            #FECHA INGRESO PARA CALCULAR EL ISR DE ACUERDO AL TIEMPO QUE ENTRO
            dia_isr = fecha_ingreso_calculo_rap.day 
            fee = fecha_ingreso_calculo_rap.month 
            year_mo = fecha_ingreso_calculo_rap.year 

            pre_ingre_dedu_total = 0.0
            sum_ingre_total = 0.0
            

            #VARIABLES PARA SACAR EL MONTO MENSUAL DEL ACUMULADO CON EL PROMEDIO DE DIAS SI ENTRA DESPUES DEL 1
            monto_anu_mensual = 0.0
            calculo_dias_trabajo = 0.0
            resta_dias = 0

            dedu_ingre_anual = self.env['model_tipo_dedu_ingre_anuales'].search([('employee_id', '=', slip.employee_id.id), ('tipo_activo', '=', True)])
            #SUMA DEL MONTO ANUAL DE INGRESOS O DEDUCCIONES EXTRAS ANUALMENTE
            for ingre_anue in dedu_ingre_anual:
                #ingre_dedu_total += ingre_anue['monto_year']
                #Mes Validacion
                if month_actual == fee and year_actual == year_mo:
                    
                    if dia_isr == 1:
                        pre_ingre_dedu_total = (ingre_anue['monto_lps'] / 2)
                    
                    else:
                            if dia_isr == 11:
                                monto_anu_mensual = (ingre_anue['monto_lps'] / 30)
                                resta_dias = 30 - (31 - dia_isr) 
                                calculo_dias_trabajo = resta_dias 
                                pre_ingre_dedu_total += (monto_anu_mensual * calculo_dias_trabajo)

                            else:
                                if dia_isr > 1 and dia_isr < 10:
                                    monto_anu_mensual = (ingre_anue['monto_lps'] / 30)
                                    resta_dias = 30 - (31 - dia_isr) 
                                    calculo_dias_trabajo = resta_dias 
                                    pre_ingre_dedu_total += (monto_anu_mensual * calculo_dias_trabajo)

                                if dia_isr > 9 and dia_isr < 31:
                                    monto_anu_mensual = (ingre_anue['monto_lps'] / 30)
                                    resta_dias = 15 - (15 - dia_isr) 
                                    calculo_dias_trabajo = resta_dias 
                                    pre_ingre_dedu_total += (monto_anu_mensual * calculo_dias_trabajo)
                else:
                    pre_ingre_dedu_total +=  (ingre_anue['monto_lps'] / 2)
                    
           
            tot_ingr = 0.0
            total_ingre = 0.0
            to_ingre1 = 0.0
            to_ingre2 = 0.0
            to_ingre3 = 0.0
            to_ingre4 = 0.0
            to_ingre5 = 0.0
            to_ingre66 = 0.0
            to_ingre77 = 0.0
            ingre_emple = self.env['test_model_ingresos'].search([('tipo_ingre_id.category_id.code', '=', 'INGRE'), ('employee_id', '=', slip.employee_id.id)])
            if ingre_emple:     
                for petu in ingre_emple:
                    for days in range(dias_totales + 1): 
                        fecha = desde + relativedelta(days=days)
                        if petu.fecha_precio == fecha:
                            total_ingre += petu['monto_lps']
                            if petu.tipo_ingre_id.code == 'COMI':
                                to_ingre1 += petu['monto_lps']
                            if petu.tipo_ingre_id.code == 'BONIFI':
                                to_ingre2 += petu['monto_lps']   
                            if petu.tipo_ingre_id.code == 'AGUIN':
                                to_ingre3 += petu['monto_lps']
                            if petu.tipo_ingre_id.code == 'DEPRECOS':
                                to_ingre4 += petu['monto_lps']   
                            if petu.tipo_ingre_id.code == 'PLANCE':
                                to_ingre5 += petu['monto_lps']
                            if petu.tipo_ingre_id.code == 'BONOEDU':
                                to_ingre66 += petu['monto_lps']
                            if petu.tipo_ingre_id.code == 'OTROINGRE':
                                to_ingre77 += petu['monto_lps']
                    worksheet.write(row, 13, to_ingre1, cell_number_format)
                    worksheet.write(row, 14, to_ingre2, cell_number_format)
                    worksheet.write(row, 15, to_ingre3, cell_number_format)
                    worksheet.write(row, 16, to_ingre4, cell_number_format)
                    worksheet.write(row, 17, to_ingre5, cell_number_format)
                    worksheet.write(row, 18, to_ingre66, cell_number_format)
                    worksheet.write(row, 19, to_ingre77, cell_number_format)
                    if contrato_validacion:
                        sueldo = (contrato_validacion.wage/2)
                        hora = total_horas_arre.get(slip.employee_id.id)
                        if hora:
                            tot_ingr = float(sueldo) + float(total_ingre) + float(hora) + float(pre_ingre_dedu_total)
                            va_in = float_round(tot_ingr, precision_digits=2)
                            worksheet.write(row, 20, va_in, cell_number_format) 
                            pal = float_round(total_ingre, precision_digits=2)
                            total_ingresos[slip.employee_id.id] = pal
                        else:
                            tot_ingr = float(sueldo) + float(total_ingre) + float(pre_ingre_dedu_total )
                            va_in = float_round(tot_ingr, precision_digits=2)
                            worksheet.write(row, 20, va_in, cell_number_format) 
                            pal = float_round(total_ingre, precision_digits=2)
                            total_ingresos[slip.employee_id.id] = pal
                    else:               
                        hora = total_horas_arre.get(slip.employee_id.id)
                        if hora:
                            tot_ingr = float(sueldo_neto) + float(total_ingre) + float(hora)  + float(pre_ingre_dedu_total )
                            va_in = float_round(tot_ingr, precision_digits=2)
                            worksheet.write(row, 20, va_in, cell_number_format) 
                            pal = float_round(total_ingre, precision_digits=2)
                            total_ingresos[slip.employee_id.id] = pal
                        else:
                            tot_ingr = float(sueldo_neto) + float(total_ingre) + float(pre_ingre_dedu_total)
                            va_in = float_round(tot_ingr, precision_digits=2)
                            worksheet.write(row, 20, va_in, cell_number_format) 
                            pal = float_round(total_ingre, precision_digits=2)
                            total_ingresos[slip.employee_id.id] = pal
            else:
                worksheet.write(row, 13, to_ingre1, cell_number_format)
                worksheet.write(row, 14, to_ingre2, cell_number_format)
                worksheet.write(row, 15, to_ingre3, cell_number_format)
                worksheet.write(row, 16, to_ingre4, cell_number_format)
                worksheet.write(row, 17, to_ingre5, cell_number_format)
                worksheet.write(row, 18, to_ingre66, cell_number_format)
                worksheet.write(row, 19, to_ingre77, cell_number_format)
                hora = total_horas_arre.get(slip.employee_id.id)    
                if hora:
                    tot_ingr = float(sueldo_neto) + float(total_ingre) + float(hora) + float(pre_ingre_dedu_total)
                    va_in = float_round(tot_ingr, precision_digits=2)
                    worksheet.write(row, 20, va_in, cell_number_format) 
                    total_ingresos[slip.employee_id.id] = 0.0
                else:
                    tot_ingr = float(sueldo_neto) + float(total_ingre) + float(pre_ingre_dedu_total)
                    va_in = float_round(tot_ingr, precision_digits=2)
                    worksheet.write(row, 20, va_in, cell_number_format) 
                    total_ingresos[slip.employee_id.id] = 0.0
            
            #EL ANUAL LO MUESTRA ACA
            #ingre_emple_revision = self.env['model_tipo_dedu_ingre_anuales'].search([('tipo_dedu_id.category_id.code', '=', 'INGRE'), ('employee_id', '=', slip.employee_id.id)])
            #TASA DOLAR
            tasa_dolar = self.env['res.currency'].search([('name', '=', 'USD')])
            
            for ingrep in dedu_ingre_anual:
                if ingrep.tipo_dedu_id.code == 'COMI' and to_ingre1 == 0.0:
                    
                    if month_actual == fee and year_actual == year_mo:
                        
                        #DOLARES VALIDACION
                        if ingrep['tipo_moneda'] == 'Dolar':
                            
                            if dia_isr == 1:
                                pre_ingre_dedu_total = ((ingrep['monto_lps'] / tasa_dolar.rate) / 2)
                            else:
                                    if dia_isr == 11:
                                        monto_anu_mensual = ((ingrep['monto_lps'] / tasa_dolar.rate) / 30)
                                        resta_dias = 30 - (31 - dia_isr) 
                                        calculo_dias_trabajo = resta_dias 
                                        pre_ingre_dedu_total = (monto_anu_mensual * calculo_dias_trabajo)

                                    else:
                                        if dia_isr > 1 and dia_isr < 10:
                                            monto_anu_mensual = ((ingrep['monto_lps'] / tasa_dolar.rate) / 30)
                                            resta_dias = 30 - (31 - dia_isr) 
                                            calculo_dias_trabajo = resta_dias 
                                            pre_ingre_dedu_total = (monto_anu_mensual * calculo_dias_trabajo)

                                        if dia_isr > 9 and dia_isr < 31:
                                            monto_anu_mensual = ((ingrep['monto_lps'] / tasa_dolar.rate) / 30)
                                            resta_dias = 15 - (15 - dia_isr) 
                                            calculo_dias_trabajo = resta_dias 
                                            pre_ingre_dedu_total = (monto_anu_mensual * calculo_dias_trabajo)

                        else:
                            if dia_isr == 1:
                                pre_ingre_dedu_total = (ingrep['monto_lps'] / 2)
                            
                            else:
                                    if dia_isr == 11:
                                        monto_anu_mensual = (ingrep['monto_lps'] / 30)
                                        resta_dias = 30 - (31 - dia_isr) 
                                        calculo_dias_trabajo = resta_dias 
                                        pre_ingre_dedu_total = (monto_anu_mensual * calculo_dias_trabajo)

                                    else:
                                        if dia_isr > 1 and dia_isr < 10:
                                            monto_anu_mensual = (ingrep['monto_lps'] / 30)
                                            resta_dias = 30 - (31 - dia_isr) 
                                            calculo_dias_trabajo = resta_dias 
                                            pre_ingre_dedu_total = (monto_anu_mensual * calculo_dias_trabajo)

                                        if dia_isr > 9 and dia_isr < 31:
                                            monto_anu_mensual = (ingrep['monto_lps'] / 30)
                                            resta_dias = 15 - (15 - dia_isr) 
                                            calculo_dias_trabajo = resta_dias 
                                            pre_ingre_dedu_total = (monto_anu_mensual * calculo_dias_trabajo)
                    else:
                        #DOLARES VALIDACION
                        if ingrep['tipo_moneda'] == 'Dolar':
                           pre_ingre_dedu_total =  ((ingrep['monto_lps'] / tasa_dolar.rate) / 2)
                        else:
                            pre_ingre_dedu_total =  (ingrep['monto_lps'] / 2)

                    worksheet.write(row, 13, pre_ingre_dedu_total, cell_number_format)
                    to_ingre1 = pre_ingre_dedu_total
                if ingrep.tipo_dedu_id.code == 'BONIFI' and to_ingre2 == 0.0:
                    
                    if month_actual == fee and year_actual == year_mo:
                        
                        #DOLARES VALIDACION
                        if ingrep['tipo_moneda'] == 'Dolar':
                            
                            if dia_isr == 1:
                                pre_ingre_dedu_total = ((ingrep['monto_lps'] / tasa_dolar.rate) / 2)
                            else:
                                    if dia_isr == 11:
                                        monto_anu_mensual = ((ingrep['monto_lps'] / tasa_dolar.rate) / 30)
                                        resta_dias = 30 - (31 - dia_isr) 
                                        calculo_dias_trabajo = resta_dias 
                                        pre_ingre_dedu_total = (monto_anu_mensual * calculo_dias_trabajo)

                                    else:
                                        if dia_isr > 1 and dia_isr < 10:
                                            monto_anu_mensual = ((ingrep['monto_lps'] / tasa_dolar.rate) / 30)
                                            resta_dias = 30 - (31 - dia_isr) 
                                            calculo_dias_trabajo = resta_dias 
                                            pre_ingre_dedu_total = (monto_anu_mensual * calculo_dias_trabajo)

                                        if dia_isr > 9 and dia_isr < 31:
                                            monto_anu_mensual = ((ingrep['monto_lps'] / tasa_dolar.rate) / 30)
                                            resta_dias = 15 - (15 - dia_isr) 
                                            calculo_dias_trabajo = resta_dias 
                                            pre_ingre_dedu_total = (monto_anu_mensual * calculo_dias_trabajo)

                        else:
                            if dia_isr == 1:
                                pre_ingre_dedu_total = (ingrep['monto_lps'] / 2)
                            
                            else:
                                    if dia_isr == 11:
                                        monto_anu_mensual = (ingrep['monto_lps'] / 30)
                                        resta_dias = 30 - (31 - dia_isr) 
                                        calculo_dias_trabajo = resta_dias 
                                        pre_ingre_dedu_total = (monto_anu_mensual * calculo_dias_trabajo)

                                    else:
                                        if dia_isr > 1 and dia_isr < 10:
                                            monto_anu_mensual = (ingrep['monto_lps'] / 30)
                                            resta_dias = 30 - (31 - dia_isr) 
                                            calculo_dias_trabajo = resta_dias 
                                            pre_ingre_dedu_total = (monto_anu_mensual * calculo_dias_trabajo)

                                        if dia_isr > 9 and dia_isr < 31:
                                            monto_anu_mensual = (ingrep['monto_lps'] / 30)
                                            resta_dias = 15 - (15 - dia_isr) 
                                            calculo_dias_trabajo = resta_dias 
                                            pre_ingre_dedu_total = (monto_anu_mensual * calculo_dias_trabajo)
                    else:
                        #DOLARES VALIDACION
                        if ingrep['tipo_moneda'] == 'Dolar':
                           pre_ingre_dedu_total =  ((ingrep['monto_lps'] / tasa_dolar.rate) / 2)
                        else:
                            pre_ingre_dedu_total =  (ingrep['monto_lps'] / 2)

                    #worksheet.write(row, 14, pre_ingre_dedu_total, cell_number_format)
                    to_ingre2 = pre_ingre_dedu_total
                if ingrep.tipo_dedu_id.code == 'AGUIN' and to_ingre3 == 0.0:
                    
                    if month_actual == fee and year_actual == year_mo:
                        
                        #DOLARES VALIDACION
                        if ingrep['tipo_moneda'] == 'Dolar':
                            
                            if dia_isr == 1:
                                pre_ingre_dedu_total = ((ingrep['monto_lps'] / tasa_dolar.rate) / 2)
                            else:
                                    if dia_isr == 11:
                                        monto_anu_mensual = ((ingrep['monto_lps'] / tasa_dolar.rate) / 30)
                                        resta_dias = 30 - (31 - dia_isr) 
                                        calculo_dias_trabajo = resta_dias 
                                        pre_ingre_dedu_total = (monto_anu_mensual * calculo_dias_trabajo)

                                    else:
                                        if dia_isr > 1 and dia_isr < 10:
                                            monto_anu_mensual = ((ingrep['monto_lps'] / tasa_dolar.rate) / 30)
                                            resta_dias = 30 - (31 - dia_isr) 
                                            calculo_dias_trabajo = resta_dias 
                                            pre_ingre_dedu_total = (monto_anu_mensual * calculo_dias_trabajo)

                                        if dia_isr > 9 and dia_isr < 31:
                                            monto_anu_mensual = ((ingrep['monto_lps'] / tasa_dolar.rate) / 30)
                                            resta_dias = 15 - (15 - dia_isr) 
                                            calculo_dias_trabajo = resta_dias 
                                            pre_ingre_dedu_total = (monto_anu_mensual * calculo_dias_trabajo)

                        else:
                            if dia_isr == 1:
                                pre_ingre_dedu_total = (ingrep['monto_lps'] / 2)
                            
                            else:
                                    if dia_isr == 11:
                                        monto_anu_mensual = (ingrep['monto_lps'] / 30)
                                        resta_dias = 30 - (31 - dia_isr) 
                                        calculo_dias_trabajo = resta_dias 
                                        pre_ingre_dedu_total = (monto_anu_mensual * calculo_dias_trabajo)

                                    else:
                                        if dia_isr > 1 and dia_isr < 10:
                                            monto_anu_mensual = (ingrep['monto_lps'] / 30)
                                            resta_dias = 30 - (31 - dia_isr) 
                                            calculo_dias_trabajo = resta_dias 
                                            pre_ingre_dedu_total = (monto_anu_mensual * calculo_dias_trabajo)

                                        if dia_isr > 9 and dia_isr < 31:
                                            monto_anu_mensual = (ingrep['monto_lps'] / 30)
                                            resta_dias = 15 - (15 - dia_isr) 
                                            calculo_dias_trabajo = resta_dias 
                                            pre_ingre_dedu_total = (monto_anu_mensual * calculo_dias_trabajo)
                    else:
                        #DOLARES VALIDACION
                        if ingrep['tipo_moneda'] == 'Dolar':
                           pre_ingre_dedu_total =  ((ingrep['monto_lps'] / tasa_dolar.rate) / 2)
                        else:
                            pre_ingre_dedu_total =  (ingrep['monto_lps'] / 2)


                    worksheet.write(row, 15, pre_ingre_dedu_total, cell_number_format)
                    to_ingre3 = pre_ingre_dedu_total
                if ingrep.tipo_dedu_id.code == 'DEPRECOS' and to_ingre4 == 0.0:
                   
                    if month_actual == fee and year_actual == year_mo:
                        
                        #DOLARES VALIDACION
                        if ingrep['tipo_moneda'] == 'Dolar':
                            
                            if dia_isr == 1:
                                pre_ingre_dedu_total = ((ingrep['monto_lps'] / tasa_dolar.rate) / 2)
                            else:
                                    if dia_isr == 11:
                                        monto_anu_mensual = ((ingrep['monto_lps'] / tasa_dolar.rate) / 30)
                                        resta_dias = 30 - (31 - dia_isr) 
                                        calculo_dias_trabajo = resta_dias 
                                        pre_ingre_dedu_total = (monto_anu_mensual * calculo_dias_trabajo)

                                    else:
                                        if dia_isr > 1 and dia_isr < 10:
                                            monto_anu_mensual = ((ingrep['monto_lps'] / tasa_dolar.rate) / 30)
                                            resta_dias = 30 - (31 - dia_isr) 
                                            calculo_dias_trabajo = resta_dias 
                                            pre_ingre_dedu_total = (monto_anu_mensual * calculo_dias_trabajo)

                                        if dia_isr > 9 and dia_isr < 31:
                                            monto_anu_mensual = ((ingrep['monto_lps'] / tasa_dolar.rate) / 30)
                                            resta_dias = 15 - (15 - dia_isr) 
                                            calculo_dias_trabajo = resta_dias 
                                            pre_ingre_dedu_total = (monto_anu_mensual * calculo_dias_trabajo)

                        else:
                            if dia_isr == 1:
                                pre_ingre_dedu_total = (ingrep['monto_lps'] / 2)
                            
                            else:
                                    if dia_isr == 11:
                                        monto_anu_mensual = (ingrep['monto_lps'] / 30)
                                        resta_dias = 30 - (31 - dia_isr) 
                                        calculo_dias_trabajo = resta_dias 
                                        pre_ingre_dedu_total = (monto_anu_mensual * calculo_dias_trabajo)

                                    else:
                                        if dia_isr > 1 and dia_isr < 10:
                                            monto_anu_mensual = (ingrep['monto_lps'] / 30)
                                            resta_dias = 30 - (31 - dia_isr) 
                                            calculo_dias_trabajo = resta_dias 
                                            pre_ingre_dedu_total = (monto_anu_mensual * calculo_dias_trabajo)

                                        if dia_isr > 9 and dia_isr < 31:
                                            monto_anu_mensual = (ingrep['monto_lps'] / 30)
                                            resta_dias = 15 - (15 - dia_isr) 
                                            calculo_dias_trabajo = resta_dias 
                                            pre_ingre_dedu_total = (monto_anu_mensual * calculo_dias_trabajo)
                    else:
                        #DOLARES VALIDACION
                        if ingrep['tipo_moneda'] == 'Dolar':
                           pre_ingre_dedu_total =  ((ingrep['monto_lps'] / tasa_dolar.rate) / 2)
                        else:
                            pre_ingre_dedu_total =  (ingrep['monto_lps'] / 2)
  
                    worksheet.write(row, 16, pre_ingre_dedu_total, cell_number_format)
                    to_ingre4 = pre_ingre_dedu_total
                if ingrep.tipo_dedu_id.code == 'PLANCE' and to_ingre5 == 0.0:
                
                    if month_actual == fee and year_actual == year_mo:
                        
                        #DOLARES VALIDACION
                        if ingrep['tipo_moneda'] == 'Dolar':
                            
                            if dia_isr == 1:
                                pre_ingre_dedu_total = ((ingrep['monto_lps'] / tasa_dolar.rate) / 2)
                            else:
                                    if dia_isr == 11:
                                        monto_anu_mensual = ((ingrep['monto_lps'] / tasa_dolar.rate) / 30)
                                        resta_dias = 30 - (31 - dia_isr) 
                                        calculo_dias_trabajo = resta_dias 
                                        pre_ingre_dedu_total = (monto_anu_mensual * calculo_dias_trabajo)

                                    else:
                                        if dia_isr > 1 and dia_isr < 10:
                                            monto_anu_mensual = ((ingrep['monto_lps'] / tasa_dolar.rate) / 30)
                                            resta_dias = 30 - (31 - dia_isr) 
                                            calculo_dias_trabajo = resta_dias 
                                            pre_ingre_dedu_total = (monto_anu_mensual * calculo_dias_trabajo)

                                        if dia_isr > 9 and dia_isr < 31:
                                            monto_anu_mensual = ((ingrep['monto_lps'] / tasa_dolar.rate) / 30)
                                            resta_dias = 15 - (15 - dia_isr) 
                                            calculo_dias_trabajo = resta_dias 
                                            pre_ingre_dedu_total = (monto_anu_mensual * calculo_dias_trabajo)

                        else:
                            if dia_isr == 1:
                                pre_ingre_dedu_total = (ingrep['monto_lps'] / 2)
                            
                            else:
                                    if dia_isr == 11:
                                        monto_anu_mensual = (ingrep['monto_lps'] / 30)
                                        resta_dias = 30 - (31 - dia_isr) 
                                        calculo_dias_trabajo = resta_dias 
                                        pre_ingre_dedu_total = (monto_anu_mensual * calculo_dias_trabajo)

                                    else:
                                        if dia_isr > 1 and dia_isr < 10:
                                            monto_anu_mensual = (ingrep['monto_lps'] / 30)
                                            resta_dias = 30 - (31 - dia_isr) 
                                            calculo_dias_trabajo = resta_dias 
                                            pre_ingre_dedu_total = (monto_anu_mensual * calculo_dias_trabajo)

                                        if dia_isr > 9 and dia_isr < 31:
                                            monto_anu_mensual = (ingrep['monto_lps'] / 30)
                                            resta_dias = 15 - (15 - dia_isr) 
                                            calculo_dias_trabajo = resta_dias 
                                            pre_ingre_dedu_total = (monto_anu_mensual * calculo_dias_trabajo)
                    else:
                        #DOLARES VALIDACION
                        if ingrep['tipo_moneda'] == 'Dolar':
                           pre_ingre_dedu_total =  ((ingrep['monto_lps'] / tasa_dolar.rate) / 2)
                        else:
                            pre_ingre_dedu_total =  (ingrep['monto_lps'] / 2)


                    worksheet.write(row, 17, pre_ingre_dedu_total, cell_number_format)
                    to_ingre5 = pre_ingre_dedu_total
                if ingrep.tipo_dedu_id.code == 'BONOEDU' and to_ingre66 == 0.0:
                    
                    if month_actual == fee and year_actual == year_mo:
                        
                        #DOLARES VALIDACION
                        if ingrep['tipo_moneda'] == 'Dolar':
                            
                            if dia_isr == 1:
                                pre_ingre_dedu_total = ((ingrep['monto_lps'] / tasa_dolar.rate) / 2)
                            else:
                                    if dia_isr == 11:
                                        monto_anu_mensual = ((ingrep['monto_lps'] / tasa_dolar.rate) / 30)
                                        resta_dias = 30 - (31 - dia_isr) 
                                        calculo_dias_trabajo = resta_dias 
                                        pre_ingre_dedu_total = (monto_anu_mensual * calculo_dias_trabajo)

                                    else:
                                        if dia_isr > 1 and dia_isr < 10:
                                            monto_anu_mensual = ((ingrep['monto_lps'] / tasa_dolar.rate) / 30)
                                            resta_dias = 30 - (31 - dia_isr) 
                                            calculo_dias_trabajo = resta_dias 
                                            pre_ingre_dedu_total = (monto_anu_mensual * calculo_dias_trabajo)

                                        if dia_isr > 9 and dia_isr < 31:
                                            monto_anu_mensual = ((ingrep['monto_lps'] / tasa_dolar.rate) / 30)
                                            resta_dias = 15 - (15 - dia_isr) 
                                            calculo_dias_trabajo = resta_dias 
                                            pre_ingre_dedu_total = (monto_anu_mensual * calculo_dias_trabajo)

                        else:
                            if dia_isr == 1:
                                pre_ingre_dedu_total = (ingrep['monto_lps'] / 2)
                            
                            else:
                                    if dia_isr == 11:
                                        monto_anu_mensual = (ingrep['monto_lps'] / 30)
                                        resta_dias = 30 - (31 - dia_isr) 
                                        calculo_dias_trabajo = resta_dias 
                                        pre_ingre_dedu_total = (monto_anu_mensual * calculo_dias_trabajo)

                                    else:
                                        if dia_isr > 1 and dia_isr < 10:
                                            monto_anu_mensual = (ingrep['monto_lps'] / 30)
                                            resta_dias = 30 - (31 - dia_isr) 
                                            calculo_dias_trabajo = resta_dias 
                                            pre_ingre_dedu_total = (monto_anu_mensual * calculo_dias_trabajo)

                                        if dia_isr > 9 and dia_isr < 31:
                                            monto_anu_mensual = (ingrep['monto_lps'] / 30)
                                            resta_dias = 15 - (15 - dia_isr) 
                                            calculo_dias_trabajo = resta_dias 
                                            pre_ingre_dedu_total = (monto_anu_mensual * calculo_dias_trabajo)
                    else:
                        #DOLARES VALIDACION
                        if ingrep['tipo_moneda'] == 'Dolar':
                           pre_ingre_dedu_total =  ((ingrep['monto_lps'] / tasa_dolar.rate) / 2)
                        else:
                            pre_ingre_dedu_total =  (ingrep['monto_lps'] / 2)


                    worksheet.write(row, 18, pre_ingre_dedu_total, cell_number_format)
                    to_ingre66 = pre_ingre_dedu_total
                if ingrep.tipo_dedu_id.code == 'OTROINGRE' and to_ingre77 == 0.0:

                    if month_actual == fee and year_actual == year_mo:
                        
                        #DOLARES VALIDACION
                        if ingrep['tipo_moneda'] == 'Dolar':
                            
                            if dia_isr == 1:
                                pre_ingre_dedu_total = ((ingrep['monto_lps'] / tasa_dolar.rate) / 2)
                            else:
                                    if dia_isr == 11:
                                        monto_anu_mensual = ((ingrep['monto_lps'] / tasa_dolar.rate) / 30)
                                        resta_dias = 30 - (31 - dia_isr) 
                                        calculo_dias_trabajo = resta_dias 
                                        pre_ingre_dedu_total = (monto_anu_mensual * calculo_dias_trabajo)

                                    else:
                                        if dia_isr > 1 and dia_isr < 10:
                                            monto_anu_mensual = ((ingrep['monto_lps'] / tasa_dolar.rate) / 30)
                                            resta_dias = 30 - (31 - dia_isr) 
                                            calculo_dias_trabajo = resta_dias 
                                            pre_ingre_dedu_total = (monto_anu_mensual * calculo_dias_trabajo)

                                        if dia_isr > 9 and dia_isr < 31:
                                            monto_anu_mensual = ((ingrep['monto_lps'] / tasa_dolar.rate) / 30)
                                            resta_dias = 15 - (15 - dia_isr) 
                                            calculo_dias_trabajo = resta_dias 
                                            pre_ingre_dedu_total = (monto_anu_mensual * calculo_dias_trabajo)

                        else:
                            if dia_isr == 1:
                                pre_ingre_dedu_total = (ingrep['monto_lps'] / 2)
                            
                            else:
                                    if dia_isr == 11:
                                        monto_anu_mensual = (ingrep['monto_lps'] / 30)
                                        resta_dias = 30 - (31 - dia_isr) 
                                        calculo_dias_trabajo = resta_dias 
                                        pre_ingre_dedu_total = (monto_anu_mensual * calculo_dias_trabajo)

                                    else:
                                        if dia_isr > 1 and dia_isr < 10:
                                            monto_anu_mensual = (ingrep['monto_lps'] / 30)
                                            resta_dias = 30 - (31 - dia_isr) 
                                            calculo_dias_trabajo = resta_dias 
                                            pre_ingre_dedu_total = (monto_anu_mensual * calculo_dias_trabajo)

                                        if dia_isr > 9 and dia_isr < 31:
                                            monto_anu_mensual = (ingrep['monto_lps'] / 30)
                                            resta_dias = 15 - (15 - dia_isr) 
                                            calculo_dias_trabajo = resta_dias 
                                            pre_ingre_dedu_total = (monto_anu_mensual * calculo_dias_trabajo)
                    else:
                        #DOLARES VALIDACION
                        if ingrep['tipo_moneda'] == 'Dolar':
                           pre_ingre_dedu_total =  ((ingrep['monto_lps'] / tasa_dolar.rate) / 2)
                        else:
                            pre_ingre_dedu_total =  (ingrep['monto_lps'] / 2)
 

                    worksheet.write(row, 19, pre_ingre_dedu_total, cell_number_format)
                    to_ingre77 = pre_ingre_dedu_total
            
            #CALCULO DEL RAP
            seguro_configu = self.env['model_configuraciones_nomina'].search([('tipo_activo', '=', True)])
            
            to_rap = (tot_sueld - seguro_configu.techo_rap)
            to_raa =  (to_rap * 0.015)
            total_rap = float_round((to_raa/2), precision_digits=2)  
            
            #ESTO ES PORQUE NO SE COBRA EL RAP
            #to_rap = 0
            #to_raa =  0 
            #total_rap = 0
            
            mes_calcular = 0 
            sueldo_isre = 0.0
            sueldo_normal_fecha = 0
            ante = 0
            dias_trabajo = 0
            plap = 0
            #SUMA TOTAL DEL ACUMULADO DEL ISR, EXCLUEYENDO EL MES EN EL QUE SE SACA LA PLANILLA YA QUE AHORA ES QUINCENAL
          
            acumul = 0.0
            acumulado_impues = self.env['hr.employee.impuesto'].search([('employee_id', '=', slip.employee_id.id)])
            for acumula in acumulado_impues:
                fe =  acumula['fecha']
                #CONDICION DE FECHA CUANDO ES EL MISMO YEAR
                if year_actual == fe.year and month_actual != fe.month:
                   acumul += acumula['monto_lps']
             

            #Validacion de que el empleado si entra en el año actual valide que agarre su fecha de ingreso y calcule
            #su ISR CON LA FEHA DE INGRESO SI EL EMPLEADO ES MAYOR A UN AÑO DE TRABAJO AGARRA 12 MESES 
            if year_actual == fecha_ingreso_calculo_rap.year:
                if fee == 1:
                    mes_calcular = 12
                    if dia_isr == 1:
                       sueldo_isre = 0.0

                    else:
                        if dia_isr == 11:
                            ante = (contrato_validacion.wage / 30)
                            plap = 30 - (31 - dia_isr) 
                            dias_trabajo = plap 
                            sueldo_isre = (ante * dias_trabajo)

                        else:
                            if dia_isr > 1 and dia_isr < 10:
                                ante = (contrato_validacion.wage / 30)
                                plap = 30 - (31 - dia_isr) 
                                dias_trabajo = plap 
                                sueldo_isre = (ante * dias_trabajo)

                            if dia_isr > 9 and dia_isr < 31:
                                ante = (contrato_validacion.wage / 30)
                                plap = 15 - (15 - dia_isr) 
                                dias_trabajo = plap 
                                sueldo_isre = (ante * dias_trabajo)

                if fee == 2:
                    #INGRESO DE ADRIAN 
                    mes_calcular = 11
                    if dia_isr == 1:
                       sueldo_isre = 0.0

                    else:
                        if dia_isr == 11:
                            ante = (contrato_validacion.wage / 30)
                            plap = 30 - (31 - dia_isr) 
                            dias_trabajo = plap 
                            sueldo_isre = (ante * dias_trabajo)

                        else:
                            if dia_isr > 1 and dia_isr < 10:
                                ante = (contrato_validacion.wage / 30)
                                plap = 30 - (31 - dia_isr) 
                                dias_trabajo = plap 
                                sueldo_isre = (ante * dias_trabajo)

                            if dia_isr > 9 and dia_isr < 31:
                                ante = (contrato_validacion.wage / 30)
                                plap = 15 - (15 - dia_isr) 
                                dias_trabajo = plap 
                                sueldo_isre = (ante * dias_trabajo)
                
                if fee == 3:
                    mes_calcular = 10
                    
                    if dia_isr == 1:
                       sueldo_isre = 0.0

                    else:
                        if dia_isr == 11:
                            ante = (contrato_validacion.wage / 30)
                            plap = 30 - (31 - dia_isr) 
                            dias_trabajo = plap 
                            sueldo_isre = (ante * dias_trabajo)

                        else:
                            if dia_isr > 1 and dia_isr < 10:
                                ante = (contrato_validacion.wage / 30)
                                plap = 30 - (31 - dia_isr) 
                                dias_trabajo = plap 
                                sueldo_isre = (ante * dias_trabajo)

                            if dia_isr > 9 and dia_isr < 31:
                                ante = (contrato_validacion.wage / 30)
                                plap = 15 - (15 - dia_isr) 
                                dias_trabajo = plap 
                                sueldo_isre = (ante * dias_trabajo)
                
                if fee == 4:
                    mes_calcular = 9
                    if dia_isr == 1:
                       sueldo_isre = 0.0

                    else:
                        if dia_isr == 11:
                            ante = (contrato_validacion.wage / 30)
                            plap = 30 - (31 - dia_isr) 
                            dias_trabajo = plap 
                            sueldo_isre = (ante * dias_trabajo)

                        else:
                            if dia_isr > 1 and dia_isr < 10:
                                ante = (contrato_validacion.wage / 30)
                                plap = 30 - (31 - dia_isr) 
                                dias_trabajo = plap 
                                sueldo_isre = (ante * dias_trabajo)

                            if dia_isr > 9 and dia_isr < 31:
                                ante = (contrato_validacion.wage / 30)
                                plap = 15 - (15 - dia_isr) 
                                dias_trabajo = plap 
                                sueldo_isre = (ante * dias_trabajo)
                if fee == 5:
                    mes_calcular = 8
                    if dia_isr == 1:
                       sueldo_isre = 0.0

                    else:
                        if dia_isr == 11:
                            ante = (contrato_validacion.wage / 30)
                            plap = 30 - (31 - dia_isr) 
                            dias_trabajo = plap 
                            sueldo_isre = (ante * dias_trabajo)

                        else:
                            if dia_isr > 1 and dia_isr < 10:
                                ante = (contrato_validacion.wage / 30)
                                plap = 30 - (31 - dia_isr) 
                                dias_trabajo = plap 
                                sueldo_isre = (ante * dias_trabajo)

                            if dia_isr > 9 and dia_isr < 31:
                                ante = (contrato_validacion.wage / 30)
                                plap = 15 - (15 - dia_isr) 
                                dias_trabajo = plap 
                                sueldo_isre = (ante * dias_trabajo)
                if fee == 6:
                    mes_calcular = 7
                
                    if dia_isr == 1:
                       sueldo_isre = 0.0

                    else:
                        if dia_isr == 11:
                            ante = (contrato_validacion.wage / 30)
                            plap = 30 - (31 - dia_isr) 
                            dias_trabajo = plap 
                            sueldo_isre = (ante * dias_trabajo)

                        else:
                            if dia_isr > 1 and dia_isr < 10:
                                ante = (contrato_validacion.wage / 30)
                                plap = 30 - (31 - dia_isr) 
                                dias_trabajo = plap 
                                sueldo_isre = (ante * dias_trabajo)

                            if dia_isr > 9 and dia_isr < 31:
                                ante = (contrato_validacion.wage / 30)
                                plap = 15 - (15 - dia_isr) 
                                dias_trabajo = plap 
                                sueldo_isre = (ante * dias_trabajo)
                        
                
                if fee == 7:
                    mes_calcular = 6
                    if dia_isr == 1:
                       sueldo_isre = 0.0

                    else:
                        if dia_isr == 11:
                            ante = (contrato_validacion.wage / 30)
                            plap = 30 - (31 - dia_isr) 
                            dias_trabajo = plap 
                            sueldo_isre = (ante * dias_trabajo)

                        else:
                            if dia_isr > 1 and dia_isr < 10:
                                ante = (contrato_validacion.wage / 30)
                                plap = 30 - (31 - dia_isr) 
                                dias_trabajo = plap 
                                sueldo_isre = (ante * dias_trabajo)

                            if dia_isr > 9 and dia_isr < 31:
                                ante = (contrato_validacion.wage / 30)
                                plap = 15 - (15 - dia_isr) 
                                dias_trabajo = plap 
                                sueldo_isre = (ante * dias_trabajo)
                
                if fee == 8:
                    mes_calcular = 5
                    if dia_isr == 1:
                       sueldo_isre = 0.0

                    else:
                        if dia_isr == 11:
                            ante = (contrato_validacion.wage / 30)
                            plap = 30 - (31 - dia_isr) 
                            dias_trabajo = plap 
                            sueldo_isre = (ante * dias_trabajo)

                        else:
                            if dia_isr > 1 and dia_isr < 10:
                                ante = (contrato_validacion.wage / 30)
                                plap = 30 - (31 - dia_isr) 
                                dias_trabajo = plap 
                                sueldo_isre = (ante * dias_trabajo)

                            if dia_isr > 9 and dia_isr < 31:
                                ante = (contrato_validacion.wage / 30)
                                plap = 15 - (15 - dia_isr) 
                                dias_trabajo = plap 
                                sueldo_isre = (ante * dias_trabajo)
                
                if fee == 9:
                    mes_calcular = 4
                    
                    if dia_isr == 1:
                       sueldo_isre = 0.0

                    else:
                        if dia_isr == 11:
                            ante = (contrato_validacion.wage / 30)
                            plap = 30 - (31 - dia_isr) 
                            dias_trabajo = plap 
                            sueldo_isre = (ante * dias_trabajo)

                        else:
                            if dia_isr > 1 and dia_isr < 10:
                                ante = (contrato_validacion.wage / 30)
                                plap = 30 - (31 - dia_isr) 
                                dias_trabajo = plap 
                                sueldo_isre = (ante * dias_trabajo)

                            if dia_isr > 9 and dia_isr < 31:
                                ante = (contrato_validacion.wage / 30)
                                plap = 15 - (15 - dia_isr) 
                                dias_trabajo = plap 
                                sueldo_isre = (ante * dias_trabajo)
                if fee == 10:
                    mes_calcular = 3
                    if dia_isr == 1:
                       sueldo_isre = 0.0

                    else:
                        if dia_isr == 11:
                            ante = (contrato_validacion.wage / 30)
                            plap = 30 - (31 - dia_isr) 
                            dias_trabajo = plap 
                            sueldo_isre = (ante * dias_trabajo)

                        else:
                            if dia_isr > 1 and dia_isr < 10:
                                ante = (contrato_validacion.wage / 30)
                                plap = 30 - (31 - dia_isr) 
                                dias_trabajo = plap 
                                sueldo_isre = (ante * dias_trabajo)

                            if dia_isr > 9 and dia_isr < 31:
                                ante = (contrato_validacion.wage / 30)
                                plap = 15 - (15 - dia_isr) 
                                dias_trabajo = plap 
                                sueldo_isre = (ante * dias_trabajo)
                if fee == 11:
                    mes_calcular = 2
                    if dia_isr == 1:
                       sueldo_isre = 0.0

                    else:
                        if dia_isr == 11:
                            ante = (contrato_validacion.wage / 30)
                            plap = 30 - (31 - dia_isr) 
                            dias_trabajo = plap 
                            sueldo_isre = (ante * dias_trabajo)

                        else:
                            if dia_isr > 1 and dia_isr < 10:
                                ante = (contrato_validacion.wage / 30)
                                plap = 30 - (31 - dia_isr) 
                                dias_trabajo = plap 
                                sueldo_isre = (ante * dias_trabajo)

                            if dia_isr > 9 and dia_isr < 31:
                                ante = (contrato_validacion.wage / 30)
                                plap = 15 - (15 - dia_isr) 
                                dias_trabajo = plap 
                                sueldo_isre = (ante * dias_trabajo)
                if fee == 12:
                    mes_calcular = 1
                    if dia_isr == 1:
                       sueldo_isre = 0.0

                    else:
                        if dia_isr == 11:
                            ante = (contrato_validacion.wage / 30)
                            plap = 30 - (31 - dia_isr) 
                            dias_trabajo = plap 
                            sueldo_isre = (ante * dias_trabajo)

                        else:
                            if dia_isr > 1 and dia_isr < 10:
                                ante = (contrato_validacion.wage / 30)
                                plap = 30 - (31 - dia_isr) 
                                dias_trabajo = plap 
                                sueldo_isre = (ante * dias_trabajo)

                            if dia_isr > 9 and dia_isr < 31:
                                ante = (contrato_validacion.wage / 30)
                                plap = 15 - (15 - dia_isr) 
                                dias_trabajo = plap 
                                sueldo_isre = (ante * dias_trabajo)
            else:
                mes_calcular = 12
                sueldo_normal_fecha = contrato_validacion.wage
            

            #Calcular los meses de la fecha actual - final de year para sacar el sueldo por esos meses restantes. 
            sueldo_restante_year = 0.0
            if month_actual == 12:
               fecha_actual_sueldoacumulado = 1 
            else:
               #Es 13 porque se le suma + 1 al year
               fecha_actual_sueldoacumulado = (13 - month_actual)

            #EL CALCULO DEL RAP ES A 3 MESES PORQUE DESDE OCTUBRE DEL 2020 SE EMPIEZA A COBRAR
            #EL OTRO AÑO 2021 CAMBIAR ESTE VALOR DE 3 POR -- fecha_actual_sueldoacumulado
            #YA QUE SE TIENE A CALCULAR A LOS 12 MESES DEL AÑO
            to_rap_anual = (to_raa * 3)

            #CALCULO DEL IHSS  479.34  / 2 ya que es quincenal
            to_ihss = seguro_configu.monto_lps
            #587.57 * 9
            to_ihss_original = (seguro_configu.monto_ISR * ihss_mes_calcular ) 

            #CALCULO DEL ISR
            #to_raa + to_ihss     
            towu = (to_ihss_original + 40000)
            tosumaa = (to_rap_anual + towu)
            #ne_prueba = to_rap_anual + to_ihss_original

            deduccion = 0.0
            total_isr_ne = 0.0
            total_isr = 0.0
            nsu = 0.0
            nop = 0.0
            

            
            #SI LA FECHA DE INGRESO ES IGUAL A 1 EL SUELDO NO CAMBIA POR ESO ES IGUAL AL SUELDO NORMAL MENSUAL DE ESA QUINCE SI NO SE APLICA LA FORMULA 
            # DE CUANTO TRABAJO Y ESE TOTAL DE ESA QUINCENA - EL SUELDO COMPLETO DEL YEAR
            ingre_total_dolar = 0.0
            ingre_dedu_total = 0.0

            #CONVERSION DEL DOLAR MALO. 
            #Obtener la tasa del dolar
            for ingre_totalp in dedu_ingre_anual:
                if ingre_totalp['tipo_moneda'] == 'Dolar':
                   ingre_total_dolar += (ingre_totalp['monto_year'] / tasa_dolar.rate) 
                else:
                   ingre_dedu_total += ingre_totalp['monto_year']


            #CALCULAR EL SUELDO CON VALIDACIONES


            guardar_sueldo = 0.0
            if sueldo_isre > 0.0 and year_actual == year_mo and month_actual == fee:
               guardar_sueldo = (contrato_validacion.wage - sueldo_isre) 
            else:
               guardar_sueldo = (contrato_validacion.wage / 2)
            

            #CREACION DEL SUELDO ACUMULADO QUINCENAL
            if self.aguinaldo == True or self.catorceavo == True:
                continue
            else:
                sueldo_acumul_creacion = self.env['hr.employee.sueldos'].search([('employee_id', '=', slip.employee_id.id),('fecha_sueldo', '=', self.date_end)])
                data_sueldo_obj = self.env['hr.employee.sueldos']   

                if len(sueldo_acumul_creacion) > 0:
                    nada = 0.0
                else:    
                    data_sueldo_obj.create({
                                    'fecha_sueldo': self.date_end,
                                    'monto_sueldo':guardar_sueldo,
                                    'employee_id': slip.employee_id.id,
                                    'aguinaldo_sueldo': False,
                                    'year_sueldo': year_actual})

            #SUELDO ACUMULADO DESDE QUE INGRESO A LABORAR
            #Agregar esto a la condicion ,('year_sueldo', '=', year_actual)
            acumulado_sueldos = self.env['hr.employee.sueldos'].search([('employee_id', '=', slip.employee_id.id),('aguinaldo_sueldo', '=', False)])
            total_sueldo_acumulado = 0.0  

            for sueldo_total in acumulado_sueldos:
                sueldo_date = sueldo_total['fecha_sueldo']
                sueldo_year = sueldo_date.year
                if sueldo_year == year_actual and sueldo_date.month != month_actual:
                   total_sueldo_acumulado += sueldo_total['monto_sueldo']

         

            #Sueldo restante de la fecha actual a fecha final del year
            sueldo_restante_year = (contrato_validacion.wage * fecha_actual_sueldoacumulado)

            #Suma total del sueldo acumulado + el sueldo restante    
            if total_sueldo_acumulado > 0:
               sueldo_final_anual = (total_sueldo_acumulado + sueldo_restante_year)
            else:
               sueldo_final_anual = (guardar_sueldo + sueldo_restante_year)
   
            nsu = sueldo_final_anual + ingre_dedu_total + ingre_total_dolar
       


            #SUMA DE COLEGIACION Y SUMA DE PENSIONES
            colegia = 0.00
            pensiones = 0.00
            suma_pen_cole = 0.00

            if contrato_validacion.cole_monto != 0.00:
               colegia = (contrato_validacion.cole_monto * contrato_validacion.meses_cole)
            if contrato_validacion.pensiones_monto != 0.00:
               pensiones = (contrato_validacion.pensiones_monto *   contrato_validacion.pensiones_cole)
            
            #Suma de colegiacion  + pensiones + RAP+ IHSS
            suma_pen_cole = (colegia + pensiones + tosumaa)
            gravable = (nsu - suma_pen_cole) 

            if gravable > 0.01 and gravable <= 165482.06: 
               total_isr_ne = 0.0 
            else: 
                    if gravable > 165482.06 and gravable <=  252330.80: 
                       deduccion = (gravable - 165482.06) * 0.15 
                    else: 
                        if gravable > 252330.80 and gravable <=  586815.84 : 
                           deduccion = (86848.74*0.15) + (gravable - 252330.80) * 0.20 
                        else: 
                            if gravable > 586815.84: 
                                deduccion = (86848.74*0.15) + (334485.04*0.20) + (gravable-586815.84) * 0.25 
                    total_isr_ne = deduccion
            
            #Impuesto Según Tarifa período 2020 (Impuesto a Retener) - TOTAL RETENIDO ACUMULADO MESES
            nop = (total_isr_ne - acumul)
            #RESULTADO DE LO DE ARRIBA / EL TOTAL DE MESES QUE HACEN FALTA
            fechaa_actual = date.today()
            meses_restantes = 0

            if fechaa_actual.month == 12:
               meses_restantes = 1
            else: 
                meses_restantes = (12 - fechaa_actual.month) + 1 
            #DVIDIR TOTAL ENTRE LOS MESES RESTANTES
            impuesto_completo_mensu = (nop / meses_restantes)
            #DIVIR QUINCENAL
            total_isr = (impuesto_completo_mensu / 2) 
            #/ mes_calcular
            #Deducciones 
            total_dedu = 0.0
            nom_dedu = ''
            #Deducciones detalladas

            #ASIGNACION DEL IHHS QUINCENAL
            #(to_ihss/2)
            #
            to_descu1 = (to_ihss/2)
            #Asignacion del calculo del RAP
            #total_rap
            to_descu2 = total_rap
            to_descu3 = 0.0
            to_descu4 = 0.0
            to_descu5 = 0.0
            to_descu6 = 0.0
            to_descu7 = 0.0
            to_descu8 = 0.0
            pal_final = 0.0
            va_dedu = 0.0
            cod_regla = self.env['hr.payslip.line'].search([('slip_id', '=', slip.id)])
            dias_aguinal_totales = 0
            total_dias_aguinal_totales = 0
            total_dias_aguinal_tota = 0
            total_sueldo_aguina_cator = 0
            sueldo_contrato_actual = float_round((contrato_validacion.wage / 30), precision_digits=2) 

            if self.aguinaldo == True or self.catorceavo == True:
                        worksheet.write(row, 13, 0.0, cell_number_format)
                        worksheet.write(row, 14, 0.0, cell_number_format)
                        worksheet.write(row, 15, 0.0, cell_number_format)
                        worksheet.write(row, 16, 0.0, cell_number_format)
                        worksheet.write(row, 17, 0.0, cell_number_format)
                        worksheet.write(row, 18, 0.0, cell_number_format)
                        worksheet.write(row, 19, 0.0, cell_number_format)
                        worksheet.write(row, 20, 0.0, cell_number_format)
                        worksheet.write(row, 21, 0.0, cell_number_format)  
                        worksheet.write(row, 22, 0.0, cell_number_format)
                        worksheet.write(row, 27, to_descu3, cell_number_format)
                        worksheet.write(row, 24, to_descu4, cell_number_format)
                        worksheet.write(row, 25, to_descu5, cell_number_format)
                        worksheet.write(row, 26, to_descu6, cell_number_format)
                        pal_final = 0.0 
                        worksheet.write(row, 23, pal_final, cell_number_format)
                        va_dedu = 0.0
                        worksheet.write(row, 28, va_dedu, cell_number_format)
                        total_deducciones[slip.employee_id.id] = va_dedu                            
                        code_col = 29
                        
                        #Calcular promedio de aguinaldo y catorceavo fechas 
                        if  month_actual == 12:
                            #Suma total del acumulado hasta noviembre + un sueldo segun contrato que es diciembre
                            total_suel_aguinaldo = total_sueldo_acumulado + contrato_validacion.wage
                            total_dias_aguinal_tota =  (total_suel_aguinaldo / 12)
                            va_in = total_dias_aguinal_tota

                            sueldo_acumul_creacion = self.env['hr.employee.sueldos'].search([('employee_id', '=', slip.employee_id.id)])
                            data_sueldo_obj = self.env['hr.employee.sueldos']   

                            if len(sueldo_acumul_creacion) > 0:
                                nada = 0.0
                            else:    
                                data_sueldo_obj.create({
                                                'fecha_sueldo': self.date_end,
                                                'monto_sueldo':guardar_sueldo,
                                                'employee_id': slip.employee_id.id,
                                                'aguinaldo_sueldo': True,
                                                'year_sueldo': year_actual})
                            worksheet.write(row, 15, total_dias_aguinal_tota, cell_number_format)
                        if  month_actual == 5:
                            continue
            else:
                dedu_emple = self.env['test_model_deducciones'].search([('tipo_dedu_id.category_id.code', '=', 'DED'), ('employee_id', '=', slip.employee_id.id)])
                if dedu_emple:    
                    for natu in dedu_emple:
                        for days in range(dias_totales + 1): 
                            fecha = desde + relativedelta(days=days)
                            if natu['fecha_precio'] == fecha:
                                total_dedu += natu['monto_lps']   
                                if natu.tipo_dedu_id.code == 'IMPVECI':
                                    to_descu3 += natu['monto_lps']
                                if natu.tipo_dedu_id.code == 'BONOEDU_DED':
                                    to_descu4 += natu['monto_lps']   
                                if natu.tipo_dedu_id.code == 'SEGUMEDI':
                                    to_descu5 += natu['monto_lps']
                                if natu.tipo_dedu_id.code == 'OTRA_DEDU':
                                    to_descu6 += natu['monto_lps']
                                #if natu.tipo_dedu_id.code == 'EQUIMO':
                                #    to_descu7 += natu['monto_lps'] 
                                #if natu.tipo_dedu_id.code == 'OTRA_DEDU':
                                #    to_descu8 += natu['monto_lps']
                        worksheet.write(row, 21, to_descu1, cell_number_format)  
                        worksheet.write(row, 22, to_descu2, cell_number_format)
                        worksheet.write(row, 27, to_descu3, cell_number_format)
                        worksheet.write(row, 24, to_descu4, cell_number_format)
                        worksheet.write(row, 25, to_descu5, cell_number_format)
                        worksheet.write(row, 26, to_descu6, cell_number_format)
                        #worksheet.write(row, 24, to_descu7, cell_number_format)
                        #worksheet.write(row, 25, to_descu8, cell_number_format)
                        pal_final = float_round(total_isr, precision_digits=2) 
                        worksheet.write(row, 23, pal_final, cell_number_format)
                        
                        suma_de = float(total_dedu) + float(pal_final) + float(to_descu1 + to_descu2)
                        va_dedu = float_round(suma_de, precision_digits=2)
                        worksheet.write(row, 28, va_dedu, cell_number_format)
                        total_deducciones[slip.employee_id.id] = va_dedu                            
                        code_col = 29
                else:
                    worksheet.write(row, 21, to_descu1, cell_number_format)  
                    worksheet.write(row, 22, to_descu2, cell_number_format)
                    worksheet.write(row, 27, to_descu3, cell_number_format)
                    worksheet.write(row, 24, to_descu4, cell_number_format)
                    worksheet.write(row, 25, to_descu5, cell_number_format)
                    worksheet.write(row, 26, to_descu6, cell_number_format)
                    #worksheet.write(row, 24, to_descu7, cell_number_format)
                    #worksheet.write(row, 25, to_descu8, cell_number_format)
                    pal_final = float_round(total_isr, precision_digits=2) 
                    worksheet.write(row, 23, pal_final, cell_number_format)
                    
                    suma_de = float(total_dedu) + float(pal_final) + float(to_descu1 + to_descu2 )
                    va_dedu = float_round(suma_de, precision_digits=2)
                    worksheet.write(row, 28, va_dedu, cell_number_format)
                    total_deducciones[slip.employee_id.id] = va_dedu                            
                    code_col = 29

            #VALIDACION DE VACACIONES
                
            
            #Modificar esta informacion luego es sumar las horas extras al total NET
            #total = 0.0
            va = 0.0
            to_to = 0.0
            for code in all_col_codigo:
                per = slip.get_amount_from_rule_code(code)[0]
                amt = (per/2)
                #Total_Ingreso
                total = va_in
                #TOtal Deduccion
                total_deduccion = va_dedu

                perma = False
                if  code == 'NET':
                                    #ENTRA SI EL EMPLEADO TIENE HORAS EXTRAS
                            if total_horas_arre.get(slip.employee_id.id) != None:
                                        #Si empleado no es permanente entra
                                    if  tipo_emple.get(slip.employee_id.id) == perma:
                                        hora = total_horas_arre.get(slip.employee_id.id) 
                                        total = float(sueldo_neto) + float(hora) 
                                              #ENTRA SI TIENE MONTO EN DEDUCCIONES
                                        if total_deducciones.get(slip.employee_id.id) != None:
                                            monto_deducci = total_deducciones.get(slip.employee_id.id)
                                             #ENTRA SI TIENE INGRESOS
                                            if total_ingresos.get(slip.employee_id.id) != None:
                                               monto_ingre = total_ingresos.get(slip.employee_id.id)
                                               to_to = float(total) + float(monto_ingre) - float(monto_deducci) 
                                               va = float_round(to_to, precision_digits=2)
                                               worksheet.write(row, code_col, va, cell_number_format)
                                               code_col += 1
                                               #ENTRA SI NO TIENE INGRESOS
                                            else:
                                               to_to = float(total) - float(monto_deducci) 
                                               va = float_round(to_to, precision_digits=2)
                                               worksheet.write(row, code_col, va, cell_number_format)
                                               code_col += 1
                                              #ENTRA SI NO TIENE DEDUCCIONES
                                        else:
                                            if total_ingresos.get(slip.employee_id.id) != None:
                                               monto_ingre = total_ingresos.get(slip.employee_id.id)
                                               to_to = float(total) + float(monto_ingre)
                                               va = float_round(to_to, precision_digits=2)
                                               worksheet.write(row, code_col, va, cell_number_format)
                                               code_col += 1
                                            else:
                                                va = float_round(total, precision_digits=2)
                                                worksheet.write(row, code_col, va, cell_number_format)
                                                code_col += 1
                                                #ENTRA SI EL EMPLEADO  ES PERMANENTE
                                    else:
                                        hora = total_horas_arre.get(slip.employee_id.id) 
                                        total = float(amt) + float(hora)
                                                #ENTRA SI TIENE DEDUCCIONES
                                        if total_deducciones.get(slip.employee_id.id) != None:
                                            monto_deducci = total_deducciones.get(slip.employee_id.id)
                                                #ENTRA SI TIENE INGRESOS
                                            if total_ingresos.get(slip.employee_id.id) != None:
                                              monto_ingre = total_ingresos.get(slip.employee_id.id)
                                              to_to = float(total) + float(monto_ingre) - float(monto_deducci) 
                                              va = float_round(to_to, precision_digits=2)
                                              worksheet.write(row, code_col, va, cell_number_format)
                                              code_col += 1
                                              #ENTRA SI NO TIENE INGRESOS
                                            else:
                                                to_to = float(total) - float(monto_deducci) 
                                                va = float_round(to_to, precision_digits=2)
                                                worksheet.write(row, code_col, va, cell_number_format)
                                                code_col += 1
                                        else:
                                                #ENTRA SI TIENE INGRESOS
                                            if total_ingresos.get(slip.employee_id.id) != None:
                                               monto_ingre = total_ingresos.get(slip.employee_id.id)
                                               to_to = float(total) + float(monto_ingre)
                                               va = float_round(to_to, precision_digits=2)
                                               worksheet.write(row, code_col, va, cell_number_format)
                                               code_col += 1
                                               #ENTRA SI NO TIENE INGRESOS
                                            else:
                                               va = float_round(total, precision_digits=2)
                                               worksheet.write(row, code_col, va, cell_number_format)
                                               code_col += 1
                                #ENTRA SI EL EMPLEADO NO TIENE HORAS EXTRAS
                            else:
                                #ENTRA SI EL EMPLEADO NO ES PERMANENTE
                                if tipo_emple.get(slip.employee_id.id) == perma:
                                        to_to = float(total) - float(total_deduccion)
                                        va = float_round(to_to, precision_digits=2)
                                        worksheet.write(row, code_col, va, cell_number_format)
                                        code_col += 1
                                else:
                                        to_to = float(total) - float(total_deduccion)
                                        va = float_round(to_to, precision_digits=2)
                                        worksheet.write(row, code_col, va, cell_number_format)
                                        code_col += 1
                                
            
            row += 1

            #CAMBIO EN EL DETALLE DE NOMINA INDIVIDUAL
            dedu_det = total_deducciones.get(slip.employee_id.id)
            #ingre_det = total_ingresos.get(slip.employee_id.id)
            record_ids = self.env['hr.payslip.line'].search([('slip_id', 'in', self.slip_ids.ids),('employee_id.id', '=', slip.employee_id.id) ]) 
            
            if self.aguinaldo == True or self.catorceavo == True:
               total_comi = 0.0
               total_boni = 0.0
               total_aguinaldo = 0.0
               total_combusti = 0.0
               total_plan_cel = 0.0
               total_bono_educa = 0.0
               total_otros_ingre = 0.0
               total_ingres = 0.0
               total_seguro = 0.0
               total_rap_sumafinal = 0.0
               total_vecinal = 0.0
               total_plan_cel_dedu = 0.0
               total_seguro_medi = 0.0
               total_otras_dedu = 0.0
               total_impuesto_renta = 0.0
               total_dedu_fin = 0.0
               
            total_todod += va
            for record in record_ids:
                #INGRESOS
                if record.code == 'SM':
                    total_sueldo_mensul += tot_sueld
                    record.write({
                        'amount': tot_sueld
                    })
                if record.code == 'SQ':
                    total_sueldo_quince += t1
                    record.write({
                        'amount': t1
                    })

                if record.code == 'COMI':
                    total_comi += to_ingre1
                    record.write({
                        'amount': to_ingre1
                    })
                if record.code == 'BONIFI':
                    total_boni += to_ingre2
                    record.write({
                        'amount': to_ingre2
                    })
                if record.code == 'AGUIN':
                    total_aguinaldo += to_ingre3
                    record.write({
                        'amount': to_ingre3
                    })
                if record.code == 'DEPRECOS':
                    total_combusti += to_ingre4
                    record.write({
                        'amount': to_ingre4
                    })
                if record.code == 'PLANCE':
                    total_plan_cel += to_ingre5
                    record.write({
                        'amount': to_ingre5
                    })
                if record.code == 'BONOEDU':
                    total_bono_educa += to_ingre66
                    record.write({
                        'amount': to_ingre66
                    })
                if record.code == 'OTROINGRE':
                    total_otros_ingre += to_ingre77
                    record.write({
                        'amount': to_ingre77
                    })
                if record.code == 'TOTAL_INGRE':
                    total_ingres += tot_ingr
                    record.write({
                        'amount': tot_ingr
                    })
       

                #DEDUCCIONES
                if record.code == 'IHSS':
                    total_seguro += to_descu1
                    record.write({
                        'amount': to_descu1
                    })
                if record.code == 'RAP':
                    total_rap_sumafinal += to_descu2
                    record.write({
                        'amount': to_descu2
                    })
                if record.code == 'IMPVECI':
                    total_vecinal += to_descu3
                    record.write({
                        'amount': to_descu3
                    })
                if record.code == 'BONOEDU_DED':
                    total_plan_cel_dedu += to_descu4
                    record.write({
                        'amount': to_descu4
                    })
                if record.code == 'SEGUMEDI':
                    total_seguro_medi += to_descu5
                    record.write({
                        'amount': to_descu5
                    })
                if record.code == 'OTRA_DEDU':
                    total_otras_dedu += to_descu6
                    record.write({
                        'amount': to_descu6
                    })
                if record.code == 'ISR':
                    total_impuesto_renta += pal_final
                    record.write({
                        'amount': pal_final
                    })
                if record.code == 'TOTAL_DEDU':
                    total_dedu_fin += va_dedu 
                    record.write({
                        'amount': va_dedu
                    })
                #SUELDO NETO
                if record.code == 'NET':
                    record.write({
                        'amount': va
                    })
            
            #CREACION DEL ISR QUINCENAL
            if self.aguinaldo == True or self.catorceavo == True:
                continue
            else:
                acumulado_creacion = self.env['hr.employee.impuesto'].search([('employee_id', '=', slip.employee_id.id),('fecha', '=', self.date_end)])
                data_obj = self.env['hr.employee.impuesto']   

                if len(acumulado_creacion) > 0:
                    nada = 0.0
                else:    
                    data_obj.create({
                                    'fecha': self.date_end,
                                    'monto_lps':pal_final,
                                    'employee_id': slip.employee_id.id})
           
            #Total de todo
            code_col = code_col - 20 
            worksheet.write(row, code_col, 'TOTAL', cell_text_format_n)
            #Total sueldo mensual 
            code_col = code_col + 1 
            worksheet.write(row, code_col, total_sueldo_mensul, normal_num_bold)
            #TOTAL-SUELDO-QUINCENAL
            code_col = code_col + 1 
            worksheet.write(row, code_col, total_sueldo_quince, normal_num_bold)
            #INGRESOS
            code_col = code_col + 1
            worksheet.write(row, code_col, total_comi, normal_num_bold)
            code_col = code_col + 1
            worksheet.write(row, code_col, total_boni, normal_num_bold)
            code_col = code_col + 1
            worksheet.write(row, code_col, total_aguinaldo, normal_num_bold)
            code_col = code_col + 1
            worksheet.write(row, code_col, total_combusti, normal_num_bold)
            code_col = code_col + 1
            worksheet.write(row, code_col, total_plan_cel, normal_num_bold)
            code_col = code_col + 1
            worksheet.write(row, code_col, total_bono_educa, normal_num_bold)
            code_col = code_col + 1
            worksheet.write(row, code_col, total_otros_ingre, normal_num_bold)
            code_col = code_col + 1
            worksheet.write(row, code_col, total_ingres, normal_num_bold)
            #DEDUCCIONES
            code_col = code_col + 1
            worksheet.write(row, code_col, total_seguro, normal_num_bold)
            code_col = code_col + 1
            worksheet.write(row, code_col, total_rap_sumafinal, normal_num_bold)
            code_col = code_col + 1
            worksheet.write(row, code_col, total_impuesto_renta, normal_num_bold)
            code_col = code_col + 1
            worksheet.write(row, code_col, total_plan_cel_dedu, normal_num_bold)
            code_col = code_col + 1
            worksheet.write(row, code_col, total_seguro_medi, normal_num_bold)
            code_col = code_col + 1
            worksheet.write(row, code_col, total_otras_dedu, normal_num_bold)
            code_col = code_col + 1
            worksheet.write(row, code_col, total_vecinal, normal_num_bold)
            code_col = code_col + 1
            worksheet.write(row, code_col, total_dedu_fin, normal_num_bold)
            #TOTAL SUELDO FINAL NETO
            code_col = code_col + 1
            worksheet.write(row, code_col, total_todod, normal_num_bold)

        #worksheet.write(row, 2, '', cell_number_format)

        workbook.close()
        file_download = base64.b64encode(fp.getvalue())
        fp.close()
        self = self.with_context(default_name=file_name, default_file_download=file_download)

        return {
            'name': 'Nomina Descarga',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'payroll.report.excel',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': self._context,
        }

   