from odoo import Command, fields, models


class PosSession(models.Model):
    _inherit = 'pos.session'

    def _create_account_move(self, balancing_account=False, amount_to_balance=0, bank_payment_method_diffs=None):
        if not self.config_id.l10n_do_fiscal_journal:
            return super()._create_account_move(balancing_account, amount_to_balance, bank_payment_method_diffs)

        account_move = self.env['account.move'].create({
            'journal_id': self.config_id.journal_id.id,
            'date': fields.Date.context_today(self),
            'ref': self.name,
        })
        self.write({'move_id': account_move.id})
        self._l10n_do_post_bank_diff_moves(bank_payment_method_diffs or {})
        MoveLine = self.env['account.move.line']
        return {
            'bank_payment_method_diffs': bank_payment_method_diffs or {},
            'MoveLine': MoveLine,
            'payment_method_to_receivable_lines': {},
            'payment_to_receivable_lines': {},
            'online_payment_to_receivable_lines': {},
            'combine_inv_payment_receivable_lines': {},
            'split_inv_payment_receivable_lines': {},
            'combine_invoice_receivable_lines': {},
            'split_invoice_receivable_lines': {},
            'split_cash_receivable_lines': MoveLine,
            'split_cash_statement_lines': MoveLine,
            'combine_cash_receivable_lines': MoveLine,
            'combine_cash_statement_lines': MoveLine,
            'stock_output_lines': {},
            'pay_later_move_lines': MoveLine,
        }

    def _l10n_do_post_bank_diff_moves(self, bank_payment_method_diffs):
        """Create closing-difference account.move for each bank/card payment method.

        Uses the UNTRANSLATED ref format that report_sale_details searches:
            "Closing difference in {pm_name} ({session_name})"
        so the standard sale_details_report (Path 1) picks it up without needing
        account.payment records (which cause double-counting in that report).
        """
        for pm_id, diff_amount in bank_payment_method_diffs.items():
            if self.currency_id.compare_amounts(diff_amount, 0) == 0:
                continue
            payment_method = self.env['pos.payment.method'].browse(pm_id)
            journal = payment_method.journal_id
            outstanding_account = (
                payment_method.outstanding_account_id
                or journal._get_journal_inbound_outstanding_payment_accounts()[:1]
                or journal.default_account_id
            )
            diff_vals = self._get_diff_vals(pm_id, diff_amount, outstanding_account)
            if not diff_vals:
                continue
            source_vals, dest_vals = diff_vals
            diff_move = self.env['account.move'].create({
                'journal_id': journal.id,
                'date': fields.Date.context_today(self),
                # Exact English format the standard report_sale_details searches (untranslated)
                'ref': "Closing difference in %s (%s)" % (payment_method.name, self.name),
                'line_ids': [Command.create(source_vals), Command.create(dest_vals)],
            })
            diff_move._post()

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
        return super()._create_bank_payment_moves(data)

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
