# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

class HrReport(models.AbstractModel):
    _name = 'report.lod_hr_report.report_one_set'
    _description = 'HR Report'

    @api.model
    def _get_report_values(self, docids, data=None):
        if not data:
            raise ValidationError(_("No data provided for the report."))

        employee_ids = data['form_data'].get('hr_employee_ids', [])
        department_ids = data['form_data'].get('hr_department_ids', [])
        start_date = data['form_data'].get('starting_date')
        end_date = data['form_data'].get('ending_date')

        if not (employee_ids or department_ids):
            raise ValidationError(_("Invalid field selection; please select at least one employee or department."))

        employee_info_list = []
    
        if employee_ids:
            employee_info_list.extend(self._get_employee_attendance(employee_ids, start_date, end_date))

        if department_ids:
            employee_info_list.extend(self._get_department_attendance(department_ids, start_date, end_date))

        return {
            'doc_ids': docids,
            'doc_model': 'hr.employee',
            'emp_name': employee_info_list,
            'data': data,
        }

    def _get_employee_attendance(self, employee_ids, start_date, end_date):
        employee_info_list = []
        employees = self.env['hr.employee'].search([
            # ('employee_id', '=', employee_ids),
            ('create_date', '>=', start_date),
            ('create_date', '<=', end_date)
        ])
        for employee in employees:
            if not employee.exists():
                continue
            attendance_records = self._get_attendance_records(employee.id, start_date, end_date)

            employee_info_list.append({
                'emp_name': employee.name,
                'gender': employee.gender if employee.gender else 'N/A',
                'identification_id ': employee.identification_id if employee.identification_id else 'N/A',
                'job': employee.job_id.name if employee.job_id else 'N/A',
                'manager': employee.parent_id.name if employee.parent_id else 'N/A',
                'department': employee.department_id.name if employee.department_id else 'N/A',
                'vals': attendance_records,
                'report_department': False,
            })
        return employee_info_list

    def _get_department_attendance(self, department_ids, start_date, end_date):
        employee_info_list = []
        for department in self.env['hr.department'].browse(department_ids):
            if not department.exists():
                continue
            for employee in department.member_ids:
                attendance_records = self._get_attendance_records(employee.id, start_date, end_date)

                employee_info_list.append({
                    'emp_name': employee.name,
                    'manager': employee.parent_id.name if employee.parent_id else 'N/A',
                    'department': employee.department_id.name if employee.department_id else 'N/A',
                    'vals': attendance_records,
                    'report_department': department.name,
                })
        return employee_info_list

    def _get_attendance_records(self, employee_id, start_date, end_date):
        attendance_records = []
        attendance_obj = self.env['hr.attendance'].search([
            ('employee_id', '=', employee_id),
            ('check_in', '>=', start_date),
            ('check_out', '<=', end_date)
        ])
        for attendance in attendance_obj:
            attendance_records.append({
                'employee': attendance.employee_id.name,
                'department': attendance.employee_id.department_id.name if attendance.employee_id.department_id else 'N/A',
                'job': attendance.employee_id.job_id.name if attendance.employee_id.job_id else 'N/A',
                'manager': attendance.employee_id.parent_id.name if attendance.employee_id.parent_id else 'N/A',
                'gender': attendance.employee_id.gender if attendance.employee_id.gender else 'N/A',
                'check_in': attendance.check_in,
                'check_out': attendance.check_out,
                'work_h': round(attendance.worked_hours, 2),
            })
        return attendance_records
