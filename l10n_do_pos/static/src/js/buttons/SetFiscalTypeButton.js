import { Component } from "@odoo/owl";
import { usePos } from "@point_of_sale/app/store/pos_hook";
import { _t } from "@web/core/l10n/translation";
import { makeAwaitable } from "@point_of_sale/app/store/make_awaitable_dialog";
import { AlertDialog } from "@web/core/confirmation_dialog/confirmation_dialog";
import { useService } from "@web/core/utils/hooks";
import { SelectionPopup } from "@point_of_sale/app/utils/input_popups/selection_popup";
import { TextInputPopup } from "@point_of_sale/app/utils/input_popups/text_input_popup";

export class SetFiscalTypeButton extends Component {
    static template = "l10n_do_pos.SetFiscalTypeButton";
    static props = {};

    setup() {
        this.pos = usePos();
        this.dialog = useService("dialog");
    }

    get currentOrder() {
        return this.pos.get_order();
    }

    get currentFiscalTypeName() {
        return this.currentOrder && this.currentOrder.fiscal_type
            ? this.currentOrder.fiscal_type.name
            : _t('Select Fiscal Type');
    }

    async onClick() {
        const currentFiscalType = this.currentOrder.fiscal_type;
        const fiscalPosList = [];
        for (let fiscalPos of this.pos.fiscal_types) {
            if (fiscalPos.type !== 'out_invoice') continue;
            fiscalPosList.push({
                id: fiscalPos.id,
                label: fiscalPos.name,
                isSelected: currentFiscalType
                    ? fiscalPos.id === currentFiscalType.id
                    : false,
                item: fiscalPos,
            });
        }

        const selectedFiscalType = await makeAwaitable(this.dialog, SelectionPopup, {
            title: _t('Select Fiscal Type'),
            list: fiscalPosList,
        }
        );

        if (selectedFiscalType) {
            var partner = this.currentOrder.get_partner();
            if (selectedFiscalType.requires_document && (!partner || !partner.vat))
                await this.open_vat_popup();

            this.currentOrder.set_fiscal_type(selectedFiscalType);
        }
    }

    async open_vat_popup() {
        const vat = await makeAwaitable(this.dialog, TextInputPopup, {
            title: _t('You need to select a customer with RNC or Cedula for this fiscal type.'),
            placeholder: _t('RNC or Cedula'),
        });

        if (vat) {
            if (!(vat.length === 9 || vat.length === 11) || Number.isNaN(Number(vat))) {
                this.dialog.add(AlertDialog, {
                    title: _t('This not RNC or Cedula'),
                    body: _t('Please ensure the RNC has exactly 9 digits or the Cedula has 11 digits'),
                    cancel: function () {
                        self.open_vat_popup();
                    },
                });

            } else {
                // TODO: in future try optimize search partners like get_partner_by_id
                var partner = this.pos.models["res.partner"].find((partner_obj) => partner_obj.vat === vat);

                if (partner) {
                    this.currentOrder.set_partner(partner);
                } else {
                    // TODO: in future create automatic partner
                    this.dialog.add(AlertDialog, {
                        title: _t('There are no partners with this RNC'),
                        body: _t('Please register the partner to continue with billing.'),
                        confirm: () => {
                            this.pos.selectPartner();
                            return;
                        },
                    });
                }
            }
        }
    }
}
