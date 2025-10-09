import { _t } from "@web/core/l10n/translation";
import { patch } from "@web/core/utils/patch";
import { PosStore } from "@point_of_sale/app/store/pos_store";

patch(PosStore.prototype, {
    async setup(env) {
        super.setup(...arguments);

        this.fiscal_types_ready = (async () => {
            this.fiscal_types = await this.env.services.orm.call(
                "account.fiscal.type",
                "search_read",
                [[]]
            );
            return this.fiscal_types;
        })();
    },

    async wait_fiscal_types_ready() {
        return this.fiscal_types_ready;
    },

    get_fiscal_type_by_id(id) {
        const fiscal_type = this.fiscal_types.find(ft => ft.id === id);
        return fiscal_type || this.get_fiscal_type_by_prefix('B02');
    },

    get_fiscal_type_by_prefix(prefix) {
        const fiscal_type = this.fiscal_types.find(ft => ft.prefix === prefix);
        if (fiscal_type) {
            return fiscal_type;
        }

        this.env.services.dialog.add(AlertDialog,
            {
                'title': _t('Fiscal type not found'),
                'body': _t('This fiscal type not exist.'),
            });
        return false;
    },

    get_fiscal_data(order) {
        return this.env.services.orm.call(
            "pos.order",
            "get_next_fiscal_sequence",
            [
                false,
                order.fiscal_type.id,
                this.env.pos.company.id,
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
        this.env.pos.payment_methods.forEach(
            function (payment_method) {
                if (payment_method.is_credit_note) {
                    credit_note_payment_method = payment_method;
                }
            }
        );
        return credit_note_payment_method;
    },

    get_credit_note(ncf) {
        return this.env.services.orm.call(
            'pos.order',
            'get_credit_note',
            [
                false,
                ncf
            ],
        );
    },

    get_credit_notes(partner_id) {
        return this.env.services.orm.call(
            'pos.order',
            'get_credit_notes',
            [
                false,
                partner_id
            ],
        );
    }
});
