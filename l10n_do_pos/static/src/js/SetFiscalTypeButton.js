/** @odoo-module */

import { Component } from "@odoo/owl";
import { useService, useListener } from "@web/core/utils/hooks";
import { _t } from "@web/core/l10n/translation";
import { SelectionPopup } from "@point_of_sale/app/utils/input_popups/selection_popup";
import { TextInputPopup } from "@point_of_sale/app/utils/input_popups/text_input_popup";
import { PartnerListScreen } from "@point_of_sale/app/screens/partner_list/partner_list";
import { usePos } from "@point_of_sale/app/store/pos_hook";
//import { registry } from "@web/core/registry";

export class SetFiscalTypeButton extends Component {
    static template = "l10n_do_pos.SetFiscalTypeButton";

    setup() {
        super.setup();
        useListener("click", this.onClick);
        this.popup = useService("popup");
        this.orm = useService("orm");
        this.ui = useService("ui");
        this.pos = usePos(); // Usa el hook para acceder a la instancia de POS
    }

    get currentOrder() {
        return this.pos.get_order();
    }

    get currentFiscalTypeName() {
        return this.currentOrder && this.currentOrder.fiscal_type
            ? this.currentOrder.fiscal_type.name
            : _t("Select Fiscal Type");
    }

    async onClick() {
        const currentFiscalType = this.currentOrder.fiscal_type;
        const fiscalPosList = [];

        for (let fiscalPos of this.pos.fiscal_types) {
            if (fiscalPos.type !== "out_invoice") {
                continue;
            }
            fiscalPosList.push({
                id: fiscalPos.id,
                label: fiscalPos.name,
                isSelected: currentFiscalType ? fiscalPos.id === currentFiscalType.id : false,
                item: fiscalPos,
            });
        }

        const { confirmed, payload: selectedFiscalType } = await this.popup.add(SelectionPopup, {
            title: _t("Select Fiscal Type"),
            list: fiscalPosList,
        });

        if (confirmed) {
            const partner = this.currentOrder.get_partner();

            if (selectedFiscalType.requires_document && (!partner || !partner.vat)) {
                await this._openVatPopup();
            }

            this.currentOrder.set_fiscal_type(selectedFiscalType);
        }
    }

    async _openVatPopup() {
        const { confirmed, payload: vat } = await this.popup.add(TextInputPopup, {
            startingValue: "",
            title: _t("You need to select a customer with RNC or Cedula for this fiscal type."),
            placeholder: _t("RNC or Cedula"),
        });

        if (confirmed) {
            if (!(vat.length === 9 || vat.length === 11) || Number.isNaN(Number(vat))) {
                await this.popup.add(ErrorPopup, {
                    title: _t("This not RNC or Cedula"),
                    body: _t("Please ensure the RNC has exactly 9 digits or the Cedula has 11 digits"),
                });
                await this._openVatPopup();
            } else {
                const partner = this.pos.db.get_partners_sorted().find((partner_obj) => partner_obj.vat === vat);
                if (partner) {
                    this.currentOrder.set_partner(partner);
                } else {
                    const { confirmed, payload: newPartner } = await this.popup.add(PartnerListScreen, {
                        partner: this.currentOrder.get_partner(),
                    });
                    if (confirmed) {
                        this.currentOrder.set_partner(newPartner);
                        this.currentOrder.updatePricelist(newPartner);
                    }
                }
            }
        }
    }
}

//registry.category("pos_screens").add("SetFiscalTypeButton", SetFiscalTypeButton);