from odoo import fields, models, api, _


class StockPickingEX(models.Model):
    _inherit = 'stock.picking'


    have_invoice = fields.Boolean(string="Have Invoice?")
    invoice_date = fields.Date(string="Invoice Date")
    invoice_num = fields.Char(string='Invoice Number')



    # @api.model
    # def create(self, vals):
    #     print(vals)