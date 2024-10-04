# -*- coding: utf-8 -*-
{
    'name': 'Search RNC name',
    'summary': """
        This module searches for the company name by entering a Taxpayer Registration Number (RNC), if the company is valid.
    """,

    'description': """
        This module searches for the company name by entering a Taxpayer Registration Number (RNC), if the company is valid.
    """,
    'author': "Guavana",
    'website': "https://www.guavana.com",
    'license': 'LGPL-3',
    'category': 'Localization',
    'version': '16.0.1.0.9',
    'depends': [
        'base',
        'contacts',
        'l10n_do',
        'l10n_do_accounting',
    ],
    # any python dependencies for this one to work correctly
    'external_dependencies': {
        'python': [
            'python-stdnum',
        ],
    },
    'data': [
        'views/res_partner_views.xml',
    ],
    'installable': True,
}
