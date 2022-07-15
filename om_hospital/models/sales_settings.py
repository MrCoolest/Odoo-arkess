from odoo import api, fields, models
from ast import literal_eval

# class SaleSettingsAdd(models.TransientModel):
#     _inherit = 'res.config.settings'


    # def set_values(self):
    #     res = super(SaleSettingsAdd, self).set_values()
    #     self.env['ir.config_parameter'].set_param('om_hospital.quotation_amendment', self.quotation_amendment)
    #     return res
    #
    # @api.model
    # def get_values(self):
    #     # res = super(SaleSettingsAdd, self).get_values()
    #     res = super(SaleSettingsAdd, self)
    #     print(res)
    #     ICPSudo = self.env['ir.config_parameter'].sudo()
    #     quotation_amd = ICPSudo.get_param('om_hospital.quotation_amendment')
    #     print(quotation_amd)
    #     res.update(
    #         quotation_amendment=quotation_amd
    #     )
        # ICPSudo = self.env['ir.config_parameter'].sudo()