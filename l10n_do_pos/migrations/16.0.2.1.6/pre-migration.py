from openupgradelib import openupgrade


def search_pos_order(env, prefix, type):
    pos_order = env['pos.order'].search([
        ('type', '=', type),
        ('prefix', '=', prefix),
    ])
    return pos_order

def _rename_fields(env):
    
    openupgrade.rename_fields(
        env,
        [
            ("pos.config","pos_config","default_partner_id","pos_partner_id",),
            ("pos.order", "pos_order", "move_name", "ncf"),
            ("pos.order", "pos_order", "sale_fiscal_type", "sale_invoiced_itbis"),
        ]
    )

    openupgrade.logged_query(env.cr(
        """
        SELECT sale_fiscal_type 
        FROM pos_order
        WHERE sale_fiscal_type NOT NULL
        """

    ))

    for i, fiscal_type in env.cr.fetchall():
        if fiscal_type == 'consumo':
            fiscal_type_id = search_pos_order(env, 'B02', 'out_invoice')
        elif fiscal_type == 'credito':
            fiscal_type_id = search_pos_order(env, 'B01', 'out_invoice')
        elif fiscal_type == 'gubernamental':
            fiscal_type_id = search_pos_order(env, 'B15', 'out_invoice')
        elif fiscal_type == 'tributacion':
            fiscal_type_id = search_pos_order(env, 'B14', 'out_invoice')
        elif fiscal_type == 'unico':
            fiscal_type_id = search_pos_order(env, 'B12', 'out_invoice')
        elif fiscal_type == 'debit_note':
            fiscal_type_id = search_pos_order(env, 'B03', 'out_debit')
        elif fiscal_type == 'credit_note':
            fiscal_type_id = search_pos_order(env, 'B04', 'out_refund')

        openupgrade.logged_query(env.cr(
            """
            UPDATE pos_order
            SET fiscal_type_id = {}
            WHERE sale_fiscal_type = {}
            """
        )).format(fiscal_type_id, fiscal_type)

@openupgrade.migrate()
def migrate(env, version):

    _rename_fields(env)
