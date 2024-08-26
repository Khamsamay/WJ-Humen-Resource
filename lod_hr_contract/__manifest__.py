# Copyright 2018 Brainbean Apps (https://brainbeanapps.com)
# Copyright 2020 CorporateHub (https://corporatehub.eu)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "LOD HR Contract",
    "version": "17.0.1.0.0",
    "category": "Human Resources",
    "website": "https://github.com/OCA/hr",
    "author": "CorporateHub, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "installable": True,
    "summary": "Employee's contract",
    "depends": ["hr_contract","hr_payroll","base"],
    "data": [
        "views/hr_contract.xml",
        # "views/hr_payroll.xml",
        "views/hr_employee.xml",
             ],
}
