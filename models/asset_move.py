from odoo import models, fields, api
from datetime import datetime, timedelta

import odoo.exceptions
from odoo.exceptions import ValidationError


class AssetMove(models.Model):
    _name = "asset.move"

    asset_id = fields.Many2one('asset', domain="[('custody_id', '=', None), ('status', '=', 'available')]")
    move_date = fields.Date(default=datetime.now())
    current_location_id = fields.Many2one("res.company", string="Current Location", default='_set_current_location')
    new_location_id = fields.Many2one("res.company", "Destination")

    @api.model
    def create(self, data_list):
        res = super(AssetMove, self).create(data_list)
        for asset_id in res:
            asset_id.asset_id.location_id = res.new_location_id.id
        return res

    @api.onchange("asset_id")
    def onchange_asset(self):
        self.current_location_id = self.asset_id.location_id.id

    def _set_current_location(self):
        return self.asset_id.location_id.id
