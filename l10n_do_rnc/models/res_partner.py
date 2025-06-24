from odoo import models, api, _
from odoo.exceptions import UserError, ValidationError
from odoo.addons.base_vat.models.res_partner import _ref_vat

if _ref_vat:
    _ref_vat.update({
        'do': _("Example: '22400504056' or '133195593' (format: 9 digits for RNC or 11 Digits for Cedula, all numbers.)"),
    })

import logging
import json
import re
_logger = logging.getLogger(__name__)

try:
    from stdnum.do import rnc, cedula
except (ImportError, IOError) as err:
    _logger.debug(str(err))

class Partner(models.Model):
    _inherit = 'res.partner'

    @api.model_create_multi
    def create(self, vals_list):
        for val in vals_list:
            is_from_vat = val.get('vat', False)

            rnc = val.get('vat', '') if is_from_vat else val.get('name', '')
            rnc = rnc.replace('-', '') if rnc else rnc

            if val.get('country_id', False) == self.env.ref('base.do').id and rnc and rnc.isdigit():
                contact_exist = self.env['res.partner'].search([('vat', '=', rnc)], limit=1)
                
                if contact_exist:
                    raise UserError(_('The contact %s already exists with the %s: %s.') % (contact_exist.name, _('ID') if len(rnc) == 11 else _('RNC'), rnc))
                
                data = self.get_name_from_dgii(rnc)
                
                if data.get('name', False):
                    val.update({
                        'name': data.get('name', False),
                        'vat': rnc
                    })
                
                elif not is_from_vat:
                    if self.env['ir.config_parameter'].get_param('l10n_do_rnc.rnc_data_fallback'):
                        raise ValidationError(_("The company name could not be found, please enter the name manually and the RNC/Cedula in the RNC field of the interface.\n\nError context: \n%s") % data.get('error', False))
                    else:
                        raise ValidationError(_("The company name could not be found, consider use RNC fallback option in the settings to search the name in the RNC local database.\n\nError context: \n%s") % data.get('error', False))

        res = super(Partner, self).create(vals_list)

        res._compute_sale_fiscal_type_id()
        
        return res

    def write(self, vals):

        if vals.get('vat', False):
            dominican_company_parnters = self.filtered(
                lambda p: p.country_id and p.country_id.code == 'DO' and not p.parent_id)
                
            for partner in dominican_company_parnters:

                try:
                    data = self.get_name_from_dgii(vals['vat'])

                    if data.get('name', False):
                        vals['name'] = data.get('name', False)
                    else:
                        _logger.error(data.get('error', False))

                except Exception as e:
                    _logger.error(e)

        return super(Partner, self).write(vals)

    def get_name_from_dgii(self, vat):
        """
        Retrieves the company name based on the configured service (DGII or Jenrax).
        :param vat: RNC or ID to query.
        :return: Company name or False if not found.
        """
        if len(vat) not in [9, 11]:
            raise UserError(_('Please verify the RNC/ID. It must have 9 digits for RNC or 11 for ID.'))

        if not ((len(vat) == 9 and rnc.is_valid(vat)) or (len(vat) == 11 and cedula.is_valid(vat))):
            raise UserError(_('The entered RNC/ID is not valid.'))
    
        # 1. FIRST ATTEMPT: DGII online service
        try:
            result = rnc.check_dgii(vat)
            if result is not None:
                result["name"] = " ".join(re.split(r"\s+", result["name"], flags=re.UNICODE))
                return {
                    'name': result["name"]
                }
        except Exception as e:
            _logger.warning(f"DGII service not available: {e}")
            error = e

        if self.env['ir.config_parameter'].get_param('l10n_do_rnc.rnc_data_fallback'):
            offline_name = self.env['rnc.cache'].search_rnc(vat)
            if offline_name:
                _logger.info(f"RNC {vat} found in offline cache")
                return {
                    'name': offline_name
                }
        return {
            'error': error or 'Unknown error'
        }