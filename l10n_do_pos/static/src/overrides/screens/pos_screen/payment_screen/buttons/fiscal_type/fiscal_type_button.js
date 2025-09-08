import { Component, useState } from "@odoo/owl";
import { usePos } from "@point_of_sale/app/store/pos_hook";
import { patch } from "@web/core/utils/patch";
import { PaymentScreen } from "@point_of_sale/app/screens/payment_screen/payment_screen";

export class FiscalTypeButton extends Component {
    setup() {
        this.pos = usePos();
        this.currentOrder = this.pos.get_order();
    }
}

// patch(PaymentScreen.prototype, {
//     setup() {
//         this.pos = usePos();
//     }
// });


////NOT WORK!!!