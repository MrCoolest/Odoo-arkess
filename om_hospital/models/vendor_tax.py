from odoo import fields,models,api

class VendorTaxes(models.Model):
    _inherit = 'purchase.order'


    @api.onchange('partner_id')
    def _amount_all(self):
        for data in self:
            print(data.partner_id.company_id.vat)
            if data.partner_id.company_id.vat != False:
                res = super(VendorTaxes, self)._amount_all()
                return res
            else:
                amount_untaxed = amount_tax = 0.0
                for line in data.order_line:
                    amount_untaxed += line.price_subtotal
                    amount_tax += 0
                data.update({
                    'amount_untaxed': data.currency_id.round(amount_untaxed),
                    'amount_tax': data.currency_id.round(amount_tax),
                    'amount_total': amount_untaxed + amount_tax,
                    })



