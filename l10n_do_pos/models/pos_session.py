from odoo import models


class PosSession(models.Model):
    _inherit = 'pos.session'

    def _create_invoice_receivable_lines(self, data):
        if self.config_id.l10n_do_fiscal_journal:
            data.update({
                'combine_invoice_receivable_lines': {},
                'split_invoice_receivable_lines': {},
            })
            return data
        return super(PosSession, self)._create_invoice_receivable_lines(data)

    def _create_bank_payment_moves(self, data):
        if self.config_id.l10n_do_fiscal_journal:
            data.update({
                'payment_method_to_receivable_lines': {},
                'payment_to_receivable_lines': {},
                'online_payment_to_receivable_lines': {},
            })
            return data
        return super(PosSession, self)._create_bank_payment_moves(data)

    def _create_cash_statement_lines_and_cash_move_lines(self, data):
        if self.config_id.l10n_do_fiscal_journal:
            AccountMoveLine = self.env['account.move.line']
            data.update({
                'split_cash_receivable_lines': AccountMoveLine,
                'split_cash_statement_lines': AccountMoveLine,
                'combine_cash_receivable_lines': AccountMoveLine,
                'combine_cash_statement_lines': AccountMoveLine
            })
            return data
        return super(PosSession, self)._create_cash_statement_lines_and_cash_move_lines(data)

    def _load_pos_data_models(self, config_id):
        result = super()._load_pos_data_models(config_id)
        result.append('account.fiscal.type')
        return result
