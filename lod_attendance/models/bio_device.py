# -*- coding: utf-8 -*-

import logging
from odoo import api, fields, models, sql_db, _
import datetime
from datetime import datetime, timezone, timedelta
from odoo.addons.base.models.res_partner import _tz_get
from odoo import http
from odoo.http import request, Response
import psycopg2

_logger = logging.getLogger(__name__)

class BiometricDevice(models.Model):
    _name = 'lod.biometric.device'
    _description = 'Biometric Device'

    name = fields.Char('Name')
    device_id = fields.Integer('Device ID')
    serial_number = fields.Char('Serial Number')
    device_ip = fields.Char('Device IP')
    real_ip = fields.Char('Real IP')
    time_zone = fields.Selection(_tz_get, string='Timezone')
    transaction_count = fields.Integer('Transaction Count')
    user_count = fields.Integer('User Count')
    fp_count = fields.Integer('FP Count')
    area_id = fields.Many2one('employee.area', string='Area')
    port = fields.Boolean('Port')
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company, readonly=True)
    # active = fields.Boolean('Active')

    def action_select_boimetric_device(self):
        try:
            db = self.env['lod.connection.db.fingerprint'].search([('active','=',True)], limit=1)
            connection = sql_db.db_connect(db.db_name)
            cursor = connection.cursor()
            # query = f"SELECT id,sn,ip_address,real_ip,terminal_tz,user_count,fp_count,area_id 
            #           FROM iclock_terminal
            #           WHERE ip_address NOT IN ()"
            query = f"SELECT id,sn,ip_address,real_ip,terminal_tz,transaction_count,terminal_name,user_count,fp_count,area_id FROM iclock_terminal"
            # [{'id': 5, 'sn': 'CQQB234760047', 'ip_address': '10.150.12.163', 'real_ip': '172.30.255.1', 'terminal_tz': 8, 'user_count': 1427, 'fp_count': 2536, 'area_id': 2}]
            _logger.info("====query===== %s",query)
            cursor.execute(query)
            data = cursor.dictfetchall()
            _logger.info("====data===== %s",data)
            if data:
                device_ids = self.search([])
                ip_address = []
                for device in device_ids: ip_address.append(device.device_ip)
                _logger.info("====ip_address===== %s",ip_address)

                for val in data:
                    if val.get('ip_address') not in ip_address or ip_address == []:
                        _logger.info("====ip_address'===== %s",val.get('ip_address'))
                        vals = {
                            'name':val.get('terminal_name'),
                            'device_id':val.get('id'),
                            'serial_number':val.get('sn'),
                            'device_ip':val.get('ip_address'),
                            'real_ip':val.get('real_ip'),
                            # 'time_zone':val.get('terminal_tz'),
                            'transaction_count':val.get('transaction_count'),
                            'user_count':val.get('user_count'),
                            'fp_count':val.get('fp_count'),
                            # 'area_id':val.get('area_id'),
                        }
                        _logger.info("====vals===== %s",vals)
                        bio_device_id = self.sudo().create(vals)
                        _logger.info("====bio_device_id===== %s",bio_device_id)


                cursor.close()

                return {
                    'name': 'Biometric Device',
                    'res_model': self._name,
                    'type': 'ir.actions.act_window',
                    'views': [[False, "list"], [False, "form"]],
                    'view_mode': 'list, form',
                }
            else:
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'message': _('No have device'),
                        'next': {'type': 'ir.actions.act_window_close'},
                        'sticky': False,
                        'type': 'warning',
                    }
                }

        except Exception as error:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'message': _(f"Error: {error}"),
                    'next': {'type': 'ir.actions.act_window_close'},
                    'sticky': False,
                    'type': 'warning',
                }
            }


    def action_download_attendance(self):
        attend_obj = self.env['lod.attendance.log']
        try:
            db = self.env['lod.connection.db.fingerprint'].search([('active','=',True)], limit=1)
            attend_obj_ids = attend_obj.search([])
            log_ids = []
            for attend in attend_obj_ids: log_ids.append(attend.log_id)
            if log_ids == []:
                log_ids = ''
            else:
                log_ids = f'WHERE id NOT IN {tuple(log_ids)}'
            _logger.info("====log_ids===== %s",log_ids)
            connection = sql_db.db_connect(db.db_name)
            cursor = connection.cursor()
            query = f"SELECT id,emp_code,punch_time,punch_state,area_alias,emp_id,terminal_id FROM iclock_transaction {log_ids}"
            _logger.info("====query===== %s",query)
            cursor.execute(query)
            data = cursor.dictfetchall()
            if data:
                # _logger.info("====first data===== %s",data)
                count_record = 0
                for val in data:
                    employee_id = self.env['hr.employee'].search([('employee_id','=',val.get('emp_code'))])
                    _logger.info("====employee_id===== %s",employee_id)
                    dt = val.get('punch_time') - timedelta(hours=7)
                    # punch_hour  = dt.tzinfo.utcoffset(None).total_seconds() / 3600
                    # dt = dt + timedelta(hours=int(punch_hour))
                    punch_time = dt.strftime('%Y-%m-%d %H:%M:%S')

                    values = {
                        'log_id':val.get('id'),
                        'employee_id': employee_id.id if employee_id else False,
                        # 'status':val.get('sn'),
                        'punching_time':punch_time,
                        'punch_state':val.get('punch_state'),
                        # 'device_ip':val.get('ip_address'),
                        'area_name':val.get('area_alias'),
                        'device':val.get('terminal_id'),
                    }
                    _logger.info("====Values===== %s",values)
                    attendance = attend_obj.sudo().create(values)
                    _logger.info("====attendance===== %s",attendance)
                    count_record += 1
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'message': _(f'Download Success {count_record} Record'),
                        'next': {'type': 'ir.actions.act_window_close'},
                        'sticky': False,
                        'type': 'success',
                    }
                }
            else:
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'message': _('No have Data'),
                        'next': {'type': 'ir.actions.act_window_close'},
                        'sticky': False,
                        'type': 'warning',
                    }
                }
               
              
            _logger.info("====data===== %s",data)
            cursor.close()

        except Exception as e:
            _logger.info(f"===Error=== {e}")

    # def download_attendance_log_new(self):
    #     devices = self.env["biometric.config"].search([])
    #     for device in devices:
    #         device.download_attendance_log()
