# -*- coding: utf-8 -*-

import logging
from odoo import api, fields, models, sql_db, _
from odoo import http
from odoo.http import request, Response
import psycopg2

_logger = logging.getLogger(__name__)

# class HrEmployee(models.Model):
#     _inherit = 'hr.employee'

#     @api.model_create_multi
#     def create(self, vals):
#         emp = super(HrEmployee, self).create(vals)
#         if vals.get("company_id") and not vals.get("currency_id"):
#             company = self.env["res.company"].browse(vals.get("company_id"))
#             vals["currency_id"] = company.currency_id.id
#         return emp
    
#     def write(self, vals):
#         res = super(AttendanceDeviceUser, self).write(vals)
#         for r in self:
#             if r.env.context.get('write_new_data_user_to_device', False):
#                 r.setUser()
#         return res

# class PersonelEmployeeArea(models.Model):
#     _name = 'employee.personel.area'
#     _description = 'Personel Employee Area'

#     name = fields.Char('Name')

class EmployeeArea(models.Model):
    _name = 'employee.area'
    _description = 'Employee Area'
    _parent_store = True
    _rec_name = 'area_name'

    area_name = fields.Char('Area Name', required=True)
    area_code = fields.Char('Area Code', required=True)
    is_default = fields.Boolean('is_default')
    parent_id = fields.Many2one('employee.area', 'Parent Area', index=True, ondelete='cascade')
    parent_path = fields.Char(index=True, unaccent=False)

    @api.model_create_multi
    def create(self, vals):
        area = super().create(vals)
        try:
            db = self.env['lod.connection.db.fingerprint'].search([('active','=',True)], limit=1)
            connection = sql_db.db_connect(db.db_name)
            cursor = connection.cursor()
            _logger.info("====vals===== %s",vals)
            _logger.info("====area_code===== %s",vals[0].get('area_code'))
            _logger.info("====area_name===== %s",vals[0].get('area_name'))
            _logger.info("====is_default===== %s",vals[0].get('is_default'))
            _logger.info("====parent_id===== %s",vals[0].get('parent_id'))
            area_code = vals[0]["area_code"] if vals[0]["area_code"] else ''
            area_name = vals[0]["area_name"] if vals[0]["area_name"] else ''
            is_default = vals[0]["is_default"] if vals[0]["is_default"] else False
            parent_id = vals[0]["parent_id"].id if vals[0]["parent_id"] else 'null'
            _logger.info("====area_code vals===== %s",vals[0].get('area_code'))
            _logger.info("====area_name vals===== %s",vals[0].get('area_name'))
            _logger.info("====is_default vals===== %s",vals[0].get('is_default'))
            _logger.info("====parent_id vals===== %s",vals[0].get('parent_id'))

            query = f"INSERT INTO personnel_area (area_code,area_name,is_default,parent_area_id) VALUES('{self.area_code}','{self.area_name}','{self.is_default}',{parent_id})"
            _logger.info("====query===== %s",query)
            cursor.execute(query)
            cursor.commit()
            # data = cursor.dictfetchall()
            # _logger.info("====data===== %s",data)
            # _logger.info("====Self===== %s",self)
            # return {
            #     'type': 'ir.actions.client',
            #     'tag': 'display_notification',
            #     'params': {
            #         'message': _('Connected to external database successfully'),
            #         'next': {'type': 'ir.actions.act_window_close'},
            #         'sticky': False,
            #         'type': 'success',
            #     }
            # }
            cursor.close()
        except Exception as error:
            _logger.info("====Error:===== %s",error)
            # return {
            #     'type': 'ir.actions.client',
            #     'tag': 'display_notification',
            #     'params': {
            #         'message': _(f"Error connecting to external database: {error}"),
            #         'next': {'type': 'ir.actions.act_window_close'},
            #         'sticky': False,
            #         'type': 'warning',
            #     }
            # }

        return area
    
    # def massage_log(self, color, message):
    #     _logger.info("====message===== %s",message)
    #     self.message_post(body=f'<span style="color:{color};font-weight: bold"> {message} <span>')


        
    # def write(self, vals):
    #     res = super(AttendanceDeviceUser, self).write(vals)
    #     for r in self:
    #         if r.env.context.get('write_new_data_user_to_device', False):
    #             r.setUser()
    #     return res
