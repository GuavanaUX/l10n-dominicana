console.log("Hello from CustomReceiptHeader.js");

import { _t } from "@web/core/l10n/translation";
import { Component, useState } from "@odoo/owl";
import { usePos } from "@point_of_sale/app/store/pos_hook";
import { useService } from "@web/core/utils/hooks";
import { PosOrder } from "@point_of_sale/app/models/pos_order";
import { patch } from "@web/core/utils/patch";

patch(PosOrder.prototype, {
    export_for_printing(baseUrl, headerData) {
        const results = super.export_for_printing(...arguments);
        console.log(results);

        if (this.get_partner()) {
            results.headerData.partner = this.get_partner();
            //returns.headerData.orderLine = this.get_orderlines();
        }

        return results;
    }
})