/** @odoo-module **/

import { _t } from "@web/core/l10n/translation";
import { Component } from "@odoo/owl";
import { usePos } from "@point_of_sale/app/store/pos_store";
import { registry } from "@web/core/registry";
import { useListener } from "@web/core/utils/hooks";


export class SetFiscalTypeButton extends Component {
    static template = "l10n_do_pos.SetFiscalTypeButton";
    setup() {
        super.setup();
        this.pos = usePos();               // accedemos al PosStore reactivo
        this.popup = useService("popup");  // servicio de popups
        this.action = useService("action");
        useListener("click", this.onClick);
    }

    get currentOrder() {
        return this.pos.get_order();
    }

    get currentFiscalTypeName() {
        return this.currentOrder?.fiscal_type?.name || this.env._t("Select Fiscal Type");
    }

    async onClick() {
        const currentFiscalType = this.currentOrder?.fiscal_type;
        const fiscalPosList = [];

        for (let fiscalPos of this.pos.fiscal_types) {
            if (fiscalPos.type !== "out_invoice") continue;
            fiscalPosList.push({
                id: fiscalPos.id,
                label: fiscalPos.name,
                isSelected: currentFiscalType ? fiscalPos.id === currentFiscalType.id : false,
                item: fiscalPos,
            });
        }

        const { confirmed, payload: selectedFiscalType } = await this.popup.add("SelectionPopup", {
            title: this.env._t("Select Fiscal Type"),
            list: fiscalPosList,
        });

        if (confirmed) {
            const partner = this.currentOrder.get_partner();
            if (selectedFiscalType.requires_document && (!partner || !partner.vat)) {
                await this.open_vat_popup();
            }
            this.currentOrder.set_fiscal_type(selectedFiscalType);
        }
    }

    async open_vat_popup() {
        const { confirmed, payload: vat } = await this.popup.add("TextInputPopup", {
            startingValue: "",
            title: this.env._t("You need to select a customer with RNC or Cedula for this fiscal type."),
            placeholder: this.env._t("RNC or Cedula"),
        });

        if (confirmed) {
            if (!(vat.length === 9 || vat.length === 11) || Number.isNaN(Number(vat))) {
                this.popup.add("ErrorPopup", {
                    title: this.env._t("This not RNC or Cedula"),
                    body: this.env._t("Please ensure the RNC has exactly 9 digits or the Cedula has 11 digits"),
                });
                return this.open_vat_popup();
            }

            let partner = this.pos.db.get_partners_sorted().find(p => p.vat === vat);

            if (partner) {
                this.currentOrder.set_partner(partner);
            } else {
                const { confirmed, payload: newPartner } = await this.action.doAction("point_of_sale.partner_list_action", {
                    additionalContext: { partner: this.currentOrder.get_partner() },
                });
                if (confirmed) {
                    this.currentOrder.set_partner(newPartner);
                    this.currentOrder.updatePricelist(newPartner);
                }
            }
        }
    }
}

//SetFiscalTypeButton.template = "l10n_do_pos.SetFiscalTypeButton";
//registry.add(SetFiscalTypeButton);
registry.category("components").add("SetFiscalTypeButton", SetFiscalTypeButton);
