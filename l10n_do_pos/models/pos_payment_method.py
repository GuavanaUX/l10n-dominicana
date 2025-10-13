from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class PosPaymentMethod(models.Model):
    _inherit = 'pos.payment.method'

    is_credit_note = fields.Boolean(
        string='Credit Note',
    )

    @api.constrains('is_credit_note')
    def _check_is_credit_note(self):
        for record in self:
            if record.is_credit_note:
                if not record.split_transactions:
                    raise ValidationError(
                        _('Identify customer must be true if is credit note is true.'))

                if record.journal_id:
                    raise ValidationError(
                        _('Journal must be empty if is credit note is true.'))

    @api.model
    def _load_pos_data_fields(self, config_id):
        result = super()._load_pos_data_fields(config_id)
        result.append('is_credit_note')
        return result
