import { _t } from "@web/core/l10n/translation";
import { patch } from "@web/core/utils/patch";
import { PosStore } from "@point_of_sale/app/store/pos_store";
import { PosOrder } from "@point_of_sale/app/models/pos_order";
import { usePos } from "@point_of_sale/app/store/pos_hook";
import { Component, useState, onMounted } from "@odoo/owl";

patch(PosOrder.prototype, {
    setup() {
        super.setup(...arguments);
        this.pos = PosStore;
        console.log("PosOrder ", this);

        this.ncf = '';
        this.ncf_origin_out = '';
        this.ncf_expiration_date = '';
        this.fiscal_type_id = false;
        this.fiscal_sequence_id = false;

        var partner = this.get_partner();

        if (partner && partner.sale_fiscal_type_id) {
            this.set_fiscal_type(this.pos.get_fiscal_type_by_id(partner.sale_fiscal_type_id[0]));
        } else {
            this.set_fiscal_type(this.pos.prototype.get_fiscal_type_by_prefix('B02'))
        }
    },

    set_fiscal_type(fiscal_type) {
        this.fiscal_type = fiscal_type;
        this.fiscal_type_id = fiscal_type.id;
        if (fiscal_type && fiscal_type.fiscal_position_id) {
            this.set_fiscal_position(_.find(this.pos.fiscal_positions, function (fp) {
                return fp.id === fiscal_type.fiscal_position_id[0];
            }));
            for (let line of this.get_orderlines()) {
                line.set_quantity(line.quantity);
            }
        }
    },

    get_fiscal_type() {
        return this.fiscal_type;
    },

    set_partner(partner) {
        super.set_partner(partner);
        if (partner && partner.sale_fiscal_type_id) {
            this.set_fiscal_type(this.pos.get_fiscal_type_by_id(partner.sale_fiscal_type_id[0]));
        } else {
            this.set_fiscal_type(this.pos.prototype.get_fiscal_type_by_prefix('B02'));
        }
    },

    set_ncf_origin_out(ncf_origin_out) {
        this.ncf_origin_out = ncf_origin_out;
    }
});