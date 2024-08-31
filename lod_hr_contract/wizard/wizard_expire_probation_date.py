# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta
import datetime
from dateutil.relativedelta import relativedelta
import xlwt
import base64
from io import BytesIO

class CustomExcel(models.TransientModel):
    _name = "report.expire.probation.date.wizard"
    _description = "Report Expire and Probation Date"

    repot_type = fields.Selection([
        ('work_expiry_date', 'Work Expiration Date'),
        ('Probation_date', 'Probation Date'),
    ], string='Report Type')
    duration = fields.Integer('Duration')
    show_expired = fields.Boolean('Show Expired')

    def open_expire_probation_date_form(self):
        duration = fields.Datetime.now() + datetime.timedelta(days=self.duration)
        if self.repot_type == 'work_expiry_date':
            name = _('Work Expiration Date')
            model = 'hr.contract'
            if self.show_expired:
                domain = [
                            ('date_start', '>=', duration),
                        '|',('date_end', '<=', duration),
                            ('date_end', '<', fields.Datetime.now())
                        ]
            else:
                domain = [
                            ('date_start', '>=', duration),
                            ('date_end', '<=', duration),
                        ]
        else:
            name = _('Probation Date')
            model = 'hr.employee'
            if self.show_expired:
                domain = [
                            ('work_permit_expiration_date', '>=', fields.Datetime.now()),
                        '|',('work_permit_expiration_date', '<=', duration),
                            ('work_permit_expiration_date', '<', fields.Datetime.now())
                        ]
            else:
                domain = [
                            ('work_permit_expiration_date', '>=', fields.Datetime.now()),
                            ('work_permit_expiration_date', '<=', duration),
                        ]

        return {
            'type': 'ir.actions.act_window',
            'name': name,
            'res_model': model,
            'view_mode': 'tree,form',
            'view_ids': [(False, 'tree'),(False, 'form')],
            'domain': domain,
        }
