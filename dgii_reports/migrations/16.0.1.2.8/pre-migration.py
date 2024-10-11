from openupgradelib import openupgrade


def _rename_and_change_to_monetary(env, table, old_field, new_field):

    """
    model: dgii.reports
    purchase_total_services(Float) --------------------------------> service_total_amount(monetary)
    purchase_total_consumption(float)------------------------------> good_total_amount(monetary)
    purchase_total_untax(float) -----------------------------------> purchase_invoiced_amount(monetary)
    purchase_total_tax(float) -------------------------------------> purchase_invoiced_itbis(monetary)
    purchase_total_withheld_tax(float)-----------------------------> purchase_withholded_itbis(monetary)
    purchase_total_taken_to_cost_itbis(float) ---------------------> cost_itbis(monetary)
    purchase_total_to_overtake_itbis(float) -----------------------> advance_itbis(monetary)
    purchase_total_perceived_in_purchases_itbis(float)-------------> income_withholding(monetary)
    purchase_total_excise_tax(float) ------------------------------> purchase_selective_tax (monetary)
    purchase_total_other_taxes(float) -----------------------------> purchase_other_taxes(monetary)
    purchase_total_legal_tip_amount(float) ------------------------> purchase_legal_tip(monetary)
    sale_total_untax(monetary)-------------------------------------> sale_invoiced_amount(float)

    
    """

    openupgrade.logged_query(
        env.cr,
        """
        ALTER TABLE {}
        RENAME COLUMN {} TO {},
        ALTER COLUMN {} TYPE numeric;   
        """.fotmat(table, old_field, new_field, new_field)
    )

def _rename_and_change_to_float(env, table, old_field, new_field):
    """
    model: dgii.reports.sale.line
    total_untax(monetary)------------------------------------------> invoiced_amount(float)
    """

    openupgrade.logged_query(
    env.cr,
        """
        ALTER TABLE dgii_reports_sale_line
        RENAME COLUMN total_untax TO invoiced_amount,
        ALTER COLUMN invoiced_amount TYPE double precision;
        """
)


def _rename_models(env):
    openupgrade.rename_models(env.cr, [
        ("dgii.report.exterior.line", "dgii.reports.exterior.line"),
        ("dgii.report.sale.line", "dgii.reports.sale.line"),
        ("dgii.report.purchase.line", "dgii.reports.purchase.line"),
        ("dgii.report", "dgii.reports"),
    ])

def _rename_tables(env):
    openupgrade.rename_tables(env.cr, [
        ("dgii_report_exterior_line", "dgii_reports_exterior_line"),
        ("dgii_report_sale_line", "dgii_reports_sale_line"),
        ("dgii_report_purchase_line", "dgii_reports_purchase_line"),
        ("dgii_report", "dgii_reports"),
    ])

def _rename_fields(env):
    openupgrade.rename_fields(
        env,
        [
            ("account.tax","account_tax","retention_tax","isr_retention_type",),
            ("dgii.reports", "dgii_reports", "purchase_count_lines", "purchase_records"),
            ("dgii.reports", "dgii_reports", "sale_count_lines", "sale_records"),
            ("dgii.reports", "dgii_reports", "sale_total_tax", "sale_invoiced_itbis"),
            ("dgii.reports", "dgii_reports", "sale_withheld_third_parties_tax", "sale_withholded_itbis"),
            ("dgii.reports", "dgii_reports", "sale_withheld_third_parties_isr", "sale_withholded_isr"),
            ("dgii.reports", "dgii_reports", "sale_excise_tax", "sale_selective_tax"),
            ("dgii.reports", "dgii_reports", "sale_other_taxes", "sale_other_taxes"),
            ("dgii.reports", "dgii_reports", "sale_legal_tip_amount", "sale_legal_tip"),
            ("dgii.reports", "dgii_reports", "cancel_count_lines", "cancel_records"),
            ("dgii.reports.purchase.line", "dgii_reports_purchase_line", "is_credit_note", "credit_note"),
            ("dgii.reports.purchase.line", "dgii_reports_purchase_line", "partner_id", "invoice_partner_id"),
            ("dgii.reports.purchase.line", "dgii_reports_purchase_line", "vat", "rnc_cedula"),
            ("dgii.reports.purchase.line", "dgii_reports_purchase_line", "id_type", "identification_type"),
            ("dgii.reports.purchase.line", "dgii_reports_purchase_line", "name", "fiscal_invoice_number"),
            ("dgii.reports.purchase.line", "dgii_reports_purchase_line", "origin", "modified_invoice_number"),
            ("dgii.reports.purchase.line", "dgii_reports_purchase_line", "date", "invoice_date"),
            ("dgii.reports.purchase.line", "dgii_reports_purchase_line", "pay_date", "payment_date"),
            ("dgii.reports.purchase.line", "dgii_reports_purchase_line", "total_amount_services", "service_total_amount"),
            ("dgii.reports.purchase.line", "dgii_reports_purchase_line", "total_amount_consumption", "good_total_amount"),
            ("dgii.reports.purchase.line", "dgii_reports_purchase_line", "total_untax", "invoiced_amount"),
            ("dgii.reports.purchase.line", "dgii_reports_purchase_line", "total_tax", "invoiced_itbis"),
            ("dgii.reports.purchase.line", "dgii_reports_purchase_line", "withheld_tax", "withholded_itbis"),
            ("dgii.reports.purchase.line", "dgii_reports_purchase_line", "subject_to_proporcional_itbis", "proportionality_tax"),
            ("dgii.reports.purchase.line", "dgii_reports_purchase_line", "taken_to_cost_itbis", "cost_itbis"),
            ("dgii.reports.purchase.line", "dgii_reports_purchase_line", "to_overtake_itbis", "advance_itbis"),
            ("dgii.reports.purchase.line", "dgii_reports_purchase_line", "perceived_in_purchases_itbis", "purchase_perceived_itbis"),
            ("dgii.reports.purchase.line", "dgii_reports_purchase_line", "type_retention_tax", "isr_withholding_type"),
            ("dgii.reports.purchase.line", "dgii_reports_purchase_line", "withheld_isr", "income_withholding"),
            ("dgii.reports.purchase.line", "dgii_reports_purchase_line", "perceived_purchase_isr", "purchase_perceived_isr"),
            ("dgii.reports.purchase.line", "dgii_reports_purchase_line", "excise_tax", "selective_tax"),
            ("dgii.reports.purchase.line", "dgii_reports_purchase_line", "other_taxes", "other_taxes"),
            ("dgii.reports.purchase.line", "dgii_reports_purchase_line", "legal_tip_amount", "legal_tip"),
            ("dgii.reports.purchase.line", "dgii_reports_purchase_line", "method_of_payment", "payment_type"),
            ("dgii.reports.sale.line", "dgii_reports_sale_line", "is_credit_note", "credit_note"),
            ("dgii.reports.sale.line", "dgii_reports_sale_line", "partner_id", "invoice_partner_id"),
            ("dgii.reports.sale.line", "dgii_reports_sale_line", "vat", "rnc_cedula"),
            ("dgii.reports.sale.line", "dgii_reports_sale_line", "id_type", "identification_type"),
            ("dgii.reports.sale.line", "dgii_reports_sale_line", "name", "fiscal_invoice_number"),
            ("dgii.reports.sale.line", "dgii_reports_sale_line", "origin", "modified_invoice_number"),
            ("dgii.reports.sale.line", "dgii_reports_sale_line", "income_type", "income_type"),
            ("dgii.reports.sale.line", "dgii_reports_sale_line", "date", "invoice_date"),
            ("dgii.reports.sale.line", "dgii_reports_sale_line", "retention_date", "withholding_date"),
            ("dgii.reports.sale.line", "dgii_reports_sale_line", "total_tax", "invoiced_itbis"),
            ("dgii.reports.sale.line", "dgii_reports_sale_line", "withheld_third_parties_tax", "third_withheld_itbis"),
            ("dgii.reports.sale.line", "dgii_reports_sale_line", "perceived_tax", "perceived_itbis"),
            ("dgii.reports.sale.line", "dgii_reports_sale_line", "withheld_third_parties_isr", "third_income_withholding"),
            ("dgii.reports.sale.line", "dgii_reports_sale_line", "perceived_isr", "perceived_isr"),
            ("dgii.reports.sale.line", "dgii_reports_sale_line", "excise_tax", "selective_tax"),
            ("dgii.reports.sale.line", "dgii_reports_sale_line", "other_taxes", "other_taxes"),
            ("dgii.reports.sale.line", "dgii_reports_sale_line", "legal_tip_amount", "legal_tip"),
            ("dgii.reports.sale.line", "dgii_reports_sale_line", "amount_cash", "cash"),
            ("dgii.reports.sale.line", "dgii_reports_sale_line", "amount_check_transfer_deposit", "bank"),
            ("dgii.reports.sale.line", "dgii_reports_sale_line", "amount_card", "card"),
            ("dgii.reports.sale.line", "dgii_reports_sale_line", "credit_sale", "credit"),
            ("dgii.reports.sale.line", "dgii_reports_sale_line", "gifts_certicate", "bond"),
            ("dgii.reports.sale.line", "dgii_reports_sale_line", "barter", "swap"),
            ("dgii.reports.sale.line", "dgii_reports_sale_line", "others_sale_forms", "others"),
            ("dgii.reports.cancel.line", "dgii_reports_cancel_line", "name", "fiscal_invoice_number"),
        ]
    )


@openupgrade.migrate()
def migrate(env, version):
        
    _rename_models(env)
    _rename_tables(env)
    _rename_fields(env)
    _rename_and_change_to_float(env)

    fields_float_to_monetary = {
        'purchase_total_services': 'service_total_amount',
        'purchase_total_consumption': 'good_total_amount',
        'purchase_total_untax': 'purchase_invoiced_amount',
        'purchase_total_tax': 'purchase_invoiced_itbis',
        'purchase_total_withheld_tax': 'purchase_withholded_itbis',
        'purchase_total_taken_to_cost_itbis': 'cost_itbis',
        'purchase_total_to_overtake_itbis': 'advance_itbis',
        'purchase_total_perceived_in_purchases_itbis': 'income_withholding',
        'purchase_total_excise_tax': 'purchase_selective_tax',
        'purchase_total_other_taxes': 'purchase_other_taxes',
        'purchase_total_legal_tip_amount': 'purchase_legal_tip',
        'sale_total_untax': 'sale_invoiced_amount'
    }

    for old_field, new_field in fields_float_to_monetary.items():
        _rename_and_change_to_monetary(env, 'dgii_reports', old_field, new_field, new_field)

