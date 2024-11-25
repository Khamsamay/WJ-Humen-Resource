# -*- coding: utf-8 -*-

{
    'name': 'Fingerprint',
    'version': '17.0',
    'author': 'Laooddoo',
    'category': 'Insurance',
    'description': 'Fingerprint',
    'summary': 'Fingerprint',
    'license': 'LGPL-3',
    'sequence': 0,
    'summary': """""",
    'depends': ['hr_attendance'],
    'data': [
        'security/ir.model.access.csv',
        'views/employee_area_view.xml',
        'views/biometric_log_view.xml',
        'views/biometric_device_view.xml',
        'views/test_connect_db_view.xml',
        'views/menu_item.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    # 'images': ['static/description/banner.png'],
}
