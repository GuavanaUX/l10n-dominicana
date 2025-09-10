import { PaymentScreen } from "@point_of_sale/app/screens/payment_screen/payment_screen";
import { patch } from "@web/core/utils/patch";
import { _t } from "@web/core/l10n/translation";
import { AlertDialog } from "@web/core/confirmation_dialog/confirmation_dialog";

patch(PaymentScreen.prototype, {
    async validateOrder(isForceValidate) {
        const order = this.currentOrder;

        if (order.get_partner() === undefined) {
            this.env.services.dialog.add(AlertDialog, {
                title: _t('Warning'),
                body: _t('The customer is mandatory.')
            });

            return false;
        }

        return await super.validateOrder(...arguments);
    }
});