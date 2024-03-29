from odoo import  models, fields, api, _
# from . import patient


class HospitalDoctor(models.Model):
    _name = "hospital.doctor"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _inherits = {'hospital.patient' : 'related_patient_id'}
    _description = "Doctors"

    name = fields.Char(string="Name", required=True)
    gender = fields.Selection([
        ('male', 'Male'),
        ('fe_male', 'Female'),
    ], default='male', string="Gender")
    user_id = fields.Many2one('res.users', string='Related User')
    patient_id = fields.Many2one('hospital.patient', string='Related Patient')
    related_patient_id = fields.Many2one('hospital.patient', string='Related Patient ID')
    appointment_ids = fields.Many2many('hospital.appointment','hospital_patient_rel','doctor_id_rec','appointment_id', string='Appointment ids')
