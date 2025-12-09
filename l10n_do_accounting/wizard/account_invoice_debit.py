from odoo import models, fields, api, _
from odoo.exceptions import UserError, AccessError


class AccountDebitNote(models.TransientModel):
    _inherit = "account.debit.note"

    # @api.model
    # def _get_l10n_do_debit_type_selection(self):
    #     selection = [
    #         ("percentage", _("Percentage")),
    #         ("fixed_amount", _("Amount")),
    #     ]
    #     return selection

    @api.model
    def _get_l10n_do_default_debit_type(self):
        return "percentage"

    @api.model
    def _get_l10n_do_debit_action_selection(self):
        return [
            ("draft_debit", _("Draft debit")),
            ("apply_debit", _("Apply debit")),
        ]

    l10n_latam_country_code = fields.Char(
        default=lambda self: self.env.company.country_code,
        help="Technical field used to hide/show fields regarding the localization",
    )

    # l10n_do_debit_type = fields.Selection(
    #     selection=_get_l10n_do_debit_type_selection,
    #     default=_get_l10n_do_default_debit_type,
    #     string="Debit Type",
    # )

    l10n_do_debit_action = fields.Selection(
        selection=_get_l10n_do_debit_action_selection,
        default="draft_debit",
        string="Action",
    )

    l10n_do_percentage = fields.Float(
        help="Debit Note based on origin invoice percentage",
        string="Percentage",
    )

    l10n_do_amount = fields.Float(
        help="Debit Note based fixed amount",
        string="Amount",
    )

    l10n_do_account_id = fields.Many2one(
        "account.account",
        string="Account",
        domain=[("deprecated", "=", False)],
    )

    l10n_latam_document_number = fields.Char(
        string="Document Number",
    )

    # is_ecf_invoice = fields.Boolean(
    #     string="Is Electronic Invoice",
    # )

    refund_ref = fields.Char(string="NCF")

    ncf_expiration_date = fields.Date(
        string="Valid until",
    )

    l10n_latam_use_documents = fields.Boolean("Use Documents", readonly=True)

    l10n_latam_document_type_id = fields.Many2one(
        "account.fiscal.type", "Document Type", ondelete="cascade"
    )

    @api.model
    def default_get(self, fields):
        res = super(AccountDebitNote, self).default_get(fields)

        move_ids = (
            self.env["account.move"].browse(self.env.context["active_ids"])
            if self.env.context.get("active_model") == "account.move"
            else self.env["account.move"]
        )

        if not move_ids:
            raise UserError(_("No invoice found for this operation"))

        move_ids_use_document = move_ids.filtered(
            lambda move: move.is_l10n_do_fiscal_invoice
            and move.company_id.country_code == "DO"
        )
        if move_ids_use_document and not self.env.user.has_group(
            "l10n_do_accounting.group_l10n_do_debit_note"
        ):
            raise AccessError(_("You are not allowed to issue Debit Notes"))

        journal = move_ids[0].journal_id
        res["l10n_do_account_id"] = journal.default_account_id.id
        res["l10n_latam_use_documents"] = journal.l10n_do_fiscal_journal

        if len(move_ids_use_document) > 1:
            raise UserError(
                _("You cannot create Debit Notes from multiple documents at a time.")
            )
        # else:
        #     res["is_ecf_invoice"] = (
        #         move_ids_use_document and move_ids_use_document[0].is_ecf_invoice
        #     )

        return res

    @api.onchange("move_ids")
    def _onchange_move_id(self):
        if (
            self.move_ids
            and self.move_ids[0].is_l10n_do_fiscal_invoice
            and self.l10n_latam_country_code == "DO"
        ):
            move_id = self.move_ids[0]
            move_type = "out_debit" if move_id.is_sale_document() else "in_debit"
            move = (
                self.env["account.move"]
                .with_context(internal_type="debit_note")
                .new(
                    {
                        "partner_id": move_id.partner_id.id,
                        "move_type": move_type,
                        "journal_id": move_id.journal_id.id,
                    }
                )
            )

            document_type = self.env["account.fiscal.type"].search(
                [
                    ("type", "=", "out_debit"),
                ],
                limit=1,
            )

            if not document_type:
                raise UserError(_("No document type found with type 'out_debit'."))

            domain_ids = [document_type.id]
            self.l10n_latam_document_type_id = document_type.id
            return {
                "domain": {
                    "l10n_latam_document_type_id": [
                        (
                            "id",
                            "in",
                            domain_ids,
                        )
                    ]
                }
            }

    def _prepare_default_values(self, move):
        res = super(AccountDebitNote, self)._prepare_default_values(move)

        if self.l10n_latam_country_code == "DO" and move.is_l10n_do_fiscal_invoice:
            res.update(
                dict(
                    ref=self.refund_ref,
                    origin_out=move.ref,
                    expense_type=move.expense_type,
                    income_type=move.income_type,
                    ncf_expiration_date=self.ncf_expiration_date,
                    fiscal_type_id=False,
                    is_debit_note=True,
                )
            )

        return res

    def create_debit(self):
        action = super(AccountDebitNote, self).create_debit()
        if self.l10n_do_debit_action == "apply_debit":
            # Post Debit Note
            move_id = self.env["account.move"].browse(action.get("res_id", False))
            move_id._post()

        return action
