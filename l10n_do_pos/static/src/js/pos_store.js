import { PosStore } from "@point_of_sale/app/store/pos_store";
import { patch } from "@web/core/utils/patch";

patch(PosStore.prototype, {

    async processServerData() {
        await super.processServerData();
        this.fiscal_types = this.data.models['account.fiscal.type'].getAll();
    },

    async get_fiscal_data(order) {
        return await this.data.call(
            'pos.order',
            'get_next_fiscal_sequence',
            [
                false,
                order.fiscal_type.id,
                this.company.id,
                [],
            ],
        );
    },

    isCreditNoteMode() {
        const current_order = this.get_order();
        return this.config.l10n_do_fiscal_journal && current_order && current_order._isRefundOrder();
    },

    get_credit_note_payment_method() {
        var credit_note_payment_method = false;
        this.config.payment_method_ids.forEach(
            function (payment_method) {
                if (payment_method.is_credit_note) {
                    credit_note_payment_method = payment_method;
                }
            }
        );
        return credit_note_payment_method;
    },

    async get_credit_note(ncf) {
        return await this.data.call(
            'pos.order',
            'get_credit_note',
            [
                false,
                ncf
            ],
        );
    },

    async get_credit_notes(partner_id) {
        return await this.data.call(
            'pos.order',
            'get_credit_notes',
            [
                false,
                partner_id
            ],
        );
    }
});
