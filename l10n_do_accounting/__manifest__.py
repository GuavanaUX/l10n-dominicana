{
    'name': 'Fiscal Accounting (Dominican Republic)',
    'summary': 
    """    
        This module implements the management of fiscal receipts numbers
        for compliance with the 06-18 regulation of the Dirección General de 
        Impuestos Internos in the Dominican Republic.
        
        It also includes the management of fiscal types and fiscal sequences.
    """,
    'author': 'Marcos, Guavana, Indexa, Iterativo SRL, Neotec, UnlimitSoft',
    'license': 'LGPL-3',
    'website': 'https://github.com/odoo-dominicana',
    'category': 'Localization',
    'version': '18.0.0.1.3',
    # any module necessary for this one to work correctly
    'depends': [
        'base',
        'web',
        'account',
        'l10n_do',
    ],
    # any python dependencies for this one to work correctly
    'external_dependencies': {
        'python': [
            'python-stdnum',
        ],
    },
    # always loaded
    'data': [
        'data/ir_config_parameters.xml',
        'data/ir_cron_data.xml',
        'data/account_fiscal_type_data.xml',
        # 'data/report_layout_data.xml',
        # 'data/mail_template_data.xml',

        'security/ir.model.access.csv',
        'security/res_groups.xml',

        'wizard/account_fiscal_sequence_validate_wizard_views.xml',
        'wizard/account_invoice_refund_views.xml',

        # 'views/account_report.xml',
        'views/account_invoice_views.xml',
        'views/account_payment_term.xml',
        'views/account_journal_views.xml',
        'views/res_partner_views.xml',
        'views/account_fiscal_sequence_views.xml',
        # Odoo 18 uses RNC as default string for the field display name.
        # If you want to add another field, you can uncomment the next line.
        #'views/res_company_views.xml',
        'views/account_invoice_cancel_views.xml',
        # 'views/backend_js.xml',

        'views/report_templates.xml',
        'views/report_invoice.xml',
        'views/layouts.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/res_partner_demo.xml',
        'demo/account_fiscal_sequence_demo.xml',
    ],
}
