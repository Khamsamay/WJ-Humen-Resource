from odoo import api, fields, models
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

class HrEmployee(models.Model):
    _inherit = "hr.employee"

    employee_id = fields.Char(string="Employee ID ", copy=False)
    allowance_id = fields.Many2one('hr.payroll.allowance', string='Allowance')
    rest_day = fields.Float(related='allowance_id.rest_day_of_month', string='Rest Day')
    remain_rest_day = fields.Float(compute='calculate_allowance', string='Remain Rest Day')
    allowance_amount = fields.Float(compute='calculate_allowance',string='Allowance Amount')
    increased_id = fields.Many2one('hr.payroll.increased', string='Increase')
    increased_amount = fields.Float(related="increased_id.increased_amount", string='Increased Amount')
    limit_amount = fields.Float(related="increased_id.limit_amount", string='Limit Amount')

    def last_day_of_month(self, date):
        return date.replace(day=1) + relativedelta(months=2) - relativedelta(days=1)

    @api.depends('allowance_id','remain_rest_day')
    def calculate_allowance(self):
        for rec in self:
            now = fields.Datetime.now() + timedelta(hours=7)
            start_date = now.replace(day=1, hour=00, minute=00, second=00)
            end_date = now.replace(hour=23, minute=59, second=59)
            end_date = self.last_day_of_month(end_date)
            print('========start_date========',start_date)
            print('========end_date========',end_date)
            hr_leave_ids = self.env['hr.leave'].search([('employee_id','=',rec.id),('state','=','validate'),('request_date_from','>=',start_date),('request_date_to','<=',end_date)])
            leave_day_count = sum(hr_leave_ids.mapped('number_of_days_display'))
            date_to = hr_leave_ids.mapped('request_date_to')
            print('========date_to========',date_to)

            if float(leave_day_count) > rec.rest_day:
                rec.remain_rest_day = 0
                rec.allowance_amount = 0
            else:
                rec.remain_rest_day = rec.rest_day - float(leave_day_count)
                rec.allowance_amount = rec.remain_rest_day * rec.allowance_id.amount
              