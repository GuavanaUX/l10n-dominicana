import { _t } from "@web/core/l10n/translation";
import { patch } from "@web/core/utils/patch";
import { PosOrder } from "@point_of_sale/app/models/pos_order";
import { onMounted } from "@odoo/owl";

patch(PosOrder.prototype, {
    async setup() {
        super.setup(...arguments);

        this.ncf = '';
        this.ncf_origin_out = '';
        this.ncf_expiration_date = '';
        this.fiscal_type_id = false;
        this.fiscal_sequence_id = false;

        onMounted(async () => {
            // Si env.pos todavía no existe, espera hasta que esté listo
            while (!this.env.pos) {
                await new Promise(r => setTimeout(r, 10));
            }

            await this.env.pos.wait_fiscal_types_ready();

            const partner = this.get_partner();
            if (partner?.sale_fiscal_type_id) {
                this.set_fiscal_type(
                    this.env.pos.get_fiscal_type_by_id(partner.sale_fiscal_type_id[0])
                );
            } else {
                this.set_fiscal_type(
                    this.env.pos.get_fiscal_type_by_prefix('B02')
                );
            }
        });
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
            this.set_fiscal_type(this.env.pos.get_fiscal_type_by_id(partner.sale_fiscal_type_id[0]));
        } else {
            this.set_fiscal_type(this.env.pos.prototype.get_fiscal_type_by_prefix('B02'));
        }
    },

    set_ncf_origin_out(ncf_origin_out) {
        this.ncf_origin_out = ncf_origin_out;
    }
});