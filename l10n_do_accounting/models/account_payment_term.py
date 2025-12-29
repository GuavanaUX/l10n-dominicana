from odoo import api, models, fields, _
from odoo.exceptions import ValidationError, AccessError
from odoo.tools.float_utils import float_compare


class PaymentTerm(models.Model):
    _inherit = "account.payment.term"

    payment_type = fields.Selection(
        selection=[
            ("01", _("Counted")),
            ("02", _("Credit")),
        ],
        string="Payment Type",
        help="Payment type according to payment term definition",
        compute="_compute_payment_type",
        store=True,
        readonly=True,
    )

    @api.depends(
        "line_ids.nb_days",
        "line_ids.value_amount",
        "line_ids.delay_type",
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

            term.payment_type = "01" if all_lines_counted else "02"
