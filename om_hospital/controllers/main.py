from  odoo import http
from odoo.http import request
# from odoo.addons.website_sale.controllers.main import WebsiteSale
# from ...website_sale.controllers.main import WebsiteSale



# from ...website_sale.controllers.main import WebsiteSale

# from odoo.addons.
class AppoitnmentController(http.Controller):

    @http.route('/om_hospital/appointment/', auth="user", type="json")
    def appointment_banner(self):
        return {
            'html' : """
                <div>
                <center> <h1> <font color="red">Hello From Ankit</font></h1></center>
                <p><font color="blue"><a href="https://www.youtube.com/watch?v=Suyekbyj1cs&list=PLqRRLx0cl0hoJhjFWkFYowveq2Zn55dhM&index=111&ab_channel=OdooMates">
                 Get Notification Regarding All The Odoo Videos
                 </a></font></p></center>
                </div>
                """
        }

# class WebsiteSaleInherit(WebsiteSale):
#
#     @http.route([
#         '''/shop''',
#         '''/shop/page/<int:page>''',
#         '''/shop/category/<model("product.public.category", "[('website_id', 'in', (False, current_website_id))]"):category>''',
#         '''/shop/category/<model("product.public.category", "[('website_id', 'in', (False, current_website_id))]"):category>/page/<int:page>'''
#     ], type='http', auth="public", website=True)
#     def shop(self, page=0, category=None, search='', ppg=False, **post):
#         res = super(WebsiteSaleInherit, self).shop(page=0, category=None, search='', ppg=False, **post)
#         print("Inherited Odoo Mates ....", res)
#         return res

class Hospital(http.Controller):

    @http.route('/patient_webform', type="http", auth="public", website=True)
    def patient_webform(self, **kw):
        print("Execution Here.........................")
        doctor_rec = request.env['hospital.doctor'].sudo().search([])
        return http.request.render('om_hospital.create_patient', {'patient_name': 'Odoo Mates Test 123', 'doctor_rec': doctor_rec})

    @http.route('/create/webpatient', type="http", auth="public", website=True)
    def create_webpatient(self, **kw):
        print("Data Received.....", kw)
        request.env['hospital.patient'].sudo().create(kw)
        doctor_val = {
            'name': kw.get('patient_name')
        }
        request.env['hospital.doctor'].sudo().create(doctor_val)
        return request.render("om_hospital.patient_thanks", {})


    # @http.route('/patient-webform', auth="public", website=True)
    # def patient_webform(self, **kwargs):
    #     print("working")
    #     return request.render('om_hospital.create_patient',{})
    #
    # @http.route('/create/webpatient', auth="public", website=True)
    # def patient_webform(self, **kwargs):
    #     print("Its Working")
    #     # request.env['hospital.patient'].sudo().create(kwargs)
    #     return http.request.render('om_hospital.patient_thanks', {})


    @http.route('/hospital/patient/', website=True, auth='public')
    def hospital_patient(self, *args, **kwargs):
        # return "Hello World"
        patient = request.env['hospital.patient'].sudo().search([])
        print(patient)
        return request.render('om_hospital.patients_page',{'patient' : patient})

    # @http.route('/create_patient', type='json', auth='user')
    # def create_patient(self, **rec):
    #     if request.jsonrequest:
    #         print("rec", rec)
    #         if rec['name']:
    #             vals = {
    #                 'patient_name': rec['name'],
    #                 'email_id': rec['email_id']
    #             }
    #             new_patient = request.env['hospital.patient'].sudo().create(vals)
    #             print("New Patient Is", new_patient)
    #             args = {'success': True, 'message': 'Success', 'id': new_patient.id}
    #     return args
    #
    # @http.route('/get_patients', type='json', auth='user')
    # def get_patients(self):
    #     print("Yes here entered")
    #     patients_rec = request.env['hospital.patient'].search([])
    #     patients = []
    #     for rec in patients_rec:
    #         vals = {
    #             'id': rec.id,
    #             'name': rec.patient_name,
    #             'sequence': rec.name_sequence,
    #         }
    #         patients.append(vals)
    #     print("Patient List--->", patients)
    #     data = {'status': 200, 'response': patients, 'message': 'Done All Patients Returned'}
    #     return data
