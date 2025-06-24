from odoo import models, fields, api

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    rnc_data_fallback = fields.Boolean(string="RNC Data Fallback", default=False)

    def set_values(self):
        super(ResConfigSettings, self).set_values()
        self.env['ir.config_parameter'].set_param('l10n_do_rnc.rnc_data_fallback', self.rnc_data_fallback)

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        res['rnc_data_fallback'] = self.env['ir.config_parameter'].get_param('l10n_do_rnc.rnc_data_fallback')
        return res