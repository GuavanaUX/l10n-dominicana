from odoo import fields, models


class AccountTax(models.Model):
    _inherit = "account.tax"

    tax_code = fields.Char(string="Tax Code", readonly=True, help="Test", copy=True)

    origin = fields.Char(string="Origin", readonly=True, help="Test", copy=True)
