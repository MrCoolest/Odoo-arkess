from odoo import  models, fields, api, _
import pytz
from datetime import datetime


class HospitalAppointment(models.Model):
    _name = "hospital.appointment"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Appointment Record"
    _order = 'id desc'

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('hospital.appointment.sequence') or _('New')
        result = super(HospitalAppointment, self).create(vals)
        return result

    @api.multi
    def write(self, vals):
        res = super(HospitalAppointment, self).write(vals)
        print("Test write Function")
        return res

    def delete_line(self):
        for rec in self:
            user_tz = pytz.timezone(self.env.context.get('tz') or self.env.user.tz)
            date_time = datetime.strptime(rec.appointment_datetime, '%Y-%m-%d %I:%M:%S')
            print(date_time)
            time_in_timezone = pytz.utc.localize(date_time).astimezone(user_tz)
            print("Time in UTC -->", rec.appointment_datetime)
            print(f'My Time : {user_tz}')
            print("Time in Users Timezone -->", time_in_timezone)
            rec.appointment_lines = [(5,0,0)]

    def _get_default_note(self):
        return 'Visite For Tests!'

    def action_confirm(self):
        for rec in self:
            active_patient = self.env['hospital.patient'].search_count([])
            all_patinet = self.env['hospital.patient'].with_context(active_text=False).search_count([])

            print(active_patient)
            print(all_patinet)

            # patients = self.env['hospital.patient'].search([])
            # print(patients)
            # femail_patient = self.env['hospital.patient'].search([('gender','=','fe_male')])
            # print(femail_patient)
            # mail_patient = self.env['hospital.patient'].search([('gender','=','male')])
            # print(mail_patient)
            #
            # # In this Search Working With on and Condition
            # femail_patient_age_10 = self.env['hospital.patient'].search([('gender', '=', 'fe_male'),('patient_age','>=',10)])
            # print(femail_patient_age_10)
            #
            # # Search With OR Conditons
            # femail_patient_or_cond = self.env['hospital.patient'].search(
            #     ['|',('gender', '=', 'fe_male'), ('patient_age', '>=', 10)])
            # print(femail_patient_or_cond)
            #
            # # odoo_search_count
            # patients_count = self.env['hospital.patient'].search_count([])
            # print(patients_count)
            #
            # fe_patients_count = self.env['hospital.patient'].search_count([('gender', '=', 'fe_male')])
            # print(fe_patients_count)
            #
            # # Ref in Odoo
            #
            # om_patient = self.env.ref('om_hospital.patient_xyz')
            # print(om_patient)
            # print(om_patient.id)
            #
            # # browse Method
            # browse_res = self.env['hospital.patient'].browse(3)
            # print(browse_res)
            #
            # if browse_res.exists():
            #     print("Existing")

            vals = {
                'patient_name' : 'Odoo',
                'patient_age' : 30
            }

            # create_record = self.env['hospital.patient'].create(vals)
            # print(create_record, create_record.id)
            #
            # browse_to_update = self.env["hospital.patient"].browse(25)
            # if browse_to_update.exists():
            #     browse_to_update.write(vals)
            #     print("Working")

            record_to_copy = self.env["hospital.patient"].browse(25)
            # record_to_copy.copy()

            record_to_copy = self.env["hospital.patient"].browse(25)
            # record_to_copy.unlink()



            # rec.state = 'confirm'
            # return {
            #     "effect" : {
            #         "fadeout" : 'slow',
            #         "message" : "Appointment confirmed",
            #         "type" : "rainbow_man",
            #     }
            # }

    def action_done(self):
        for rec in self:
            rec.state = 'done'

    def notify_user(self):
        for rec in self:
            rec.doctor_id.user_id.notify_warning("appointment")

    def test_recordset(self):
        for rec in self:
            print("Hello World!")
            partners = self.env['res.partner'].search([])
            print(partners)
            print(type(partners))
            print(list(partners))
            # print(partners.mapped('email'))
            # print(partners.mapped('create_date'))
            # print(partners.sorted(lambda a: a.write_date, reverse=True))
            # print(partners.filtered(lambda a: a.customer))
            # print(partners.filtered(lambda a: a.email))

    @api.model
    def default_get(self, fields):
        res = super(HospitalAppointment, self).default_get(fields)
        print("test......")
        appointment_lines = [(5,0,0)]
        product_rec = self.env['product.product'].search([])
        print(product_rec)
        for pro in product_rec:
            line =(0,0,{
                'product_id' : pro.id,
                'product_qty' : pro.list_price
            })
            appointment_lines.append(line)
        res.update({
            'appointment_lines' : appointment_lines,
            # 'patient_id' : 14,
            'notes' : 'Work Done Good'
        })
        # res['patient_id'] = 13
        # res['notes'] = "Hello World!"
        return res


    @api.onchange('partner_id')
    def onchange_partner_id(self):
        for rec in self:
            return {'domain': {'order_id': [('partner_id', '=', rec.partner_id.id)]}}


    patient_id = fields.Many2one('hospital.patient', string='Patient')
    doctor_id = fields.Many2one('hospital.doctor', string='Doctor')
    doctor_ids = fields.Many2many('hospital.doctor','hospital_patient_rel','appointment_id','doctor_id_rec', string='Doctorsn ')
    patient_age = fields.Integer('Age', related ="patient_id.patient_age")
    notes = fields.Text(string='Appointment Notes', default=_get_default_note)
    appointment_date = fields.Date(string="Date" , required=True)
    appointment_date_end = fields.Date(string="End Date")
    appointment_datetime = fields.Datetime(string='Date Time')
    name = fields.Char(string="Appointment id", required=True, copy=False,
                                readonly= True, index= True, default = lambda self : _('New'))
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirm', 'Confirm'),
        ('done', 'Done'),
        ('cancel', 'Cancelled'),
    ],string="Status", readonly=True, default="draft")
    doctor_note = fields.Text(string="Doctor Note")
    pharmacy_note = fields.Text(string="Pharmacy Note")
    amount = fields.Float(string="Total Amount")
    appointment_lines = fields.One2many('hospital.appointment.lines', 'appointment_id',  string="Appointment lines")
    partner_id = fields.Many2one('res.partner', string='Customer')
    order_id = fields.Many2one('sale.order', string='Sale Order')
    product_id = fields.Many2one('product.template', 'Product Template')

    @api.onchange('product_id')
    def onchange_product_id(self):
        for rec in self:
            lines = [[5,0,0]]
            # lines = []
            for line in self.product_id.product_variant_ids:
                vals = {
                    'product_id' : line.id,
                    'product_qty' : 5
                }
                lines.append((0,0,vals))
            rec.appointment_lines = lines


class HospitalAppointmentLines(models.Model):
    _name = "hospital.appointment.lines"
    _description = "Appointment lines"

    product_id = fields.Many2one("product.product", string="Medicine",domain="['|',('type','=','service'),('type', '=','product')]")
    product_qty = fields.Integer(string="Quantity")
    sequence = fields.Integer(string="Sequence")
    appointment_id = fields.Many2one('hospital.appointment', string='Appointment_id')

