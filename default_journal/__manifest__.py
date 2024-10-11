{
    'name': 'Diario por defecto',
    'version': '1.0',
    'summary': '',
    'description': 'Este módulo asigna un diario contable por defecto, por usuario.',
    'category': '',
    'author': 'Sarah Pérez',
    'website': 'www.guavana.com',
    'license': '',
    'depends': ['account'],
    'data': [
        'views/res_users_view.xml',
        'security/ir.model.access.csv',
        'views/account_journal_view.xml'
             ],
    'installable': True,
    'auto_install': False,
}