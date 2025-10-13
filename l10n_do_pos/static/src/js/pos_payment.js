import { PosPayment } from "@point_of_sale/app/models/pos_payment";
import { patch } from "@web/core/utils/patch";

patch(PosPayment.prototype, {

    setup() {
        super.setup(...arguments);
        this.credit_note_ncf = this.credit_note_ncf || '';
        this.credit_note_partner_id = this.credit_note_partner_id || false;
    },

    set_fiscal_data(ncf, partner_id){
        this.credit_note_ncf = ncf;
        this.credit_note_partner_id = partner_id;
    },
});
