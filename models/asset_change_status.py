from odoo import models, fields, api
from datetime import datetime, timedelta

import odoo.exceptions
from odoo.exceptions import ValidationError


class AssetChangeStatus(models.Model):
    _name = "asset.change.status"

    asset_id = fields.Many2one('asset')
    action_date = fields.Date(default=datetime.now())
    current_status = fields.Selection([
        ('available', 'Available'),
        ('booked', 'Booked'),
        ('workshop', 'Workshop'),
        ('loaned', 'Loaned')
    ], default='available')

    new_status = fields.Selection([
        ('available', 'Available'),
        ('booked', 'Booked'),
        ('workshop', 'Workshop'),
        ('loaned', 'Loaned')
    ], default='available')

    @api.model
    def create(self, data_list):
        res = super(AssetChangeStatus, self).create(data_list)
        for asset_id in res:
            asset_id.asset_id.status = res.new_status
        return res

    @api.onchange("asset_id")
    def onchange_asset(self):
        self.current_status = self.asset_id.status