{
    'name' : 'Asset Management / Loan',
    'author' : 'Mohamed Ramadan',
    'category' : '',
    'version' : "17.0.0.1.0",
    'depends' : [
        'base', 'hr'
    ],
    'data' : [
        'security/ir.model.access.csv',
        'views/base_menu.xml',
        'views/asset_view.xml',
        'views/tag_view.xml',
        'views/asset_loan_view.xml',
        'views/category_group_view.xml',
        'views/make_order_view.xml',
        'data/ir_sequence.xml',
        'report/asset_qr.xml',
        'report/asset_qr_template.xml',
    ],
    'assets': {
        'web.assets_backend': ['mo_asset_management/static/src/css/property.css']
    },
    'application' : True,
}
