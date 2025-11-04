from odoo import api, models, fields, _
from odoo.exceptions import ValidationError, AccessError


class PaymentTerm(models.Model):
    _inherit = "account.payment.term"

    def _get_payment_type_selection(self):
        return [
            ("01", _("Counted")),
            ("02", _("Credit")),
        ]

    payment_type = fields.Selection(
        string="Payment Type",
        help="Payment type to client according days of payment term",
        selection="_get_payment_type_selection",
        compute="_compute_paymentType",
        store=True,
        readonly=True,
    )

    payment_type_name = fields.Char(
        store=True,
        readonly=True,
    )

    @api.depends("line_ids")
    def _compute_paymentType(self):
        for term in self:
            if any(line.nb_days > 0 for line in term.line_ids):
                term.payment_type = "02"  # Credit
                term.payment_type_name = "credit"
            else:
                term.payment_type = "01"  # Counted
                term.payment_type_name = "counted"
