from odoo import models, fields, api
try:
  import qrcode
except ImportError:
  qrcode = None
try:
  import base64
except ImportError:
  base64 = None
from io import BytesIO

import odoo.exceptions
from odoo.exceptions import ValidationError

from datetime import datetime, timedelta


class Asset(models.Model):
    _name = "asset"

    quantity = fields.Integer(default=1)

    name = fields.Char(required=1)
    serial = fields.Text()
    price = fields.Float(default=100)
    buy_date = fields.Date(default=datetime.now())
    dep_fin_value = fields.Float(default=1)
    dep_period = fields.Integer(default=36)
    location_id = fields.Many2one("res.company")
    category_id = fields.Many2one("product.category")
    custody_id = fields.Many2one("hr.employee", readonly=True)
    sell_price = fields.Float()
    state = fields.Selection([
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('stopped', 'Stopped')
    ], default='draft')
    status = fields.Selection([
        ('available', 'Available'),
        ('booked', 'Booked'),
        ('workshop', 'Workshop'),
        ('loaned', 'Loaned')
    ], default='available')
    description = fields.Text()
    tag_ids = fields.Many2many('tag')
    currency_id = fields.Many2one('res.currency', string='Currency',
                                  default=lambda self: self.env.user.company_id.currency_id)
    current_price = fields.Float(compute='_compute_current_price')
    asset_qr_code = fields.Binary("QR Code", compute='generate_asset_qr_code')

    asset_moves = fields.One2many('asset.move', 'asset_id')
    asset_loans = fields.One2many('asset.loan', 'asset_id')

    def generate_asset_qr_code(self):
        for rec in self:
            if qrcode and base64:
                ir_param = self.env['ir.config_parameter'].sudo()
                base_url = ir_param.get_param('web.base.url')
                if base_url:
                    base_url += '/web#&model=%s&id=%s' % (rec._name, rec.id)
                qr = qrcode.QRCode(version=1,
                                   error_correction=qrcode.constants.ERROR_CORRECT_L,
                                   box_size=3,
                                   border=4)
                qr.add_data(base_url)
                qr.make(fit=True)
                img = qr.make_image()
                temp = BytesIO()
                img.save(temp, format="PNG")
                qr_image = base64.b64encode(temp.getvalue())
                rec.update({'asset_qr_code': qr_image})

    @api.model
    def create(self, data_list):
        res = ''
        data_list['state'] = 'active'
        quantity = data_list["quantity"]
        if quantity >= 1:
            for x in range(0, quantity):
                data_list['quantity'] = 1
                data_list["serial"] = (self.env["ir.sequence"]
                                       .next_by_code("asset", sequence_date=datetime.now().year) or "New")
                res = super(Asset, self).create(data_list)
        return res

    @api.onchange('price', 'buy_date', 'dep_period')
    def _compute_current_price(self):
        for rec in self:
            if rec.dep_period > 0 and rec.price > 0:
                current_price = rec.price - ((rec.price / rec.dep_period) * (
                        (datetime.now().year - rec.buy_date.year) * 12
                        + datetime.now().month - rec.buy_date.month))
                if current_price > rec.dep_fin_value:
                    rec.current_price = current_price
                else:
                    rec.current_price = rec.dep_fin_value

    def action_draft(self):
        for rec in self:
            rec.state = 'draft'

    def action_active(self):
        for rec in self:
            rec.state = 'active'

    def action_stop(self):
        for rec in self:
            rec.state = 'stopped'


