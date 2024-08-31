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
