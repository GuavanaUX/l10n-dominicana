from odoo import models, api


class AccountFiscalPosition(models.Model):
    _name = 'account.fiscal.type'
    _inherit = ['account.fiscal.type', 'pos.load.mixin']

    @api.model
    def _load_pos_data_domain(self, data):
        return [('active', '=', True), ('type', 'in', ('out_invoice', 'out_refund'))]

    @api.model
    def _load_pos_data_fields(self, config_id):
        return ['name', 'requires_document', 'fiscal_position_id', 'prefix', 'type']
