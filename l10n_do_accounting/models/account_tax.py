from odoo import fields, models, _


class AccountTax(models.Model):
    _inherit = "account.tax"

    tax_code = fields.Char(
        string="Tax Code",
        readonly=True,
        help="Tax code",
        copy=True,
    )

    l10n_do_tax_group = fields.Selection(
        string="Tax Group",
        readonly=True,
        help="Type of tax according to Dominican tax regulations",
        copy=True,
        selection=[
            ("itbis_general", _("ITBIS 18%")),
            ("itbis_reduced", _("ITBIS 16% (Transitory / Specific cases)")),
            ("itbis_exempt", _("ITBIS 0% (Exempt / Not subject to tax)")),
            ("isc_specific", _("ISC Specific")),
            ("isc_ad_valorem", _("ISC Ad Valorem")),
            # ("OTROS_ADICIONALES", _("Other Additional Taxes")),
            ("itbis_withholding", _("ITBIS Withholding")),
            ("isr_withholding", _("ISR Withholding")),
            ("itbis_perception", _("ITBIS Perception")),
            ("isr_perception", _("ISR Perception")),
            ("legal_tip", _("Legal Tip Tax")),
            # ("municipal_taxes", _("Municipal Taxes")),
            # ("special_taxes", _("Special Taxes")),
        ],
    )

    origin = fields.Selection(
        string="Origin",
        readonly=True,
        help="Origin of the tax",
        copy=True,
        selection=[
            ("base_taxes", _("Base Taxes")),
            ("additional_taxes", _("Additional Taxes")),
            ("other_additional_taxes", _("Other Additional Taxes")),
        ],
    )
