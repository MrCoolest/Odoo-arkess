from odoo import fields, models, api, _
from odoo.addons import decimal_precision as dp
from datetime import datetime
class RequestforQuotation(models.Model):
    _name = 'purchase.rfq.new'

    name = fields.Char(string="New RFQ", required=True, copy=False,
                       readonly=True, index=True, default=lambda self: _('New'))
    partner_id = fields.Many2one('res.partner', string='Vendor', required=True, change_default=True, track_visibility='always')
    order_type = fields.Char(string="Order type", default='Direct', readonly=True)
    currency_id = fields.Many2one('res.currency', 'Currency', required=True, default=lambda self: self.env.user.company_id.currency_id.id)
    rfq_date = fields.Datetime(string='RFQ Date', default=str(datetime.now()))
    rfq_reference = fields.Many2one('purchase.rfq.new', string="Reference RFQ", domain="['|',('state','=','quotation_recd'),('state', '=','not_awarded')]")
    order_line = fields.One2many('rfq.order.line', 'order_id', string='Order Lines', states={'cancel': [('readonly', True)], 'done': [('readonly', True)]}, copy=True)
    state = fields.Selection([
        ('quotation_recd', 'Quotation Recd'),
        ('awarded', 'Awarded'),
        ('not_awarded', 'Not Awarded'),
    ], string="Status", readonly=True, default="quotation_recd")

    amount_untaxed = fields.Monetary(string='Untaxed Amount', store=True, readonly=True, compute='_amount_all',
                                     track_visibility='always')
    amount_tax = fields.Monetary(string='Taxes', store=True, readonly=True, compute='_amount_all')
    amount_total = fields.Monetary(string='Total', store=True, readonly=True, compute='_amount_all')

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('new.rfq.seq') or _('New')

        result = super(RequestforQuotation, self).create(vals)
        return result

    @api.depends('order_line.price_total')
    def _amount_all(self):
        for order in self:
            amount_untaxed = amount_tax = 0.0
            for line in order.order_line:
                amount_untaxed += line.price_subtotal
                amount_tax += line.price_tax
            order.update({
                'amount_untaxed': order.currency_id.round(amount_untaxed),
                'amount_tax': order.currency_id.round(amount_tax),
                'amount_total': amount_untaxed + amount_tax,
            })

    @api.onchange('rfq_reference')
    def on_change_rfq_reference(self):
        for rec in self:
            rec.partner_id =  rec.rfq_reference.partner_id
            rec.currency_id =  rec.rfq_reference.currency_id
            rec.amount_untaxed =  rec.rfq_reference.amount_untaxed
            rec.amount_tax =  rec.rfq_reference.amount_tax
            rec.amount_total =  rec.rfq_reference.amount_total
            rec.order_line =  rec.rfq_reference.order_line

    def button_confirm(self):
        # create_purchase =
        val_of_ref = self.env['purchase.rfq.new'].search([('rfq_reference','=',self.rfq_reference.id)])
        print(val_of_ref)
        for rec in val_of_ref:
            rec.state = 'not_awarded'
        lines = []
        for line in self.order_line:
            vals = {
                'product_id': line.product_id.id,
                'product_qty': line.total_qty,
                'name': line.name,
                'price_unit': line.price_unit,
                'date_planned': datetime.now(),
                'product_uom': line.product_uom.id,
                'taxes_id' :  line.taxes_id.ids,
            }
            lines.append((0, 0, vals))
        context = dict(self.env.context)
        # send_data.partner_id = self.partner_id
        context['form_view_initial_mode'] = 'edit'
        context['default_partner_id'] = self.partner_id.id
        context['default_order_line'] = lines
        print(lines)
        print(context)
        self.state = 'awarded'
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'purchase.order',
            'view_id': self.env.ref("purchase.purchase_order_form").id,
            'context': context
        }

class RfqOrderLine(models.Model):
    _name = 'rfq.order.line'

    name = fields.Text(string='Description', required=True)
    sequence = fields.Integer(string='Sequence', default=10)
    product_id = fields.Many2one('product.product', string='Product', domain=[('purchase_ok', '=', True)], change_default=True, required=True)
    product_uom = fields.Many2one('product.uom', string='Product Unit of Measure', required=True)
    request_qty = fields.Float(string='Request Quantity', required=True)
    order_qty = fields.Float(string='Order Quantity', required=True)
    total_qty = fields.Float(string='Total Quantity', required=True)
    taxes_id = fields.Many2many('account.tax', string='Taxes', domain=['|', ('active', '=', False), ('active', '=', True)])
    price_unit = fields.Float(string='Unit Price', required=True, digits=dp.get_precision('Product Price'))

    order_id = fields.Many2one('purchase.rfq.new', string='Order Reference', index=True, ondelete='cascade')


    price_subtotal = fields.Monetary(compute='_compute_amount', string='Subtotal', store=True)
    price_total = fields.Monetary(compute='_compute_amount', string='Total', store=True)
    price_tax = fields.Float(compute='_compute_amount', string='Tax', store=True)

    partner_id = fields.Many2one('res.partner', related='order_id.partner_id', string='Partner', readonly=True,
                                 store=True)
    currency_id = fields.Many2one(related='order_id.currency_id', store=True, string='Currency', readonly=True)
    date_order = fields.Datetime(related='order_id.rfq_date', string='Order Date', readonly=True)



    @api.depends('order_qty', 'price_unit', 'taxes_id')
    def _compute_amount(self):
        for line in self:
            taxes = line.taxes_id.compute_all(line.price_unit, line.order_id.currency_id, line.total_qty, product=line.product_id, partner=line.order_id.partner_id)
            line.update({
                'price_tax': sum(t.get('amount', 0.0) for t in taxes.get('taxes', [])),
                'price_total': taxes['total_included'],
                'price_subtotal': taxes['total_excluded'],
            })

    @api.onchange('product_id')
    def on_change_product_id(self):
        for rec in self:
            rec.name = rec.product_id.name

