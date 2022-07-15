from odoo import api, fields, models
from ast import literal_eval

class HospitalSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    note = fields.Char(string='Default Note')
    module_crm = fields.Boolean(string='CRM')
    product_ids = fields.Many2many('product.product', string='Medicines')

    # sale setting Field
    quotation_amendment = fields.Boolean(string='Quotation Amendement')

    def set_values(self):
        res = super(HospitalSettings, self).set_values()
        self.env['ir.config_parameter'].set_param('om_hospital.note', self.note)
        self.env['ir.config_parameter'].set_param('om_hospital.product_ids', self.product_ids.ids)
        self.env['ir.config_parameter'].set_param('om_hospital.quotation_amendment', self.quotation_amendment)
        return res

    @api.model
    def get_values(self):
        res = super(HospitalSettings, self).get_values()
        ICPSudo = self.env['ir.config_parameter'].sudo()
        notes = ICPSudo.get_param('om_hospital.note')
        product_ids  = ICPSudo.get_param('om_hospital.product_ids')
        quotaion_amd  = ICPSudo.get_param('om_hospital.quotation_amendment')
        print(quotaion_amd)
        print(product_ids)
        res.update(
            note=notes,
            product_ids = [(6,0, literal_eval(product_ids))],
            quotation_amendment = quotaion_amd
        )
        return res
