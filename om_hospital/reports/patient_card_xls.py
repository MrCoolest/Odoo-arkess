from odoo import models

class PartnerXlsx(models.AbstractModel):
    _name = 'report.om_hospital.report_patient_xls'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, lines):

        formate_1 = workbook.add_format({'font_size' : 14, 'align' : 'vcenter', 'bold': True})
        formate_2 = workbook.add_format({'font_size' : 10, 'align' : 'vcenter'})
        sheet = workbook.add_worksheet("Patient Card")
        sheet.right_to_left()
        sheet.set_column(3,3,50)
        sheet.write(2, 2, 'Name', formate_1)
        sheet.write(2, 3, lines.patient_name, formate_2)
        sheet.write(3, 2, 'Age', formate_1)
        sheet.write(3, 3, lines.patient_age, formate_2)
