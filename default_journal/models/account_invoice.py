from odoo import models, fields, api

class AccountMove(models.Model):
    _inherit = "account.move"

    @api.model
    def _search_default_journal(self):
        res = super(AccountMove, self)._search_default_journal()
        current_user = self.env['res.users'].search([('id','=',self._uid)])
        current_user_sale_default_journal = current_user.sale_default_journal_id.id
        if(current_user_sale_default_journal and self._context.get('default_move_type')=='out_invoice'):
            default_journal = self.env['account.journal'].search([('id','=',current_user_sale_default_journal)])
            return default_journal
        else:
            return res

    journal_id = fields.Many2one('account.journal',
        required=True, readonly=True, states={'draft': [('readonly', False)]},
        default=_search_default_journal,
        domain="[('type', 'in', {'out_invoice': ['sale'], 'out_refund': ['sale'], 'in_refund': ['purchase'], 'in_invoice': ['purchase']}.get(move_type, [])), ('company_id', '=', company_id)]")
