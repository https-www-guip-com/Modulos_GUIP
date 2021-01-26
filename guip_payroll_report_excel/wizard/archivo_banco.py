
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

class payroll_report_excel_banco(models.TransientModel):
    _name = 'payroll.report.excel.banco'

    name = fields.Char('File Name', size=256, readonly=True)
    file_download = fields.Binary('Download payroll', readonly=True)


class hr_payslip(models.Model):
    _inherit = 'hr.payslip'

    @api.one
    def get_amount_from_rule_code_banco(self, rule_code):
        line = self.env['hr.payslip.line'].search([('slip_id', '=', self.id), ('code', '=', rule_code)])
        if line:
            return round(line.total, 2)
        else:
            return 0.0

    @api.one
    def update_sheet_banco(self):
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
    def compute_sheet_banco(self):
        if not self.line_ids:
            super(hr_payslip, self).compute_sheet_banco()
        self.update_sheet_banco()
        return True

class PayslipBatchesBanco(models.Model):
    _inherit = 'hr.payslip.run'

    #name = fields.Char('File Name', size=256, readonly=True)
    file_data_banco = fields.Binary('File')


    @api.multi
    def get_all_columns_banco(self):
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
    def duracion_fechas_banco(self):
        mos = self.slip_ids.employee_id.date_start
        final = mos.month
        raise ValidationError(final) 

        #for netu in vaca_validacion:
        #    if netu.code == 'NET':
        #        result = super(PayslipBatches, self).write({'amount': to})
        
   #ULTIMOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOO
    @api.multi
    def get_nomi_data_banco(self):
        file_name = _(self.name + '-Banco' +'.xlsx')
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
        cell_number_format = workbook.add_format({'align': 'center',
                                                  'bold': False, 'size': 9,
                                                  'num_format': 'L         #,##0.00'})
        cell_number_format.set_border()
        worksheet = workbook.add_worksheet('payroll report.xlsx')
        normal_num_bold = workbook.add_format({'bold': True, 'num_format': '#,###0.00', 'size': 9, })
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
        res=self.get_all_columns_banco()
        all_col_nombre = res[0]
        all_col_codigo = res[1]

        row = 6

        worksheet.write(row, 0, 'Código Beneficiario', heading_format)
        worksheet.write(row, 1, 'Cód. Banco', heading_format)
        worksheet.write(row, 2, 'Cód. de Servicio', heading_format)
        worksheet.write(row, 3, 'Pago Neto', heading_format)
        worksheet.write(row, 4, 'Descripción del Pago', heading_format)
   
        row_set = row
        column = 5
        #Nombre de las reglas salariales como titulo
        row = 7
        for slip in self.slip_ids:
            worksheet.write(row, 0, str(slip.employee_id.identification_id), cell_text_format)
            worksheet.write(row, 1, int(1), cell_text_format)
            worksheet.write(row, 2, int(1), cell_text_format)
            cargo = slip.employee_id.job_id.name or None
            dept_nm = 'Pago planilla moneda en Lempiras'
            worksheet.write(row, 4, dept_nm, cell_text_format)
            sueldo_toral = 0.0
            recorrer_sueldo = self.env['hr.payslip'].search([('number', '=', slip.number)])
            for papo in recorrer_sueldo.line_ids:
                if papo.code == 'NET':
                   sueldo_toral = papo.total
                   worksheet.write(row, 3, sueldo_toral, cell_text_format)
                   row += 1    
   
        workbook.close()
        file_download = base64.b64encode(fp.getvalue())
        fp.close()
        self = self.with_context(default_name=file_name, default_file_download=file_download)

        return {
            'name': 'Archivo Banco',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'payroll.report.excel.banco',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': self._context,
        }

           