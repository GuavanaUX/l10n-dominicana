from . import models
from . import wizard
from . import controllers

import logging
from odoo import api, SUPERUSER_ID

_logger = logging.getLogger(__name__)

def migrate_journal_fields(env):
    
    env.cr.execute(
        """
            UPDATE account_journal
            SET payment_form = CASE
                WHEN dgii_payment_method = 'cash' THEN 'cash'
                WHEN dgii_payment_method = 'check_transfer' THEN 'bank'
                WHEN dgii_payment_method = 'card' THEN 'card'
                WHEN dgii_payment_method = 'certificate' THEN 'bond'
                WHEN dgii_payment_method = 'barter' THEN 'swap'
                WHEN dgii_payment_method = 'others_sale_forms' THEN 'others'
                ELSE payment_form
            END;
        """
    )

    env.cr.execute(
        """
            UPDATE account_journal
            SET l10n_do_fiscal_journal = ncf_control
            END;
        """
    )

def search_fiscal_type(env, prefix, type):
    fiscal_type = env['account.fiscal.type'].search([
        ('type', '=', type),
        ('prefix', '=', prefix),
    ])
    return fiscal_type

def migrate_sale_invoice_fields(env, company):

    Move = env["account.move"]

    # Sale invoices routine
    sales_journal = Move.with_context(
        default_type="sale", default_company_id=company.id
    )._get_default_journal()

    sale_invoices = Move.search(
        [
            ("journal_id", "=", sales_journal.id),
            ("company_id", "=", company.id),
            ("fiscal_type_id", "=", False),
        ]
    )
    sale_invoices_len = len(sale_invoices)

    for i, invoice in enumerate(sale_invoices):
        query = """
                SELECT
                name, ncf_control, anulation_type, sale_fiscal_type
                FROM account_invoice
                WHERE move_name = '%s'
                AND state != 'draft'
                AND company_id = %s;
            """
        env.cr.execute(query % (invoice.name, company.id))
        data = env.cr.fetchone()
        fiscal_type_id = False
        if data:
            _logger.info(
                "Migrating data for sale invoice %s - %s of %s"
                % (data[0], i, sale_invoices_len)
            )

            if data[2] == 'consumo':
                fiscal_type_id = search_fiscal_type(env, 'B02', 'out_invoice')
            elif data[2] == 'credito':
                fiscal_type_id = search_fiscal_type(env, 'B01', 'out_invoice')
            elif data[2] == 'gubernamental':
                fiscal_type_id = search_fiscal_type(env, 'B15', 'out_invoice')
            elif data[2] == 'tributacion':
                fiscal_type_id = search_fiscal_type(env, 'B14', 'out_invoice')
            elif data[2] == 'unico':
                fiscal_type_id = search_fiscal_type(env, 'B12', 'out_invoice')
            elif data[2] == 'debit_note':
                fiscal_type_id = search_fiscal_type(env, 'B03', 'out_debit')
            elif data[2] == 'credit_note':
                fiscal_type_id = search_fiscal_type(env, 'B04', 'out_refund')

            invoice._write(
                {
                    "ref": data[0],
                    "is_l10n_do_fiscal_invoice": data[1],
                    "annulation_type": data[1],
                    "fiscal_type_id": fiscal_type_id.id,
                }
            )

    sales_journal._write({"l10n_do_fiscal_journal": True})

def migrate_purchase_invoice_fields(env, company):

    # Purchase invoices routine
    env.cr.execute(
    """
        SELECT id FROM account_journal
        WHERE type = 'purchase'
        AND purchase_type != 'others'
        AND company_id = %s
    """
        % company.id
    )

    purchase_journals = env["account.journal"].browse([i[0] for i in env.cr.fetchall()])
    Move = env["account.move"]

    for journal in purchase_journals:

        purchase_invoices = Move.search(
            [
                ("journal_id", "=", journal.id),
                ("company_id", "=", company.id),
                ("fiscal_type_id", "=", False),
            ]
        )
        purchase_invoices_len = len(purchase_invoices)

        for i, invoice in enumerate(purchase_invoices):
            query = """
                        SELECT
                        name, ncf_control, anulation_type, purchase_type
                        FROM account_invoice
                        WHERE move_name = '%s'
                        AND state != 'draft'
                        AND company_id = %s;
                    """
            env.cr.execute(query % (invoice.name, company.id))
            data = env.cr.fetchone()
            fiscal_type_id = False
            if data:
                _logger.info(
                    "Migrating data for purchase invoice %s - %s of %s"
                    % (data[0], i, purchase_invoices_len)
                )

                if data[2] == 'normal':
                    fiscal_type_id = search_fiscal_type(env, 'B01', 'in_invoice')
                elif data[2] == 'minor':
                    fiscal_type_id = search_fiscal_type(env, 'B13', 'in_invoice')
                elif data[2] == 'exterior':
                    fiscal_type_id = search_fiscal_type(env, 'B17', 'in_invoice')
                elif data[2] == 'informal':
                    fiscal_type_id = search_fiscal_type(env, 'B11', 'in_invoice')
                elif data[2] == 'in_refund':
                    fiscal_type_id = search_fiscal_type(env, 'B03', 'in_refund')
                elif data[2] == 'in_debit':
                    fiscal_type_id = search_fiscal_type(env, 'B04', 'in_debit')

                invoice._write(
                {
                    "ref": data[0],
                    "is_l10n_do_fiscal_invoice": data[1],
                    "annulation_type": data[1],
                    "fiscal_type_id": fiscal_type_id.id,
                }
            )

        journal._write({"l10n_do_fiscal_journal": True})

def migrate_invoice_fields(env):

    """
    table: account_invoice  -------------------------------------->  account_move
    ncf_control --------------------------------------------------> is_l10n_do_fiscal_invoice
    purchase_type(journal_id.purchase_type)-----------------------> fiscal_type_id(many2one)
    anulation_type(selection)-------------------------------------> annulation_type
    sale_fiscal_type(selection)-----------------------------------> fiscal_type_id(many2one)
    """
    env.cr.execute(
        """
        SELECT EXISTS (
            SELECT FROM information_schema.tables
            WHERE table_schema = 'public'
            AND table_name = 'account_invoice'
        );
        """
    )

    # if account_invoice table exist
    if env.cr.fetchone()[0] or False:

        _logger.info("Starting data migration from account_invoice to account_move")

        for company in (
            env["res.company"]
            .search([("chart_template_id", "!=", False)])
            .filtered(lambda c: c.partner_id.country_id == env.ref("base.do"))
        ):

            migrate_sale_invoice_fields(env, company)
            migrate_purchase_invoice_fields(env, company)

            # Archive deprecated journals.
            # purchase_type in (minor, informal, exterior).
            env.cr.execute(
                """
            SELECT id FROM account_journal
            WHERE type = 'purchase'
            AND purchase_type != 'normal'
            AND company_id = %s
            """
                % company.id
            )

            env["account.journal"].browse([i[0] for i in env.cr.fetchall()]).write(
                {"active": False}
            )

def migrate_partner_fields(env):
    """
    sale_fiscal_type -----------------> fiscal_type_id
    """
    env.cr.execute(
        """
        SELECT EXISTS(
            SELECT
            FROM information_schema.columns
            WHERE table_name = 'res_partner'
            AND column_name = 'sale_fiscal_type'
        );
        """
    )

    if env.cr.fetchone()[0] or False:
        _logger.info("Starting partner fields migration")
        env.cr.execute(
            """
            SELECT id, sale_fiscal_type
            FROM res_partner
            WHERE sale_fiscal_type_id IS NULL
            AND expense_type IS NOT NULL;
            """
        )
        for i, fiscal_type in env.cr.fetchall():
            if fiscal_type == 'consumo':
                fiscal_type_id = search_fiscal_type(env, 'B02', 'out_invoice')
            elif fiscal_type == 'credito':
                fiscal_type_id = search_fiscal_type(env, 'B01', 'out_invoice')
            elif fiscal_type == 'gubernamental':
                fiscal_type_id = search_fiscal_type(env, 'B15', 'out_invoice')
            elif fiscal_type == 'tributacion':
                fiscal_type_id = search_fiscal_type(env, 'B14', 'out_invoice')
            elif fiscal_type == 'unico':
                fiscal_type_id = search_fiscal_type(env, 'B12', 'out_invoice')

            partner_id = env["res.partner"].browse(i)
            _logger.info(
                "Setting up %s sale_fiscal_type_id = %s"
                % (partner_id.name, fiscal_type)
            )
            partner_id.write({"sale_fiscal_type_id": fiscal_type_id.id})


def migrate_fiscal_sequences(env):
    fiscal_sequence = env['account.fiscal.sequence']
    """
    table : ir_sequence ----------------------------------------> account_fiscal_sequence

    id ---------------------------------------------------------> sequence_id
    ncf_max ----------------------------------------------------> sequence_end
    sale_fiscal_type -------------------------------------------> fiscal_type_id
    ncf_expiration_date ----------------------------------------> expiration_date
    is_ncf_active ----------------------------------------------> state('active')
    """
    env.cr.execute(
        """
        SELECT name ,id, ncf_max, sale_fiscal_type,
            ncf_expiration_date, is_ncf_active
            FROM ir_sequence
            WHERE is_ncf_active NOT NULL
        """
    )

    if env.cr.fetchone():
        _logger.info(
            "Starting data migration from ir_sequence to account_fiscal_sequence"
        )

        fields = env.cr.fetchone()
        for field in fields:
            if field[3] == 'consumo':
                fiscal_type_id = search_fiscal_type(env, 'B32', 'out_invoice')
            elif field[3] == 'credito':
                fiscal_type_id = search_fiscal_type(env, 'B31', 'out_invoice')
            elif field[3] == 'gubernamental':
                fiscal_type_id = search_fiscal_type(env, 'B15', 'out_invoice')
            elif field[3] == 'tributacion':
                fiscal_type_id = search_fiscal_type(env, 'B14', 'out_invoice')
            elif field[3] == 'unico':
                fiscal_type_id = search_fiscal_type(env, 'B12', 'out_invoice')
            elif field[3] == 'in_refund':
                fiscal_type_id = search_fiscal_type(env, 'B33', 'in_refund')
            elif field[3] == 'in_debit':
                fiscal_type_id = search_fiscal_type(env, 'B04', 'in_debit')

            fiscal_sequence.create({
                'name': field[0],
                'sequence_id': field[1],
                'sequence_end': field[2],
                'fiscal_type_id': fiscal_type_id.id,
                'expiration_date': field[4],
                'state': 'active' if field[5] == True else 'draft'
            })

def post_init_hook(cr, registry):
    """
    This script maps and migrate data from v10 ncf_manager_g module to their
    homologue fields present in this module.
    """

    env = api.Environment(cr, SUPERUSER_ID, {})

    migrate_journal_fields(env)
    migrate_invoice_fields(env)
    migrate_fiscal_sequences(env)
    migrate_partner_fields(env)
