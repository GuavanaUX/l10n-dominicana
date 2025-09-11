/** @odoo-module **/

import { _t } from "@web/core/l10n/translation";
import { patch } from "@web/core/utils/patch";
import { useService } from "@web/core/utils/hooks";
import { PartnerList } from "@point_of_sale/app/screens/partner_list/partner_list";
//import { PartnerDetailsEdit } from "@point_of_sale/app/screens/partner_list/partner_details_edit";
import { isConnectionError } from "@point_of_sale/utils";

patch(PartnerList.prototype, {
    async saveChanges(event) {
        try {
            const rpc = useService("rpc");

            // Crear partner desde el UI
            const partnerId = await rpc("/web/dataset/call_kw", {
                model: "res.partner",
                method: "create_from_ui",
                args: [event.detail.processedChanges],
            });

            // Recargar partners en POS
            await this.pos.load_new_partners();

            const new_partner = this.pos.db.get_partner_by_id(partnerId);
            this.editPartner(new_partner);

            // Actualizar inputs (en caso de que existan en la vista)
            const $partner_name = document.querySelector(".partner-name");
            const $vat = document.querySelector(".vat");

            if ($partner_name) $partner_name.value = new_partner.name;
            if ($vat) $vat.value = new_partner.vat;

            this.state.selectedPartner = new_partner;
            this.props.partner = new_partner;

        } catch (error) {
            if (isConnectionError(error)) {
                await this.popup.add("OfflineErrorPopup", {
                    title: _t("Offline"),
                    body: _t("Unable to save changes."),
                });
            } else {
                throw error;
            }
        }
    },
});

// patch(PartnerDetailsEdit.prototype, {
//     saveChanges() {
//         const $partner_name = document.querySelector(".partner-name");
//         const $vat = document.querySelector(".vat");

//         if ($partner_name && $partner_name.value !== this.changes.name) {
//             this.changes.name = $partner_name.value;
//         }

//         if ($vat && $vat.value !== this.changes.vat) {
//             this.changes.vat = $vat.value;
//         }

//         super.saveChanges();
//     },
// });

// OLD CODE

// odoo.define('l10n_do_pos.PartnerListScreen', function (require) {
//     'use strict';

//     const PartnerListScreen = require('point_of_sale.PartnerListScreen');
//     const PartnerDetailsEdit = require('point_of_sale.PartnerDetailsEdit');
//     const Registries = require('point_of_sale.Registries');
//     const { isConnectionError } = require('point_of_sale.utils');
//     const { useListener } = require("@web/core/utils/hooks");
//     const { useAsyncLockedMethod } = require("point_of_sale.custom_hooks");

//     const L10nDoPosPartnerListScreen = (PartnerListScreen) =>
//         class extends PartnerListScreen {

//             async saveChanges(event) {

//                 try {
//                     let partnerId = await this.rpc({
//                         model: 'res.partner',
//                         method: 'create_from_ui',
//                         args: [event.detail.processedChanges],
//                     });
                    
//                     await this.env.pos.load_new_partners();
                    
//                     var new_partner = this.env.pos.db.get_partner_by_id(partnerId);
//                     this.editPartner(new_partner);
                    
//                     var $partner_name = $('.partner-name');
//                     var $vat = $('.vat');

//                     $partner_name.val(new_partner.name);
//                     $vat.val(new_partner.vat);

//                     this.state.selectedPartner = new_partner;
//                     this.props.partner = new_partner;
                    
//                 } catch (error) {
//                     if (isConnectionError(error)) {
//                         await this.showPopup('OfflineErrorPopup', {
//                             title: this.env._t('Offline'),
//                             body: this.env._t('Unable to save changes.'),
//                         });
//                     } else {
//                         throw error;
//                     }
//                 }
//             }
//         };

//     const L10nDoPosPartnerDetailsEdit = (PartnerDetailsEdit) => class extends PartnerDetailsEdit {
//         saveChanges() {

//             var $partner_name = $('.partner-name')
//             var $vat = $('.vat')

//             if ($partner_name && $partner_name.val() != this.changes.name){
//                 this.changes.name = $partner_name.val()
//             }

//             if ($vat && $vat.val() != this.changes.vat){
//                 this.changes.vat = $vat.val()
//             }

//             super.saveChanges();
//         }
//     };

//     Registries.Component.extend(PartnerListScreen, L10nDoPosPartnerListScreen);
//     Registries.Component.extend(PartnerDetailsEdit, L10nDoPosPartnerDetailsEdit);

//     return PartnerListScreen;
// });
