# Part of Domincana Premium.
# See LICENSE file for full copyright and licensing details.
# © 2018 José López <jlopez@indexa.do>

from . import controllers
from . import models
from . import wizard


from odoo import api, SUPERUSER_ID

def update_taxes(env):
    Tax = env['account.tax']
    # Selecciona todos los impuestos con valores configurados en los nuevos campos
    template_taxes = Tax.search([
        ('l10n_do_tax_type', '!=', False),
        ('isr_retention_type', '!=', False),
    ])
    for tmpl in template_taxes:
        # Encuentra impuestos del mismo nombre, misma compañía y distintos ID
        duplicates = Tax.search([
            ('name', '=', tmpl.name),
            ('company_id', '=', tmpl.company_id.id),
            ('id', '!=', tmpl.id),
        ])
        if duplicates:
            duplicates.write({
                'l10n_do_tax_type': tmpl.l10n_do_tax_type,
                'isr_retention_type': tmpl.isr_retention_type,
                'tax_group_id': tmpl.tax_group_id.id,
            })
