from odoo import api, fields, models
class HrEmployee(models.Model):
    _inherit = "hr.employee"

    employee_id = fields.Char(string="Employee ID ", copy=False)