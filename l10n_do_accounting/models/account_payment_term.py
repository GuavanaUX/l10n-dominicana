from odoo import api, models, fields, _
from odoo.exceptions import ValidationError, AccessError
from odoo.tools.float_utils import float_compare


class PaymentTerm(models.Model):
    _inherit = "account.payment.term"

    def _get_payment_type_selection(self):
        return [
            (1, _("Counted")),
            (2, _("Credit")),
        ]

    payment_type = fields.Integer(
        string="Payment Type",
        help="Payment type to client according days of payment term",
        selection="_get_payment_type_selection",
        compute="_compute_payment_type",
        store=True,
        readonly=True,
    )

    payment_type_name = fields.Char(
        store=True,
        readonly=True,
    )

    @api.depends(
        "line_ids.nb_days", "line_ids.value_amount", "line_ids.delay_type", "line_ids"
    )
    def _compute_payment_type(self):
        for term in self:

            def line_is_counted(line):
                delay = line.delay_type or ""
                value = float(line.value_amount or 0.0)
                nb_days = int(line.nb_days or 0)

                return (
                    delay == "days_after"
                    and nb_days == 0
                    and float_compare(value, 100.0, precision_digits=6) == 0
                )

            all_lines_counted = bool(term.line_ids) and all(
                line_is_counted(line) for line in term.line_ids
            )

            if all_lines_counted:
                term.payment_type = 1
                term.payment_type_name = "counted"
            else:
                term.payment_type = 2
                term.payment_type_name = "credit"
