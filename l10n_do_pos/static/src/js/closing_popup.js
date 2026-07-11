import { ClosePosPopup } from "@point_of_sale/app/navbar/closing_popup/closing_popup";
import { patch } from "@web/core/utils/patch";
import { useState } from "@odoo/owl";

patch(ClosePosPopup.prototype, {
    setup() {
        super.setup();
        this.closingState = useState({ inProgress: false });
    },
    async closeSession() {
        this.closingState.inProgress = true;
        try {
            return await super.closeSession(...arguments);
        } finally {
            this.closingState.inProgress = false;
        }
    },
    get isClosingSession() {
        return this.closingState.inProgress;
    },
});
