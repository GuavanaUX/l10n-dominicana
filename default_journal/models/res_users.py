from odoo import models, fields


class Users(models.Model):
    _inherit = 'res.users'

    sale_default_journal_id = fields.Many2one('account.journal','user_id', domain="[('type', '=', 'sale')]")
