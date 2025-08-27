{
    'name': "Fiscal POS (Dominican Republic)",
    'summary': 
    """
        This module adds NCF invoicing functionalities to the POS.
    """,
    'author': "Guavana, Indexa, Iterativo SRL, UnlimitSoft",
    'license': 'LGPL-3',
    'website': "https://github.com/odoo-dominicana",
    'category': 'Localization',
    'version': '18.0.0.0.2',
    'depends': [
        'base',
        'point_of_sale',
        'l10n_do_accounting',
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/data.xml',
        #'views/res_config_settings_views.xml',
        'views/pos_order_views.xml',
        'views/pos_payment_method_views.xml',
    ],
    # 'assets': {
    #     'point_of_sale.assets': [
    #         'l10n_do_pos/static/src/scss/*',
    #         'l10n_do_pos/static/src/js/**/*.js',
    #         'l10n_do_pos/static/src/xml/**/*.xml',
    #     ],
    # },
    'installable': True,
}
