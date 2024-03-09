from odoo import models, fields, api
from datetime import datetime, timedelta

import odoo.exceptions
from odoo.exceptions import ValidationError


class AssetLoan(models.Model):
    _name = "asset.loan"

    asset_id = fields.Many2one('asset', domain="[('custody_id', '=', None), ('status', '=', 'available')]")
    start_date = fields.Date(default=datetime.now())
    end_date = fields.Date()
    custody_id = fields.Many2one("hr.employee")

    loan_accepted = fields.Date()
    loan_started = fields.Date()
    loan_returned = fields.Date()

    state = fields.Selection([('pending', 'Pending'),
                              ('accepted', 'Accepted'),
                              ('running', 'Running'),
                              ('rejected', 'Rejected'),
                              ('expired', 'Expired'),
                              ('returned', 'Returned')],
                             default='pending')

    def action_pending(self):
        for asset_id in self:
            if asset_id.asset_id.custody_id == self.custody_id or not asset_id.asset_id.custody_id:
                asset_id.asset_id.status = "available"
                asset_id.asset_id.custody_id = None
                self.loan_accepted = None
                self.loan_returned = None
                self.loan_started = None
                self.state = 'pending'
            else:
                raise odoo.exceptions.ValidationError('This asset with another one')

    def action_accept(self):
        for asset_id in self:
            if not asset_id.asset_id.custody_id:
                self.loan_accepted = datetime.now()
                self.state = 'accepted'
                asset_id.asset_id.status = "booked"
            else:
                raise odoo.exceptions.ValidationError('Some assets have a custody Already')

    def action_reject(self):
        self.state = 'rejected'

    def action_expire(self):
        self.state = 'expired'

    def action_return(self):
        for asset_id in self:
            if asset_id.asset_id.custody_id == self.custody_id:
                asset_id.asset_id.status = "available"
                asset_id.asset_id.custody_id = None
                self.loan_returned = datetime.now()
                self.state = 'returned'
            else:
                raise odoo.exceptions.ValidationError('This asset with another one')

    def change_custody(self):
        for asset_id in self:
            print(asset_id)
            asset_id.asset_id.custody_id = asset_id.custody_id.id

    def action_running(self):
        for asset_id in self:
            if not asset_id.asset_id.custody_id:
                asset_id.asset_id.custody_id = asset_id.custody_id.id
                self.loan_started = datetime.now()
                self.state = 'running'
                asset_id.asset_id.status = "loaned"

    # def _prepare_asset(self):
    #     asset_vals = super(AssetLoan, self)._prepare_asset()
    #     asset_vals['custody_id'] = self.custody_id.id
    #     return asset_vals
