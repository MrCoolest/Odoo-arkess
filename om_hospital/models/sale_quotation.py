from odoo import api, fields, models, _
from odoo.addons import decimal_precision as dp

class SaleQuotationNew(models.Model):
    _name = 'sale.quotaion.new'
    _description = "Sales Quotation"

    user_id = fields.Many2one('res.users', string='User', track_visibility='onchange', readonly=True,
                              states={'draft': [('readonly', False)]}, default=lambda self: self.env.user)
    company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env['res.company']._company_default_get('sale.quotaion.new'))

    name = fields.Char(string="Sale Quotation", required=True, copy=False,
                       readonly=True, index=True, default=lambda self: _('New'))
    partner_id = fields.Many2one('res.partner', string='Customer', required=True, change_default=True,
                                 track_visibility='always')
    invoice = fields.Many2one('res.partner', string='Invoice Address', required=True, change_default=True,
                                 track_visibility='always')
    delivery = fields.Many2one('res.partner', string='Delivery Address', required=True, change_default=True,
                                 track_visibility='always')
    # order_type = fields.Char(string="Order type", default='Direct', readonly=True)
    currency_id = fields.Many2one('res.currency', 'Currency', required=True,
                                  default=lambda self: self.env.user.company_id.currency_id.id)
    expiration_date = fields.Date(string='Expiration Date')
    # rfq_reference = fields.Many2one('purchase.rfq.new', string="Reference RFQ",
    #                                 domain="['|',('state','=','quotation_recd'),('state', '=','not_awarded')]")
    order_line = fields.One2many('sale.quotation.new.line', 'order_id', string='Order Lines',states={'cancel': [('readonly', True)], 'done': [('readonly', True)]}, copy=True)
    amendemets = fields.One2many('sale.quotaion.ambedment.new', 'amendment_history', string='Amendement history',states={'cancel': [('readonly', True)], 'done': [('readonly', True)]}, copy=True)
    state = fields.Selection([
        ('quotation', 'Quotation'),
        ('quotaion_sent', 'Quotation Sent'),
        ('quatation_ambedment', 'Quotation Ambedment'),
        ('sale_order', 'Sale order'),
    ], string="Status", readonly=True, default="quotation")

    amount_untaxed = fields.Monetary(string='Untaxed Amount', store=True, readonly=True, compute='_amount_all',
                                     track_visibility='always')
    amount_tax = fields.Monetary(string='Taxes', store=True, readonly=True, compute='_amount_all')
    amount_total = fields.Monetary(string='Total', store=True, readonly=True, compute='_amount_all')

    @api.multi
    def write(self, vals):
        result = super(SaleQuotationNew, self).write(vals)
        flag = self.env['ir.config_parameter'].sudo().get_param('om_hospital.quotation_amendment')
        if flag:
            if vals.get('order_line'):
                lines = []
                for line in self.order_line:
                    vals_list = {
                        'product_id': line.product_id.id,
                        'order_qty': line.order_qty,
                        'name': line.name,
                        'price_unit': line.price_unit,
                        'taxes_id': line.taxes_id.ids,
                    }
                    lines.append((0, 0, vals_list))

                vals_2 = {
                    'partner_id': self.partner_id.id,
                    'invoice': self.invoice.id,
                    'delivery': self.delivery.id,
                    'expiration_date': self.expiration_date,
                    'currency_id': self.currency_id.id,
                    'order_line': lines,
                    'amount_untaxed': self.amount_untaxed,
                    'amount_tax': self.amount_tax,
                    'amount_total': self.amount_total,
                    'amendment_history': self.id
                }

                new_amendement = self.env['sale.quotaion.ambedment.new'].create(vals_2)
                self.state = 'quatation_ambedment'
                # print(new_amendement)
        return result


    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):

            vals['name'] = self.env['ir.sequence'].next_by_code('new.sale.quotation.seq') or _('New')
        result = super(SaleQuotationNew, self).create(vals)
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

    def button_confirm(self):
        print('Confirm Sale is Working')
        lines = []
        for line in self.order_line:
            vals = {
                'product_id': line.product_id.id,
                'product_qty': line.order_qty,
                'name': line.name,
                'price_unit': line.price_unit,
                'taxes_id': line.taxes_id.ids,
            }
            lines.append((0, 0, vals))
        context = dict(self.env.context)
        context['form_view_initial_mode'] = 'edit'
        context['default_partner_id'] = self.partner_id.id
        context['default_validity_date'] = self.expiration_date
        context['default_order_line'] = lines
        self.state = 'sale_order'
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'sale.order',
            'view_id': self.env.ref("sale.view_order_form").id,
            'context': context
        }


class SaleQuotationNewLine(models.Model):
    _name = 'sale.quotation.new.line'


    salesman_id = fields.Many2one(related='order_id.user_id', store=True, string='Salesperson', readonly=True)
    name = fields.Text(string='Description', required=True)
    sequence = fields.Integer(string='Sequence', default=10)
    product_id = fields.Many2one('product.product', string='Product', domain=[('purchase_ok', '=', True)],
                                 change_default=True, required=True)
    product_uom = fields.Many2one('product.uom', string='Product Unit of Measure')
    order_qty = fields.Float(string='Order Quantity', required=True)
    taxes_id = fields.Many2many('account.tax', string='Taxes',
                                domain=['|', ('active', '=', False), ('active', '=', True)])
    price_unit = fields.Float(string='Unit Price', required=True, digits=dp.get_precision('Product Price'))

    order_id = fields.Many2one('sale.quotaion.new', string='Order Reference', index=True, ondelete='cascade')

    price_subtotal = fields.Monetary(compute='_compute_amount', string='Subtotal', store=True)
    price_total = fields.Monetary(compute='_compute_amount', string='Total', store=True)
    price_tax = fields.Float(compute='_compute_amount', string='Tax', store=True)

    partner_id = fields.Many2one('res.partner', related='order_id.partner_id', string='Partner', readonly=True,
                                 store=True)
    currency_id = fields.Many2one(related='order_id.currency_id', store=True, string='Currency', readonly=True)
    date_order = fields.Date(related='order_id.expiration_date', string='Order Date', readonly=True)


    @api.depends('order_qty', 'price_unit', 'taxes_id')
    def _compute_amount(self):
        for line in self:
            taxes = line.taxes_id.compute_all(line.price_unit, line.order_id.currency_id, line.order_qty, product=line.product_id, partner=line.order_id.partner_id)
            line.update({
                'price_tax': sum(t.get('amount', 0.0) for t in taxes.get('taxes', [])),
                'price_total': taxes['total_included'],
                'price_subtotal': taxes['total_excluded'],
            })

    @api.onchange('product_id')
    def on_change_product_id(self):
        for rec in self:
            rec.name = rec.product_id.name


# ------------------------------------------------  Sale Quotation Ambedment Table -------------------------------------------------------------------------
class SaleQuotationAmbedmentNew(models.Model):
    _name = 'sale.quotaion.ambedment.new'
    _description = "Sales Quotation Ambedment"

    name = fields.Char(string="Sale Quotation Ambedment", required=True, copy=False,
                       readonly=True, index=True, default=lambda self: _('New'))
    partner_id = fields.Many2one('res.partner', string='Customer', required=True, change_default=True,
                                 track_visibility='always')
    invoice = fields.Many2one('res.partner', string='Invoice Address', required=True, change_default=True,
                                 track_visibility='always')
    delivery = fields.Many2one('res.partner', string='Delivery Address', required=True, change_default=True,
                                 track_visibility='always')

    currency_id = fields.Many2one('res.currency', 'Currency', required=True,
                                  default=lambda self: self.env.user.company_id.currency_id.id)
    expiration_date = fields.Date(string='Expiration Date')

    order_line = fields.One2many('sale.quotation.ambedment.new.line', 'order_id', string='Order Lines',states={'cancel': [('readonly', True)], 'done': [('readonly', True)]}, copy=True)

    amendment_history = fields.Many2one('sale.quotaion.new', copy=True)

    state = fields.Selection([
        ('quotation', 'Quotation'),
        ('quotaion_sent', 'Quotation Sent'),
        ('quatation_ambedment', 'Quotation Ambedment'),
        ('sale_order', 'Sale order'),
    ], string="Status", readonly=True, default="quotation")

    amount_untaxed = fields.Monetary(string='Untaxed Amount', store=True, readonly=True, compute='_amount_all',
                                     track_visibility='always')
    amount_tax = fields.Monetary(string='Taxes', store=True, readonly=True, compute='_amount_all')
    amount_total = fields.Monetary(string='Total', store=True, readonly=True, compute='_amount_all')

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):

            vals['name'] = self.env['ir.sequence'].next_by_code('new.sale.quotation.ambedment.seq') or _('New')
        result = super(SaleQuotationAmbedmentNew, self).create(vals)
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



class SaleQuotationAmbedmentNewLine(models.Model):
    _name = 'sale.quotation.ambedment.new.line'

    name = fields.Text(string='Description')
    sequence = fields.Integer(string='Sequence', default=10)
    product_id = fields.Many2one('product.product', string='Product', domain=[('purchase_ok', '=', True)],
                                 change_default=True)
    product_uom = fields.Many2one('product.uom', string='Product Unit of Measure')
    order_qty = fields.Float(string='Order Quantity')
    taxes_id = fields.Many2many('account.tax', string='Taxes',
                                domain=['|', ('active', '=', False), ('active', '=', True)])
    price_unit = fields.Float(string='Unit Price', digits=dp.get_precision('Product Price'))

    order_id = fields.Many2one('sale.quotaion.ambedment.new', string='Order Reference', index=True, ondelete='cascade')

    price_subtotal = fields.Monetary(compute='_compute_amount', string='Subtotal', store=True)
    price_total = fields.Monetary(compute='_compute_amount', string='Total', store=True)
    price_tax = fields.Float(compute='_compute_amount', string='Tax', store=True)

    partner_id = fields.Many2one('res.partner', related='order_id.partner_id', string='Partner', readonly=True,
                                 store=True)
    currency_id = fields.Many2one(related='order_id.currency_id', store=True, string='Currency', readonly=True)
    date_order = fields.Date(related='order_id.expiration_date', string='Order Date', readonly=True)


    @api.depends('order_qty', 'price_unit', 'taxes_id')
    def _compute_amount(self):
        for line in self:
            taxes = line.taxes_id.compute_all(line.price_unit, line.order_id.currency_id, line.order_qty, product=line.product_id, partner=line.order_id.partner_id)
            line.update({
                'price_tax': sum(t.get('amount', 0.0) for t in taxes.get('taxes', [])),
                'price_total': taxes['total_included'],
                'price_subtotal': taxes['total_excluded'],
            })









