from odoo import  models, fields, api, _
from odoo.exceptions import ValidationError


class ResPartner(models.Model):
    _inherit = 'res.partner'

    # @api.model
    # def create(self, vals_list):
    #     res = super(ResPartner, self).create(vals_list)
    #     #This is Hpw we can do the Custome Coding
    #     print("its Working")
    #     return res

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.multi
    def action_confirm(self):
        print("Over riding the sale Fucntion")
        res = super(SaleOrder, self).action_confirm()
        return res

    patient_name = fields.Char(string='Patient Name')
    is_patient = fields.Boolean(string='Is Patient')

class ResPartner(models.Model):
    _inherit = 'res.partner'

    company_type = fields.Selection(selection_add=[('om', 'Odoo Mates'), ('odoodev', 'Odoo Dev')])


class HospitalPatients(models.Model):
    _name = "hospital.patient"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Patient Record"
    _rec_name = "patient_name"


    @api.constrains('patient_age')
    def check_age(self):
        for res in self:
            if res.patient_age <= 5:
                raise ValidationError('The Age Greater Than 5')


    @api.depends('patient_age')
    def set_age_group(self):
        for rec in self:
            if rec.patient_age:
                if rec.patient_age < 18:
                    rec.age_group = 'minor'
                else:
                    rec.age_group = 'major'

    @api.multi
    def open_patient_appointment(self):
        # print("Hello World!")
        return  {
            'name' : _('Appointment'),
            'domain' : [('patient_id','=', self.id)],
            'view_type' :'form',
            'view_id' : False,
            'view_mode' : 'tree,form',
            'res_model' : 'hospital.appointment',
            'type' : 'ir.actions.act_window',
        }

    @api.multi
    def patient_report(self):
        return self.env.ref('om_hospital.report_patient_card').report_action(self)

    @api.multi
    def patient_report_excel(self):
        return self.env.ref('om_hospital.report_patient_card_xlsx').report_action(self)


    def count_patient_appointments(self):
        count = self.env['hospital.appointment'].search_count([('patient_id','=', self.id)])
        self.appointment_count = count

    def action_patients(self):
        print("Testing that function is running from menuItem or not")
        return {
            'name': _('Hospital Server Action'),
            'domain': [],
            'view_type': 'form',
            'view_id': False,
            'view_mode': 'tree,form',
            'res_model': 'hospital.patient',
            'type': 'ir.actions.act_window',
        }



    @api.onchange('doctor_id')
    def set_doctor_gender(self):
        for rec in self:
            if rec.doctor_id:
                rec.doctor_gender = rec.doctor_id.gender

    @api.multi
    def name_get(self):
        res= []
        for rec in self:
            # res.append((rec.id, '%s - %s' % (rec.patient_name, rec.name_sequence)))
            res.append((rec.id, f'{rec.patient_name} - {rec.name_sequence}'))
        return res


    @api.model
    def _name_search(self, name="", args=None, operator='ilike', limit=100):
        if args is None:
            args=[]
        domain = args + ['|',('name_sequence', operator, name), ('patient_name', operator, name)]
        return super(HospitalPatients, self).search(domain, limit=limit).name_get()

    def action_send_card(self):
        print("Sned You The Email")
        template_id = self.env.ref('om_hospital.patient_card_email_template').id
        template = self.env['mail.template'].browse(template_id)
        template.send_mail(self.id, force_send=True)

    @api.depends('patient_name')
    def _compute_upper_name(self):
        for rec in self:
            rec.patient_name_upper = rec.patient_name.upper() if rec.patient_name else False

    def _inverse_upper_name(self):
        for rec in self:
            rec.patient_name = rec.patient_name_upper.lower() if rec.patient_name_upper else False

    @api.model
    def test_cron_job(self):
        print("Hello World!")

    # def toggle_active(self):
    #     print("This Is Archive button")

    patient_name = fields.Char(string='Name', required=True, track_visibility='always')
    patient_age = fields.Integer('Age', track_visibility='always', group_operator=False)
    patient_age_2 = fields.Float(string="Age2")
    notes = fields.Text(string='Notes')
    image = fields.Binary(string = "Image")
    name = fields.Char(string='Test')
    gender = fields.Selection([
        ('male', 'Male'),
        ('fe_male', 'Female'),
    ], default="male", string='Gender')
    age_group = fields.Selection([
        ('minor', 'Minor'),
        ('major', 'Major'),
    ], string='Age group', compute='set_age_group', store=True)
    name_sequence = fields.Char(string="Patient Refrence", required=True, copy=False,
                                readonly= True, index= True, default = lambda self : _('New'))
    appointment_count = fields.Integer("Appointment",  compute="count_patient_appointments")
    active = fields.Boolean("Active", default=True)
    doctor_id = fields.Many2one('hospital.doctor', string="Doctor")
    doctor_gender = fields.Selection([
        ('male', 'Male'),
        ('fe_male', 'Female'),
    ], string='Doctor Gender')
    email_id = fields.Char(string="Email")
    user_id = fields.Many2one('res.users', string="PRO")
    patient_name_upper = fields.Char(compute="_compute_upper_name", string="Patient Upper Name", inverse="_inverse_upper_name")
    company_id = fields.Many2one('res.company', required=True, default=lambda self: self.env.user.company_id)

    @api.model
    def create(self, vals):
        if vals.get('name_sequence', _('New')) == _('New'):
            vals['name_sequence'] = self.env['ir.sequence'].next_by_code('hospital.patient.sequence') or _('New')
        result = super(HospitalPatients, self).create(vals)
        return result