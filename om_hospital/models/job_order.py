from odoo import fields,models,api,_



class PurchaseOrderJobEntry(models.Model):
    _inherit = "purchase.order"


    order_type_flag = fields.Selection([
        ('JO', 'Job Order'),
        ('PO', 'Purchase Order'),
    ], string='Order Type', compute='set_flag', store=True)
    flag_id = fields.Boolean(string="Flag For Order Type")
    recived_item = fields.Boolean(string="Same Item to Be Recived")
    product_in_JO = fields.One2many('purchase.order.line', 'product_in_id', required=True, string='Product In', states={'cancel': [('readonly', True)], 'done': [('readonly', True)]}, copy=True)
    product_out_JO = fields.One2many('purchase.order.line', 'product_out_id', required=True, string='Product Out', states={'cancel': [('readonly', True)], 'done': [('readonly', True)]}, copy=True)

    @api.onchange('recived_item')
    def _onchange_item(self):
        for rec in self:
            if rec.recived_item:
                lines = []

                for line in rec.product_out_JO:
                    vals = {
                        'product_id' : line.product_id,
                        'product_qty' : line.product_qty,
                        'name' : line.name,
                        'price_unit' : line.price_unit,
                        'date_planned' : line.date_planned,
                        'product_uom' : line.product_uom
                    }
                    lines.append((0,0,vals))
                rec.order_line = lines


    @api.depends('flag_id')
    def set_flag(self):
        for rec in self:
            print(f'Flag Val {rec.flag_id}')
            if rec.flag_id:
                rec.order_type_flag='JO'
            else:
                rec.order_type_flag='PO'


    @api.model
    def create(self, vals):
        # print(vals)
        if vals.get('flag_id'):
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code('Job.Order.seq') or _('New')
            result = super(PurchaseOrderJobEntry, self).create(vals)
            return  result
        else:
            result = super(PurchaseOrderJobEntry, self).create(vals)
            return result

        # result = super(PurchaseOrderJobEntry, self).create(vals)
        # print(self.flag_id)
        # return result
    # related_job_id = fields.char('purchase.requisition', string='Purchase Agreement')
    # partner_id1 = fields.Many2one('res.partner', string='Vendor', required=True, track_visibility='always')
    # @api.model
    # def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
    #     menu_id = self._context.get('menu_id', False)
    #     action = self._context.get('action', False)
    #     print(menu_id, action)
        # res = super(YourClassName, self).fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar,
        #                                                  submenu=submenu)
        # return res

    class PurchaseOrderLine_IN_Out(models.Model):
        _inherit = "purchase.order.line"

        product_in_id = fields.Many2one('purchase.order', string='Product_In Reference', index=True,
                                   ondelete='cascade')

        product_out_id = fields.Many2one('purchase.order', string='Product_Out Reference', index=True, required=True,
                                   ondelete='cascade')
