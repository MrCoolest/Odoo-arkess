from odoo import fields,models,api
from odoo.exceptions import ValidationError
import re
# inheriting the res.company
class CompanyValidation(models.Model):
    _inherit = 'res.company'

    @api.model
    def create(self, vals_list):
        if vals_list['company_registry'] and vals_list['vat']:
            if (vals_list['state_id'] == False):
                raise ValidationError('State is Must because of Gst Validation')
            gst_val = self.check_gst(vals_list['vat'], vals_list['state_id'])
            if gst_val is not None:
                if gst_val is False:
                    raise ValidationError('GST is not Valid, Please Enter Valid GST')

        elif vals_list['company_registry'] or vals_list['vat']:
            raise ValidationError('If You have Registed company than GST is Must to fill')
        res = super(CompanyValidation, self).create(vals_list)
        return res


    def check_gst(self,gst_num,state):
        if isinstance(state,int):
            state = self.env['res.country.state'].browse(state)
            if state.country_id.name != 'India':
                return False

        if len(gst_num) == 15:
            print("wor2")
            state_code = self.env['res.country.state'].search([('name', '=', state.name)]).l10n_in_tin
            print(f"State_code= {state_code}")
            regex = "^"+state_code+"[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9]{1}[A-Z]{2}$"
            pattern = re.compile(regex)
            if(re.search(pattern,gst_num)):
                return True
            else:
                return False
        else:
            return False


    @api.multi
    def write(self, vals):

        for data in self:

            if (vals.get('vat')==None):
                vals['vat'] = data.vat

            if(vals.get('company_registry')==None):
                vals['company_registry'] = data.company_registry

            if (vals.get('state_id') == None):
                vals['state_id'] = data.state_id


            if vals['company_registry'] and vals['vat'] == False:
                raise ValidationError('GST is must for Registed Company')
            elif vals['vat'] and vals['company_registry'] == False:
                raise ValidationError('Registry id is must if you have GST')

            gst_val = data.check_gst(vals['vat'],vals['state_id'])
            if gst_val is False:
                raise ValidationError('GST is not Valid, Please Enter Valid GST')


        res = super(CompanyValidation, self).write(vals)
        return res





    # @api.multi
    # def gst_validation(self, vals_list):
    #     # res = super(CompanyValidation, self).create(vals_list)
    #     #This is Hpw we can do the Custome Coding
    #     print("its Working")
    #     print(vals_list)
        # return res

    # @api.constrains('company_registry', 'vat')
    # def check_registry(self):
    #     for data in self:
    #         print(data.company_registry)
    #         print(data.vat)
            # if data.company_registry and data.vat is False:
            #     raise ValidationError('GST is must for Registed Company')
    #         # elif data.vat is True and data.company_registry is False:
    #         #     raise ValidationError('Registry number is must if you have GST')

    # @api.constrains('vat')
    # def check_gst(self):
    #     for data in self:
    #         print(data.company_registry)
    #         print(data.vat)
    #         if data.vat and data.company_registry is False:
    #             raise ValidationError('Registry number is must if you have GST')

    # @api.onchange('company_registry','vat')
    # def check_registry(self):
    #     for data in self:
    #         print(data.company_registry)
    #         print(data.vat )
    #         if data.company_registry != "" and data.vat == "":
    #             raise ValidationError('GST is must for Registed Company')
    #         # elif data.vat != "" and data.company_registry === "":
    #         #     raise ValidationError('Registry number is must if you have GST')

    # @api.onchange('vat')
    # def check_gst(self):
    #     for data in self:
    #         print(data.company_registry)
    #         print(data.vat)
    #         if data.vat and data.company_registry is False:
    #             raise ValidationError('Registry number is must if you have GST')

    # @api.multi
    # def method(self, args):
    #     for data in self:
    #         print(data.company_registry)
    #         print(data.vat)
    #         print(args)