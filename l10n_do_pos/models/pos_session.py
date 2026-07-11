from odoo import models


class PosSession(models.Model):
    _inherit = 'pos.session'

    def _load_pos_data_models(self, config_id):
        result = super()._load_pos_data_models(config_id)
        result.append('account.fiscal.type')
        return result
