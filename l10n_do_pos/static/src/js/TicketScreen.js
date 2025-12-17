import { TicketScreen } from "@point_of_sale/app/screens/ticket_screen/ticket_screen";
import { AlertDialog } from "@web/core/confirmation_dialog/confirmation_dialog";
import { patch } from "@web/core/utils/patch";
import { _t } from "@web/core/l10n/translation";

patch(TicketScreen.prototype, {

    async onDoRefund() {
        const order = this.getSelectedOrder();
        if (order && this._doesOrderHaveSoleItem(order)) {
            if (!this._prepareAutoRefundOnOrder(order)) {
                return;
            }
        }

        if (!order || !this.getHasItemsToRefund()) {
            return;
        }

        if (this.pos.config.l10n_do_fiscal_journal){
            const refund_fiscal_type = order.get_fiscal_type_by_prefix('B04');
            const credit_note_payment_method = this.pos.get_credit_note_payment_method();

            if (!credit_note_payment_method) {
                this.dialog.add(AlertDialog, {
                    title: _t("Error"),
                    body: _t(
                        'There are no credit note payment method configured.'
                    ),
                });
                return;
            }

            if(!refund_fiscal_type){
                this.dialog.add(AlertDialog, {
                    title: _t("Error"),
                    body: _t(
                        'The fiscal type credit note does not exist. Please activate or configure it.'
                    ),
                });
                return;
            }

            if (order.ncf == '') {
                this.dialog.add(AlertDialog, {
                    title: _t("Error"),
                    body: _t(
                        'This order has no NCF'
                    ),
                });
                return;
            }
        }
        //TODO: check updatePricelist
        await super.onDoRefund(...arguments);
    },

    async closeTicketScreen() {
        var new_order = this.pos.get_order();
        const order = this.getSelectedOrder();
        if (new_order && this.pos.config.l10n_do_fiscal_journal && new_order._isRefundOrder() && order.ncf){

            try {
                const refund_fiscal_type = order.get_fiscal_type_by_prefix('B04');
                const credit_note_payment_method = this.pos.get_credit_note_payment_method();
                new_order.set_ncf_origin_out(order.ncf);
                new_order.set_fiscal_type(refund_fiscal_type);
                // Convert the date string to a Date object
                const orderDate = new Date(order.validation_date);
                // Get the current date
                const currentDate = new Date();
                // Calculate the time difference in milliseconds
                const timeDifferenceMilliseconds = currentDate - orderDate;
                // Calculate the time difference in days
                const timeDifferenceDays = timeDifferenceMilliseconds / (1000 * 60 * 60 * 24);
                // Check if the difference is greater than 30 days and clear the tax_ids if so
                if (timeDifferenceDays > 30) {
                    // Iterate through each orderline in new_order and clear the tax_ids

                    // TODO: only remove ITBIS tax
                    new_order.lines.forEach(orderline => {
                        orderline.tax_ids = [];
                    });
                }
                new_order.add_paymentline(credit_note_payment_method);
                // TODO: maybe do not need this validation
                // var fiscal_data = await this.pos.get_fiscal_data(new_order);
                // console.log('NCF Generated', fiscal_data);
                // new_order.ncf = fiscal_data.ncf;
                // new_order.fiscal_type_id = new_order.fiscal_type;
                // new_order.ncf_expiration_date = fiscal_data.ncf_expiration_date;
                // new_order.fiscal_sequence_id = fiscal_data.fiscal_sequence_id;
                // console.log('GO TO VALIDATE ORDER', this)

            } catch (error) {
                // TODO: when error show ticket screen
                this.pos.add_new_order();
                this.pos.deleteOrders(new_order);
                throw error;
            }
        }
        super.closeTicketScreen(...arguments);
    },

    _getSearchFields() {
        if (!this.pos.config.l10n_do_fiscal_journal) {
            return super._getSearchFields(...arguments);
        }
        return Object.assign({}, super._getSearchFields(...arguments), {
            NCF: {
                repr: (order) => order.ncf,
                displayName: _t("NCF"),
                modelField: "ncf",
            },
        });
    },

    _returnAllOrder(){
        console.log('returnAll')
        const order = this.getSelectedOrder();
        if (!order) return NumberBuffer.reset();

        for (const orderline of order.lines) {
            const toRefundDetail = this.getToRefundDetail(orderline);
            const refundableQty = toRefundDetail.line.qty - toRefundDetail.line.refunded_qty;
            if (refundableQty > 0) {
                toRefundDetail.qty = refundableQty;
            }
        }
    },
});
