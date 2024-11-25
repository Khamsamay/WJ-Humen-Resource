# -*- coding: utf-8 -*-
# This module and its content is copyright of Technaureus Info Solutions Pvt. Ltd.
# - © Technaureus Info Solutions Pvt. Ltd 2020. All rights reserved.

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from datetime import datetime


class AttendanceLog(models.Model):
    _name = 'lod.attendance.log'
    _description = 'attendance log'
    _order = 'punching_time'
    _rec_name = 'punching_time'

    log_id = fields.Integer('Log ID')
    employee_id = fields.Many2one('hr.employee', string='Employee')
    status = fields.Selection([('0', 'Check In'),
                               ('1', 'Check Out'),
                               ('2', 'Punched')], string='Status')
    punching_time = fields.Datetime('Punching Time')
    punch_state = fields.Char('Punch State')
    is_calculated = fields.Boolean('Calculated', default=False)
    # area_id = fields.Many2one('employee.area', string='Area')
    area_name = fields.Char('Area')
    device = fields.Char('Device')
    company_id = fields.Many2one('res.company', string='Company', readonly=True, default=lambda self: self.env.company)

    start_time = fields.Datetime(string="Start Time")
    end_time = fields.Datetime(string="End Time")
    in_out_diff = fields.Float(string="In/Out Difference", compute="_compute_in_out_diff")

    @api.depends('start_time', 'end_time')
    def _compute_in_out_diff(self):
        for record in self:
            if record.start_time and record.end_time:
                record.in_out_diff = (record.end_time - record.start_time).total_seconds() / 3600  # Difference in hours
            else:
                record.in_out_diff = 0
                
    def unlink(self):
        if any(self.filtered(lambda log: log.is_calculated == True)):
            raise UserError(('You cannot delete a Record which is already Calculated !!!'))
        return super(AttendanceLog, self).unlink()

# {'id': 447, 'emp_code': '2024', 'punch_time': datetime.datetime(2024, 9, 11, 6, 56, 48, tzinfo=datetime.timezone(datetime.timedelta(seconds=25200))), 'punch_state': '255', 'area_alias': 'AR-01', 'emp_id': None, 'terminal_id': None}, 
# {'id': 448, 'emp_code': '18', 'punch_time': datetime.datetime(2024, 9, 11, 6, 56, 51, tzinfo=datetime.timezone(datetime.timedelta(seconds=25200))), 'punch_state': '255', 'area_alias': 'AR-01', 'emp_id': None, 'terminal_id': None}, 
# {'id': 449, 'emp_code': '22', 'punch_time': datetime.datetime(2024, 9, 11, 6, 56, 53, tzinfo=datetime.timezone(datetime.timedelta(seconds=25200))), 'punch_state': '255', 'area_alias': 'AR-01', 'emp_id': None, 'terminal_id': None}


# class HrAttendance(models.Model):
#     _inherit = "hr.attendance"

#     punch_date = fields.Date(string='Punch Date')

#     def compute_in_out_difference(self):
#         for attendance in self:
#             if attendance.check_in and attendance.check_out:
#                 check_in = datetime.strptime(str(attendance.check_in), '%Y-%m-%d %H:%M:%S')
#                 check_out = datetime.strptime(str(attendance.check_out), '%Y-%m-%d %H:%M:%S')
#                 diff1 = check_out - check_in
#                 total_seconds = diff1.seconds
#                 diff2 = total_seconds / 3600.0
#                 attendance.in_out_diff = diff2
#             else:
#                 attendance.in_out_diff = 0

#     in_out_diff = fields.Float('Difference', compute='compute_in_out_difference')

#     def unlink(self):
#         for record in self:
#             domain = [('employee_id', '=', record.employee_id.id), '|',
#                       ('punching_time', '=', record.check_in),
#                       ('punching_time', '=', record.check_out)]
#             attend_obj = self.env['attendance.log'].search(domain)
#             for log in attend_obj:
#                 log.is_calculated = False
#         return super(HrAttendance, self).unlink()
