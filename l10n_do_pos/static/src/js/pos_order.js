import { PosOrder } from "@point_of_sale/app/models/pos_order";
import { patch } from "@web/core/utils/patch";
import { formatDate } from "@web/core/l10n/dates";
import { parseUTCString } from "@point_of_sale/utils";

patch(PosOrder.prototype, {

    setup(_defaultObj, options) {
        super.setup(...arguments);
        if (this.config.l10n_do_fiscal_journal) {
            this.customer_count = this.customer_count || 1;
            this.ncf = this.ncf || '';
            this.ncf_origin_out = this.ncf_origin_out || '';
            this.ncf_expiration_date = this.ncf_expiration_date || false;
            this.fiscal_type_id = this.fiscal_type_id || false;
            this.fiscal_sequence_id = this.fiscal_sequence_id || false;
            var partner = this.get_partner();
            if (partner && partner.sale_fiscal_type_id) {
                this.set_fiscal_type(this.get_fiscal_type_by_id(partner.sale_fiscal_type_id.id));
            } else {
                this.set_fiscal_type(this.get_fiscal_type_by_prefix('B02'))
            }
        }
    },

    set_fiscal_type(fiscal_type) {
        this.fiscal_type = fiscal_type;
        this.fiscal_type_id = fiscal_type.id;
        if (fiscal_type && fiscal_type.fiscal_position_id) {
            const fiscalPosition = this.models["account.fiscal.position"].find(
                (position) => position.id === fiscal_type.fiscal_position_id?.id
            )
            if (fiscalPosition) {
                this.update({ fiscal_position_id: fiscalPosition });
                // Only reapply taxes on editable orders
                if (!this.finalized) {
                    for (const line of this.get_orderlines()) {
                        line.set_quantity(line.qty);
                    }
                }
            }
        }
    },

    get_fiscal_type() {
        return this.fiscal_type;
    },

    get fiscal_types() {
        return this.models['account.fiscal.type'].getAll();
    },

    get_fiscal_type_by_id(id) {
        var res_fiscal_type = false;
        this.fiscal_types.forEach(function (fiscal_type) {
            if (fiscal_type.id === id) {
                res_fiscal_type = fiscal_type;
            }
        });
        if (!res_fiscal_type) {
            res_fiscal_type = this.get_fiscal_type_by_prefix('B02');
        }
        return res_fiscal_type;
    },

    get_fiscal_type_by_prefix(prefix) {
        var res_fiscal_type = false;
        this.fiscal_types.forEach(function (fiscal_type) {
            if (fiscal_type.prefix === prefix) {
                res_fiscal_type = fiscal_type;
            }
        });
        return res_fiscal_type;
    },

    set_partner(partner) {
        const invoice = this.is_to_invoice();
        super.set_partner(partner);
        this.set_to_invoice(invoice);
        if (partner && partner.sale_fiscal_type_id) {
            this.set_fiscal_type(this.get_fiscal_type_by_id(partner.sale_fiscal_type_id.id));
        } else {
            this.set_fiscal_type(this.get_fiscal_type_by_prefix('B02'));
        }
    },

    set_ncf_origin_out(ncf_origin_out) {
        this.ncf_origin_out = ncf_origin_out;
    },

    export_for_printing(baseUrl, headerData) {
        const result = super.export_for_printing(...arguments);
        result.headerData = {
                ...headerData,
                l10n_do_fiscal_journal: this.config.l10n_do_fiscal_journal,
                date: result.date,
                partner: this.get_partner(),
                ncf: this.ncf,
                ncf_origin_out: this.ncf_origin_out,
                ncf_expiration_date: this.ncf_expiration_date && formatDate(parseUTCString(this.ncf_expiration_date)),
            }
        result.fiscal_type = this.get_fiscal_type();
        return result;
    },
});
