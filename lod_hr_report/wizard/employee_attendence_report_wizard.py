# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
import xlwt
import base64
from io import BytesIO

class CustomExcel(models.TransientModel):
    _name = "custom.excel.class"
    _rec_name = 'datas_fname'
    _description = "Employee Excel Report Wizard"

    file_name = fields.Binary(string="Report")
    datas_fname = fields.Char(string="Filename")


class EmployeeAttendenceReportWizard(models.TransientModel):
    _name = "employee.attendence.report.wizard"
    _description = "Employee Report Wizard"

    is_employee = fields.Boolean(string="Employees", default=True)
    is_department = fields.Boolean(string="Departments")
    hr_employee_ids = fields.Many2many("hr.employee", string="Employees Selection")
    hr_department_ids = fields.Many2many("hr.department", string="Departments Selection")
    select_all_employee = fields.Boolean(default=True, string="Select All Employees")
    select_all_department = fields.Boolean(default=False, string="Select All Departments")
    starting_date = fields.Date(string="Start Date", required=True)
    ending_date = fields.Date(string="End Date", required=True)

    @api.onchange('is_employee')
    def _onchange_is_employee(self):
        if self.is_employee:
            self.is_department = False
            self.hr_department_ids = False
        else:
            self.select_all_employee = False
            self.hr_employee_ids = False

    @api.onchange('is_department')
    def _onchange_is_department(self):
        if self.is_department:
            self.is_employee = False
            self.hr_employee_ids = False
        else:
            self.select_all_department = False
            self.hr_department_ids = False

    @api.onchange('select_all_employee', 'select_all_department')
    def _onchange_select_all(self):
        if self.is_employee and self.select_all_employee:
            self.hr_employee_ids = self.env['hr.employee'].search([])
        elif not self.select_all_employee:
            self.hr_employee_ids = False

        if self.is_department and self.select_all_department:
            self.hr_department_ids = self.env['hr.department'].search([])
        elif not self.select_all_department:
            self.hr_department_ids = False

    def generate_employee_pdf_report(self):
        self._validate_dates()
        data = {
            'form_data': self.read()[0],
        }
        return self.env.ref('lod_hr_report.action_report_attendence_report_wizard').report_action(self, data=data)

    def generate_employee_excel_report(self):
        self._validate_dates()

        if not self.hr_employee_ids and not self.select_all_employee:
            raise ValidationError(_("No employees selected. Please select employees or choose 'Select All Employees' option."))

        workbook = xlwt.Workbook(encoding='utf-8')
        filename = "Employee_Excel_Report.xls"
        sheet = workbook.add_sheet("Employee Details")

        date_format = xlwt.XFStyle()
        date_format.num_format_str = 'dd/mm/yyyy/'

        format1 = xlwt.easyxf(
            'align: horiz center; font: color black, bold True;'
            'borders: top_color black, bottom_color black, right_color black, left_color black,'
            'left thin, right thin, top thin, bottom thin;'
        )
        format2 = xlwt.easyxf('align:horiz center')
        format3 = xlwt.easyxf('align:horiz center;font:color black, height 300,bold True')

        header_row = 0
        sheet.write_merge(header_row, header_row, 0, 17, "Employee Report", format3)

        header_row += 1

        headers = ["Employee ID", "Government ID", "Annual Leave Balance", "Annual Leave Type", "Employee Name",
                   "Basic Salary (RMB)", "Allowances & Benefits", "Gender", "Department", "Location",
                   "Job Position", "Manager", "Nationality", "Start Date", "Work Permit Expiration Date",
                   "Last Salary Increment Date", "Shift Table", "Allowance/Benefits"]

        for col, header in enumerate(headers):
            sheet.write(header_row, col, header, format1)

        row = header_row + 1

        employees = self.env['hr.employee'].search([
        ('create_date', '>=', self.starting_date),
        ('create_date', '<=', self.ending_date)
        ])

        if self.hr_employee_ids:
            employees = employees.filtered(lambda e: e.id in self.hr_employee_ids.ids)

        time_offs = self.env['hr.leave'].search([
            ('employee_id', 'in', self.hr_employee_ids.ids)
        ])

        for employee in employees:
            
            employee_time_offs = time_offs.filtered(lambda t: t.employee_id == employee)

            sheet.write(row, 0, employee.employee_id, format1)
            sheet.write(row, 1, employee.identification_id or " ", format1)
            sheet.write(row, 2, employee.remaining_leaves if employee.remaining_leaves else " ", format1)
            leave_names = ", ".join([str(name) for name in employee_time_offs.mapped('name') if name]) if employee_time_offs else " "
            sheet.write(row, 3, leave_names, format1)
            sheet.write(row, 4, employee.name, format1)
            sheet.write(row, 5, employee.contract_id.wage if employee.contract_id else " ", format1)
            sheet.write(row, 6, "",format1)
            sheet.write(row, 7, employee.gender or " ", format1)
            sheet.write(row, 8, employee.department_id.name if employee.department_id else " ", format1)
            sheet.write(row, 9, employee.work_location_id.name if employee.work_location_id else " ", format1)
            sheet.write(row, 10, employee.job_id.name if employee.job_id else " ", format1)
            sheet.write(row, 11, employee.parent_id.employee_id if employee.parent_id else " ", format1)
            sheet.write(row, 12, employee.country_id.name if employee.country_id else " ", format1)
            sheet.write(row, 13, employee.contract_id.date_start.strftime('%d/%m/%Y') if employee.contract_id and employee.contract_id.date_start else " ", format1)
            sheet.write(row, 14, "",format1)
            sheet.write(row, 15, "",format1)
            sheet.write(row, 16, employee.resource_calendar_id.name if employee.resource_calendar_id else " ", format1)
            sheet.write(row, 17, "",format1)
            row += 1

        stream = BytesIO()
        workbook.save(stream)
        out = base64.encodebytes(stream.getvalue())
        excel_id = self.env['custom.excel.class'].create({
            "datas_fname": filename,
            "file_name": out,
        })
        stream.close()

        return {
            "res_id": excel_id.id,
            "name": "Employee Report",
            "view_mode": "form",
            "res_model": "custom.excel.class",
            "view_id": False,
            "type": "ir.actions.act_window",
            "target": 'new',
        }

    def _validate_dates(self):
        if self.starting_date > self.ending_date:
            raise ValidationError(_("Invalid DATE selection; please select a proper date range."))
