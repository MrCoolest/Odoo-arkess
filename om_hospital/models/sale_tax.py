from odoo import fields,models,api


# inheriting the res.company
class SalesTaxesmodels(models.Model):
    _inherit = 'sale.order'


    @api.onchange('partner_id')
    def _amount_all(self):
        for data in self:
            if data.partner_id.company_id.vat != False:
                res = super(SalesTaxesmodels, self)._amount_all()
            else:
                amount_untaxed = amount_tax = 0.0
                for line in data.order_line:
                    amount_untaxed += line.price_subtotal
                    amount_tax += 0
                data.update({
                    'amount_untaxed': amount_untaxed,
                    'amount_tax': amount_tax,
                    'amount_total': amount_untaxed + amount_tax,
                })







