import { Component, useState } from "@odoo/owl";
import { usePos } from "@point_of_sale/app/store/pos_hook";
import { patch } from "@web/core/utils/patch";
import { PaymentScreen } from "@point_of_sale/app/screens/payment_screen/payment_screen";

patch(PaymentScreen.prototype, {
    setup() {
        super.setup();
        this.pos = usePos();
        //this.currentOrder = this.pos.get_order();
    },

    selectPartner2() {
        console.log("✅ selectPartner2 ejecutado");
        console.log("Orden actual:", this.currentOrder);
        console.log("Cliente actual:", this.currentOrder.get_partner());
    },
});

// TEST 2
// export class FiscalTypeButton extends Component {
//     setup() {
//         this.pos = usePos();
//         this.currentOrder = this.pos.get_order();
//     }
//     selectPartner2() {
//         console.log("selectPartner2");
//     }
// }

// TEST 1
// patch(PaymentScreen.prototype, {
//     setup() {
//         this.pos = usePos();
//     }
// });


////NOT WORK!!!