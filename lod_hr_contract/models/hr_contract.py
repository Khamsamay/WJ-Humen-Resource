from odoo import api, fields, models

class HrContract(models.Model):
    _inherit = "hr.contract"

    currency_id = fields.Many2one(
        "res.currency",
        readonly=False,
        required=True,
        default=lambda self: self._get_default_currency_id(),
        tracking=True,
    )

    is_exchange = fields.Boolean(string='Apply Manual Currency', help='Enable to display rate field')
    rate_lak = fields.Float(string="Rate LAK", digits=(16, 8), readonly=False, store=True, default=lambda self: self.env['res.currency'].search([('name', '=', 'LAK')], limit=1).inverse_rate)
    rate_thb = fields.Float(string="Rate THB", digits=(16, 8), readonly=False, store=True, default=lambda self: self.env['res.currency'].search([('name', '=', 'THB')], limit=1).inverse_rate)
    rate_usd = fields.Float(string="Rate USD", digits=(16, 8), readonly=False, store=True, default=lambda self: self.env['res.currency'].search([('name', '=', 'USD')], limit=1).inverse_rate)

    amount = fields.Float(
        string='Amount',
        help='Employee\'s contract amount per period',
        compute='_compute_amount_totals', readonly=False, store=True,
    )

    @api.depends('currency_id', 'rate_usd', 'rate_thb', 'rate_lak', 'amount')
    def _compute_amount_totals(self):
        for rec in self:
            if rec.currency_id:
                if rec.currency_id.name == 'THB': 
                    rec.amount = rec.wage
                    rec.amount = (rec.wage * rec.rate_thb) / rec.rate_usd if rec.rate_usd else 0.0
                    rec.amount = (rec.wage * rec.rate_thb) if rec.rate_thb else 0.0
                elif rec.currency_id.name == 'USD':    
                    rec.amount = rec.wage
                    rec.amount = (rec.wage * rec.rate_usd) / rec.rate_thb if rec.rate_thb else 0.0
                    rec.amount = rec.wage * rec.rate_usd if rec.rate_usd else 0.0
                elif rec.currency_id.name == 'LAK':
                    rec.amount = rec.wage
                    rec.amount = rec.wage / rec.rate_thb if rec.rate_thb else 0.0
                    rec.amount = rec.wage / rec.rate_usd if rec.rate_usd else 0.0
            else:
                rec.amount = 0.0
                rec.amount = 0.0
                rec.amount = 0.0

    def _get_default_currency_id(self):
        return self.company_id.currency_id.id or self.env.company.currency_id.id

    @api.model
    def create(self, vals):
        if vals.get("company_id") and not vals.get("currency_id"):
            company = self.env["res.company"].browse(vals.get("company_id"))
            vals["currency_id"] = company.currency_id.id
        return super().create(vals)
