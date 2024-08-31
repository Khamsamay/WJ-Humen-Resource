from odoo import api, fields, models

class HrPayrollIncreased(models.Model):
    _name = "hr.payroll.increased"
    _description = "HR Payroll Increased"
    
    name = fields.Char('Name')
    country_id = fields.Many2one('res.country', string='Nationality')
    increased_daily = fields.Selection([
        ('1', 'Month'),
        ('3', 'Quarter'),
        ('6', 'Half Yearly'),
        ('12', 'Yearly'),
    ], string='Increasing')
    increased_amount = fields.Float('Increased Amount')
    limit_amount = fields.Float('Limit Amount')

class HrAllowance(models.Model):
    _name = "hr.payroll.allowance"
    _description = "HR Payroll Allowance"
    
    name = fields.Char('Name')
    rest_day_of_month = fields.Float('Rest Day/Mounth')
    amount = fields.Float('Allowance Amount')


class HrBatchAdvanceCommission(models.Model):
    _name = "hr.payroll.advance.commission"
    _description = "HR Payroll Allowance"
    
    name = fields.Char('Name')
    date_start = fields.Date('Date Start')
    date_end = fields.Date('Date End')
    adv_comm_line_ids = fields.One2many('hr.payroll.advance.commission.line', 'adv_comm_id', string='Advance-Commission Line')

class HrBatchAdvanceCommissionLine(models.Model):
    _name = "hr.payroll.advance.commission.line"
    _description = "HR Payroll Allowance"
    
    adv_comm_id = fields.Many2one('hr.payroll.advance.commission', string='Advance-Commission')
    employee_id = fields.Many2one('hr.employee', string='Employee')
    date_start = fields.Date(related='adv_comm_id.date_start', string='Date Start')
    date_end = fields.Date(related='adv_comm_id.date_end', string='Date End')
    name = fields.Char('Name', compute="employee_id.name")
    adv_amount = fields.Float('Advance Amount') 
    comm_amount = fields.Float('Commission Amount')