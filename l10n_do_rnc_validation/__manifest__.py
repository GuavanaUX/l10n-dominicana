{
    "name": "Dominican Tax ID Validation",
    "summary": "Validate RNC/Cédula from external service",
    "author": "Guavana," "Indexa," "Iterativo",
    "license": "LGPL-3",
    "website": "https://github.com/odoo-dominicana",
    "category": "Extra Tools",
    "version": "18.0.0.0.0",
    "depends": [
        "base",
        "base_setup",
    ],
    "data": [
        "views/res_partner_views.xml",
        "views/res_config_settings_views.xml",
        "data/ir_config_parameter_data.xml",
    ],
    "installable": True,
}
