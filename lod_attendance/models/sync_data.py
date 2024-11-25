# -*- coding: utf-8 -*-

import logging
from odoo import api, fields, models, sql_db, _


_logger = logging.getLogger(__name__)


# class FingerPrint(models.Model):
#     _name = 'lod.iclock.transaction'
#     _description = 'Connect Fingerprint'



class TestConnectFingerPrint(models.Model):
    _name = 'lod.connection.db.fingerprint'
    _description = 'Connection Fingerprint'

    name = fields.Char('Name')
    db_name = fields.Char('Database Name')
    db_location = fields.Selection([
        ('internal', 'Internal Database'),
        ('external', 'External Database'),
    ], string='Database Location')
    db_user = fields.Char('User')
    db_pass = fields.Char('Password')
    db_host = fields.Char('Host')
    db_port = fields.Char('Port')
    active = fields.Boolean('Active')

    @api.onchange('active')
    def _onchange_active(self):
        for rec in self:
            all_rec = rec.search([])
            all_rec.write({'active': False})
            rec.active = True


    def test_connect(self):
        try:
            # connection = psycopg2.connect(
            #     user="odoo17",
            #     password="123",
            #     host="locathost",
            #     port="5432",
            #     database="fingerprint"
            # )
            connection = sql_db.db_connect(self.db_name)
            cursor = connection.cursor()
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'message': _('Connected to external database successfully'),
                    'next': {'type': 'ir.actions.act_window_close'},
                    'sticky': False,
                    'type': 'success',
                }
            }
        except Exception as error:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'message': _(f"Error connecting to external database: {error}"),
                    'next': {'type': 'ir.actions.act_window_close'},
                    'sticky': False,
                    'type': 'warning',
                }
            }


        