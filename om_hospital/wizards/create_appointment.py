from odoo import  models, fields, api, _

class CreateAppointment(models.TransientModel):
    _name = 'create.appointment'


    patient_id = fields.Many2one('hospital.patient', string='Patient')
    appointment_date = fields.Date(string="Appointment Date")


    def create_appointment(self):
        vals = {
            'patient_id' : self.patient_id.id,
            'appointment_date' : self.appointment_date,
            'notes' : 'Testing The Odoo'
        }
        self.patient_id.message_post(body='Appointment Created Successfully', subject="Appointment Creation")
        new_appointment = self.env['hospital.appointment'].create(vals)
        context = dict(self.env.context)
        context['form_view_initial_mode'] = 'edit'
        return {
            'type' : 'ir.actions.act_window',
            'view_type' : 'form',
            'view_mode' : 'form',
            'res_model' : 'hospital.appointment',
            'res_id' : new_appointment.id,
            'context' : context
        }

    def get_data(self):
        print("Getting Data From DB")
        appointment = self.env['hospital.appointment'].search([])
        for rec in appointment:
            print(rec.name)
        return {
            'type' : 'ir.actions.do_nothing'
        }

    def delete_patient(self):
        for rec in self:
            print(rec.patient_id.id)
            rec.patient_id.unlink()

    def print_report(self):
        data = {
            'model': 'create.appointment',
            'form': self.read()[0]
        }
        if data['form']['patient_id']:
            selected_patient = data['form']['patient_id'][0]
            appointments = self.env['hospital.appointment'].search([('patient_id', '=', selected_patient)])
        else:
            appointments = self.env['hospital.appointment'].search([])
        appointment_list = []
        for app in appointments:
            vals = {
                'name': app.name,
                'notes': app.notes,
                'appointment_date': app.appointment_date
            }
            appointment_list.append(vals)
        print("appointments", appointments)
        data['appointments'] = appointment_list
        print("Data", data)
        print(data['appointments'])
        da = data['appointments']
        return self.env.ref('om_hospital.report_appointment').with_context(landscape=True).report_action(self, data)
