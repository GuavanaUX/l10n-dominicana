from odoo import models, fields, api, _
from odoo.exceptions import UserError
from odoo.osv.expression import AND
from datetime import timedelta


class PosOrder(models.Model):
    _inherit = 'pos.order'

    ncf = fields.Char(
        string='NCF',
        copy=False,
    )
    ncf_origin_out = fields.Char(
        string='Affects',
        copy=False,
    )
    ncf_expiration_date = fields.Date(
        string='NCF expiration date',
    )
    fiscal_type_id = fields.Many2one(
        string='Fiscal type',
        comodel_name='account.fiscal.type',
    )
    fiscal_sequence_id = fields.Many2one(
        string='Fiscal Sequence',
        comodel_name='account.fiscal.sequence',
        copy=False,
    )
    is_used_in_order = fields.Boolean(
        default=False
    )

    def _prepare_invoice_vals(self):
        """
        Prepare the dict of values to create the new invoice for a pos order.
        """
        invoice_vals = super(PosOrder, self)._prepare_invoice_vals()

        if self.config_id.invoice_journal_id.l10n_do_fiscal_journal:
            invoice_vals['ref'] = self.ncf
            invoice_vals['origin_out'] = self.ncf_origin_out
            invoice_vals['ncf_expiration_date'] = self.ncf_expiration_date
            invoice_vals['fiscal_type_id'] = self.fiscal_type_id.id
            invoice_vals['fiscal_sequence_id'] = self.fiscal_sequence_id.id

        return invoice_vals

    # @api.model
    # def _process_order(self, order, existing_order):
        # """
        # this part is using for eliminate cash return
        # :param pos_order:
        # :return pos_order:
        # """
        # if order['amount_return'] > 0:

        #     pos_session_obj = self.env['pos.session'].browse(
        #         order['pos_session_id']
        #     )
        #     cash_journal_id = pos_session_obj.cash_journal_id.id
        #     if not cash_journal_id:
        #         # If none, select for change one of the cash journals of the PO
        #         # This is used for example when a customer pays by credit card
        #         # an amount higher than total amount of the order and gets cash
        #         # back
        #         cash_journal = [statement.journal_id
        #                         for statement in pos_session_obj.statement_ids
        #                         if statement.journal_id.type == 'cash']
        #         if not cash_journal:
        #             raise UserError(
        #                 _("No cash statement found for this session. "
        #                   "Unable to record returned cash."))

        #         cash_journal_id = cash_journal[0].id

        #     for index, statement in enumerate(order['statement_ids']):
        #         if statement[2]['journal_id'] == cash_journal_id:
        #             order['statement_ids'][index][2]['amount'] = \
        #                 statement[2]['amount'] - order['amount_return']

        #     order['amount_return'] = 0

        # return super(PosOrder, self)._process_order(order, existing_order)

    @api.model
    def sync_from_ui(self, orders):
        pos_data = super(PosOrder, self).sync_from_ui(orders)
        order_ids = pos_data['pos.order']
        for order in self.sudo().browse([o['id'] for o in order_ids]):
            if order.config_id.invoice_journal_id.l10n_do_fiscal_journal \
                    and order.state != 'invoiced' \
                    and order.amount_total != 0 \
                    and order.ncf:

                if not order.partner_id:
                    if not order.config_id.pos_partner_id:
                        raise UserError(_('This point of sale not have default customer, please set default customer in config POS'))
                    
                    order.write({
                        'partner_id': order.config_id.pos_partner_id.id
                    })

                order._generate_pos_order_invoice()
            
        return pos_data

    def get_next_fiscal_sequence(self, fiscal_type_id, company_id, payments):
        """
        search active fiscal sequence dependent with fiscal type
        :param order:[fiscal_type_id, company_id, mode, lines,]
        :return: {ncf, expiration date, fiscal sequence}
        """
        fiscal_type = self.env['account.fiscal.type'].search([
            ('id', '=', fiscal_type_id)
        ])

        if not fiscal_type:
            raise UserError(_('Fiscal type not found'))

        for payment in payments:
            if payment.get('returned_ncf', False):
                cn_invoice = self.env['account.move'].search([
                    ('ref', '=', payment['returned_ncf']),
                    ('move_type', '=', 'out_refund'),
                    ('is_l10n_do_fiscal_invoice', '=', True),
                ])
                if cn_invoice.residual != cn_invoice.amount_total:
                    raise UserError(
                        _('This credit note (%s) has been used' % payment['returned_ncf'])
                    )

        fiscal_sequence = self.env['account.fiscal.sequence'].search([
            ('fiscal_type_id', '=', fiscal_type.id),
            ('state', '=', 'active'),
            ('company_id', '=', company_id)
        ], limit=1)

        if not fiscal_sequence:
            raise UserError(
                _(u"There is no current active NCF of {}, please create a new fiscal sequence of type {}.").format(
                    fiscal_type.name,
                    fiscal_type.name,
            ))

        return {
            'ncf': fiscal_sequence.get_fiscal_number(),
            'fiscal_sequence_id': fiscal_sequence.read()[0],
            'ncf_expiration_date': fiscal_sequence.expiration_date
        }

    def get_credit_note(self, ncf):
        """
        Get credit note
        :param ncf:
        :return:
        """
        credit_note = self.env['account.move'].search([
            ('ref', '=', ncf),
            ('move_type', '=', 'out_refund'),
            ('is_l10n_do_fiscal_invoice', '=', True),
            ('company_id', '=', self.env.company.id),
            ('state', '=', 'posted')
        ], limit=1)

        if not credit_note:
            raise UserError(_('Credit note not found'))

        return {
            'partner_id': credit_note.partner_id.id,
            'residual_amount': credit_note.amount_residual,
            'ncf': credit_note.ref,
        }

    def get_credit_notes(self, partner_id):
        """
        Get credit note
        :param partner_id:
        :return: credit notes from partner
        """
        credit_notes = self.env['account.move'].search([
            ('partner_id', '=', partner_id),
            ('move_type', '=', 'out_refund'),
            ('is_l10n_do_fiscal_invoice', '=', True),
            ('amount_residual', '>', 0.0),
            ('company_id', '=', self.env.company.id),
            ('state', '=', 'posted')
        ])

        if not credit_notes:
            raise UserError(_('This customer does not have credit notes'))

        return[{
            'id': credit_note.id,
            'label': "%s - %s %s" % (credit_note.ref, credit_note.currency_id.name, credit_note.amount_residual),
            'item':{
                'partner_id': credit_note.partner_id.id,
                'residual_amount': credit_note.amount_residual,
                'ncf': credit_note.ref,
            }} for credit_note in credit_notes]

    @api.model
    def search_paid_order_ids(self, config_id, domain, limit, offset):
        """Search for 'paid' orders that satisfy the given domain, limit and offset."""
        pos_config = self.env['pos.config'].browse(config_id)

        if pos_config.invoice_journal_id.l10n_do_fiscal_journal:
            config_ids = self.env['pos.config'].search([
                ('invoice_journal_id.l10n_do_fiscal_journal', '=', True)
            ]).ids

            custom_filters = [
                ('config_id', 'in', config_ids), 
                ('ncf', '!=', False),
                ('amount_total', '>', 0),
            ]
            if pos_config.l10n_do_type_limit_order_history == 'days':
                custom_filters.append((
                    'create_date',
                    '>=',
                    fields.Datetime.to_string(
                        fields.Datetime.now() - timedelta(days=pos_config.l10n_do_type_limit_order_history_days)
                    )
                ))

            domain = AND([domain or [], custom_filters])

        return super(PosOrder, self).search_paid_order_ids(config_id, domain, limit, offset)
