from odoo import models, fields, api

class AccountJournal(models.Model):
    _inherit = 'account.journal'
    _name = 'account.journal'

    user_id = fields.One2many('res.users', 'sale_default_journal_id')
