from odoo import models


class PosPayment(models.Model):
    _inherit = 'pos.payment'

    def _create_payment_moves(self, is_reverse=False):
        """Standard flow handles every payment method except credit notes:
        `is_credit_note` payment methods have no journal_id (enforced by
        `pos.payment.method._check_is_credit_note`) and settle against an
        already-posted NCF credit note instead of creating a new move.
        """
        credit_notes = self.filtered(lambda p: p.payment_method_id.is_credit_note and p.name)
        other_payments = self - credit_notes

        result = self.env['account.move']
        credit_line_ids = []
        if other_payments:
            result = super(PosPayment, other_payments)._create_payment_moves(is_reverse)
            credit_line_ids += result._context.get('credit_line_ids', [])

        for credit_note in credit_notes:
            account_move_credit_note = self.env['account.move'].search([
                ('partner_id', '=', credit_note.partner_id.id),
                ('ref', '=', credit_note.name),
                ('move_type', '=', 'out_refund'),
                ('is_l10n_do_fiscal_invoice', '=', True),
                ('company_id', '=', self.env.company.id),
                ('state', '=', 'posted')
            ], limit=1)

            if account_move_credit_note and credit_note.amount > 0:
                account_move_credit_note.write({
                    'pos_payment_ids': credit_note.ids,
                })
                credit_note.write({
                    'account_move_id': account_move_credit_note.id
                })
                result |= account_move_credit_note
                credit_line_ids += account_move_credit_note.line_ids.filtered(lambda l: l.credit > 0).ids

        return result.with_context(credit_line_ids=credit_line_ids)