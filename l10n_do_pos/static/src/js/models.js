/** @odoo-module **/

import { _t } from "@web/core/l10n/translation";
import { patch } from "@web/core/utils/patch";
import { AlertDialog } from "@web/core/confirmation_dialog/confirmation_dialog";

import { PosStore } from "@point_of_sale/app/store/pos_store";
import { PosOrder } from "@point_of_sale/app/models/pos_order";
import { PosPayment } from "@point_of_sale/app/models/pos_payment";


patch(PosStore.prototype, {
    async setup() {
        await super.setup(...arguments);
        // Inicializar fiscal_types si no existe
        this.fiscal_types = this.models["account.fiscal.type"] || [];
    },

    get_fiscal_type_by_id(id) {
        if (!this.fiscal_types) {
            console.warn("fiscal_types not initialized yet");
            return null;
        }

        let res_fiscal_type = this.fiscal_types.find(ft => ft.id === id);
        if (!res_fiscal_type) {
            res_fiscal_type = this.get_fiscal_type_by_prefix("B02");
        }
        return res_fiscal_type;
    },

    get_fiscal_type_by_prefix(prefix) {
        if (!this.fiscal_types) {
            console.warn("fiscal_types not initialized yet");
            return this._getDefaultFiscalType();
        }

        let res_fiscal_type = this.fiscal_types.find(ft => ft.prefix === prefix);
        if (res_fiscal_type) {
            return res_fiscal_type;
        }

        // Usar el servicio dialog correctamente
        if (this.env?.services?.dialog) {
            this.env.services.dialog.add(AlertDialog, {
                title: _t("Fiscal type not found"),
                body: _t("This fiscal type does not exist."),
            });
        }
        console.error("Fiscal type not found");
        return this._getDefaultFiscalType();
    },

    // ✅ Método auxiliar para tipo fiscal por defecto
    _getDefaultFiscalType() {
        return {
            id: 0,
            name: "Default Fiscal Type",
            prefix: "B02",
            fiscal_position_id: false
        };
    },

    async get_fiscal_data(order) {
        return this.env.services.rpc({
            model: "pos.order",
            method: "get_next_fiscal_sequence",
            args: [
                false,
                order.fiscal_type.id,
                this.company.id,
                [],
            ],
        });
    },

    // ✅ Tu función principal
    isCreditNoteMode() {
        const current_order = this.get_order();
        return (
            this.config.l10n_do_fiscal_journal &&
            current_order &&
            current_order._isRefundOrder()
        );
    },

    get_credit_note_payment_method() {
        return this.payment_methods?.find(pm => pm.is_credit_note) || false;
    },

    async get_credit_note(ncf) {
        return this.env.services.rpc({
            model: "pos.order",
            method: "get_credit_note",
            args: [false, ncf],
        });
    },

    async get_credit_notes(partner_id) {
        return this.env.services.rpc({
            model: "pos.order",
            method: "get_credit_notes",
            args: [false, partner_id],
        });
    }
});

patch(PosOrder.prototype, {
    setup(obj, options) {
        super.setup(...arguments);

        if (!options?.json) {
            this.ncf = "";
            this.ncf_origin_out = "";
            this.ncf_expiration_date = "";
            this.fiscal_type_id = false;
            this.fiscal_sequence_id = false;

            // Limitar los intentos de inicialización
            this._fiscalTypeInitAttempts = 0;

            // ✅ SOLUCIÓN: Diferir la configuración del fiscal type
            this._initializeFiscalType();
        }
    },

    // ✅ Método separado para inicializar fiscal type
    _initializeFiscalType() {
        if (this._fiscalTypeInitAttempts > 10) {
            console.error("No se pudo inicializar el fiscal type después de varios intentos.");
            return;
        }
        this._fiscalTypeInitAttempts++;

        // Verificar que pos esté disponible
        if (!this.pos) {
            console.warn("POS not available during order initialization, deferring fiscal type setup");
            // Intentar de nuevo en el siguiente tick
            setTimeout(() => this._initializeFiscalType(), 0);
            return;
        }

        // Verificar que los métodos del pos estén disponibles
        if (typeof this.pos.get_fiscal_type_by_id !== 'function') {
            console.warn("Fiscal type methods not available yet, deferring setup");
            setTimeout(() => this._initializeFiscalType(), 100);
            return;
        }

        const partner = this.get_partner();

        if (partner && partner.sale_fiscal_type_id) {
            const fiscalType = this.pos.get_fiscal_type_by_id(partner.sale_fiscal_type_id[0]);
            if (fiscalType) {
                this.set_fiscal_type(fiscalType);
            }
        } else {
            // ✅ FIX: Acceso seguro al PosStore
            const defaultFiscalType = this.pos.get_fiscal_type_by_prefix("B02");
            if (defaultFiscalType) {
                this.set_fiscal_type(defaultFiscalType);
            }
        }
    },

    set_fiscal_type(fiscal_type) {
        if (!fiscal_type) {
            console.warn("Attempting to set null fiscal type");
            return;
        }

        this.fiscal_type = fiscal_type;
        this.fiscal_type_id = fiscal_type.id;

        if (fiscal_type && fiscal_type.fiscal_position_id) {
            const fiscalPosition = this.pos?.fiscal_positions?.find(
                fp => fp.id === fiscal_type.fiscal_position_id[0]
            );
            if (fiscalPosition) {
                this.set_fiscal_position(fiscalPosition);
                for (let line of this.get_orderlines()) {
                    line.set_quantity(line.quantity);
                }
            }
        }
    },

    get_fiscal_type() {
        return this.fiscal_type;
    },

    set_partner(partner) {
        super.set_partner(partner);

        // ✅ Verificar que pos esté disponible
        if (!this.pos || typeof this.pos.get_fiscal_type_by_id !== 'function') {
            console.warn("POS not ready for fiscal type operations");
            return;
        }

        if (partner && partner.sale_fiscal_type_id) {
            const fiscalType = this.pos.get_fiscal_type_by_id(partner.sale_fiscal_type_id[0]);
            if (fiscalType) {
                this.set_fiscal_type(fiscalType);
            }
        } else {
            const defaultFiscalType = this.pos.get_fiscal_type_by_prefix("B02");
            if (defaultFiscalType) {
                this.set_fiscal_type(defaultFiscalType);
            }
        }
    },

    export_as_JSON() {
        const json = super.export_as_JSON(...arguments);

        if (this.pos?.config?.l10n_do_fiscal_journal) {
            json.ncf = this.ncf;
            json.ncf_origin_out = this.ncf_origin_out;
            json.ncf_expiration_date = this.ncf_expiration_date;
            json.fiscal_type_id = this.fiscal_type_id;
            json.fiscal_sequence_id = this.fiscal_sequence_id;
        }
        return json;
    },

    init_from_JSON(json) {
        super.init_from_JSON(...arguments);

        if (this.pos?.config?.l10n_do_fiscal_journal) {
            this.ncf = json.ncf || "";
            this.ncf_origin_out = json.ncf_origin_out || "";
            this.ncf_expiration_date = json.ncf_expiration_date || "";
            this.fiscal_type_id = json.fiscal_type_id || false;
            this.fiscal_sequence_id = json.fiscal_sequence_id || false;

            // ✅ Verificar disponibilidad antes de usar
            if (json.fiscal_type_id && this.pos && typeof this.pos.get_fiscal_type_by_id === 'function') {
                const fiscalType = this.pos.get_fiscal_type_by_id(json.fiscal_type_id);
                if (fiscalType) {
                    this.set_fiscal_type(fiscalType);
                }
            }
            if (json.fiscal_type) {
                this.set_fiscal_type(json.fiscal_type);
            }
        }
    },

    set_ncf_origin_out(ncf_origin_out) {
        this.ncf_origin_out = ncf_origin_out;
    },
});

patch(PosPayment.prototype, {
    setup(obj, options) {
        super.setup(...arguments);
        this.credit_note_ncf = this.credit_note_ncf || "";
        this.credit_note_partner_id = this.credit_note_partner_id || false;
    },

    export_as_JSON() {
        const json = super.export_as_JSON(...arguments);
        json.credit_note_ncf = this.credit_note_ncf;
        json.credit_note_partner_id = this.credit_note_partner_id;
        return json;
    },

    init_from_JSON(json) {
        super.init_from_JSON(...arguments);
        this.credit_note_ncf = json.credit_note_ncf;
        this.credit_note_partner_id = json.credit_note_partner_id;
    },

    set_fiscal_data(ncf, partner_id) {
        this.credit_note_ncf = ncf;
        this.credit_note_partner_id = partner_id;
    },
});




// odoo.define('l10n_do_pos.models', function (require) {
//     "use strict";

//     var { Order, PosGlobalState, Payment } = require('point_of_sale.models');
//     var Registries = require('point_of_sale.Registries');

//     const L10nDoPosPosGlobalState = PosGlobalState => class extends PosGlobalState {
//         async _processData(loadedData) {
//             await super._processData(loadedData);
//             this.fiscal_types = loadedData['account.fiscal.type']
//         }

//         get_fiscal_type_by_id(id) {
//             var self = this;
//             var res_fiscal_type = false;
//             self.fiscal_types.forEach(function (fiscal_type) {
//                 if (fiscal_type.id === id) {
//                     res_fiscal_type = fiscal_type;
//                 }
//             });
//             if (!res_fiscal_type) {
//                 res_fiscal_type = this.get_fiscal_type_by_prefix('B02');
//             }
//             return res_fiscal_type;
//         }

//         get_fiscal_type_by_prefix(prefix) {
//             var self = this;
//             var res_fiscal_type = false;
//             // TODO: try make at best performance
//             self.fiscal_types.forEach(function (fiscal_type) {
//                 if (fiscal_type.prefix === prefix) {
//                     res_fiscal_type = fiscal_type;
//                 }
//             });
//             if (res_fiscal_type) {
//                 return res_fiscal_type;
//             }
//             self.gui.show_popup('error', {
//                 'title': _t('Fiscal type not found'),
//                 'body': _t('This fiscal type not exist.'),
//             });
//             return false;
//         }
//         async get_fiscal_data(order) {
//             return this.env.services.rpc({
//                 model: 'pos.order',
//                 method: 'get_next_fiscal_sequence',
//                 args: [
//                     false,
//                     order.fiscal_type.id,
//                     this.env.pos.company.id,
//                     [],
//                 ],
//             });
//         }
//         isCreditNoteMode() {
//             const current_order = this.env.pos.get_order();
//             return this.env.pos.config.l10n_do_fiscal_journal && current_order && current_order._isRefundAndSaleOrder();
//         }
//         get_credit_note_payment_method() {
//             var credit_note_payment_method = false;

//             this.env.pos.payment_methods.forEach(
//                 function (payment_method) {
//                     if (payment_method.is_credit_note) {
//                         credit_note_payment_method = payment_method;
//                     }
//                 }
//             );

//             return credit_note_payment_method;
//         }
//         async get_credit_note(ncf) {
//             return this.env.services.rpc({
//                 model: 'pos.order',
//                 method: 'get_credit_note',
//                 args: [
//                     false,
//                     ncf
//                 ],
//             });
//         }
//         async get_credit_notes(partner_id) {
//             return this.env.services.rpc({
//                 model: 'pos.order',
//                 method: 'get_credit_notes',
//                 args: [
//                     false,
//                     partner_id
//                 ],
//             });
//         }

//     }

//     const L10nDoPosOrder = Order => class extends Order {
//         /**
//          * @override
//          */
//         constructor(obj, options) {
//             super(...arguments);

//             if (!options.json) {
//                 this.ncf = '';
//                 this.ncf_origin_out = '';
//                 this.ncf_expiration_date = '';
//                 this.fiscal_type_id = false;
//                 this.fiscal_sequence_id = false;

//                 var partner = this.get_partner();

//                 if (partner && partner.sale_fiscal_type_id) {

//                     this.set_fiscal_type(this.pos.get_fiscal_type_by_id(partner.sale_fiscal_type_id[0]));

//                 } else {

//                     this.set_fiscal_type(this.pos.get_fiscal_type_by_prefix('B02'))

//                 }
//             }

//         }

//         set_fiscal_type(fiscal_type) {
//             this.fiscal_type = fiscal_type;
//             this.fiscal_type_id = fiscal_type.id;
//             if (fiscal_type && fiscal_type.fiscal_position_id) {
//                 this.set_fiscal_position(_.find(this.pos.fiscal_positions, function (fp) {
//                     return fp.id === fiscal_type.fiscal_position_id[0];
//                 }));
//                 for (let line of this.get_orderlines()) {
//                     line.set_quantity(line.quantity);
//                 }
//             }
//         }

//         get_fiscal_type() {
//             return this.fiscal_type;
//         }
//         set_partner(partner) {

//             super.set_partner(partner);

//             if (partner && partner.sale_fiscal_type_id) {
//                 this.set_fiscal_type(this.pos.get_fiscal_type_by_id(partner.sale_fiscal_type_id[0]));
//             } else {
//                 this.set_fiscal_type(this.pos.get_fiscal_type_by_prefix('B02'));
//             }
//         }

//         //@override
//         export_as_JSON() {
//             const json = super.export_as_JSON(...arguments);

//             if (this.pos.config.l10n_do_fiscal_journal) {
//                 json.ncf = this.ncf;
//                 json.ncf_origin_out = this.ncf_origin_out;
//                 json.ncf_expiration_date = this.ncf_expiration_date;
//                 json.fiscal_type_id = this.fiscal_type_id;
//                 json.fiscal_sequence_id = this.fiscal_sequence_id;
//             }

//             return json;
//         }

//         init_from_JSON(json) {
//             super.init_from_JSON(...arguments);
//             if (this.pos.config.l10n_do_fiscal_journal) {
//                 this.ncf = json.ncf || '';
//                 this.ncf_origin_out = json.ncf_origin_out || '';
//                 this.ncf_expiration_date = json.ncf_expiration_date || '';
//                 this.fiscal_type_id = json.fiscal_type_id || false;
//                 this.fiscal_sequence_id = json.fiscal_sequence_id || false;
//                 console.log('init_from_JSON', json.fiscal_type_id)

//                 if (json.fiscal_type_id)
//                     this.set_fiscal_type(this.pos.get_fiscal_type_by_id(json.fiscal_type_id));

//                 if (json.fiscal_type)
//                     this.set_fiscal_type(json.fiscal_type);

//             }
//         }
//         set_ncf_origin_out(ncf_origin_out) {
//             this.ncf_origin_out = ncf_origin_out;
//         }

//     }
//     const L10nDoPayment = Payment => class extends Payment {
//         /**
//          * @override
//          */
//         constructor(obj, options) {
//             super(...arguments);

//             this.credit_note_ncf = this.credit_note_ncf || '';
//             this.credit_note_partner_id = this.credit_note_partner_id || false;
//         }
//         //@override
//         export_as_JSON() {
//             const json = super.export_as_JSON(...arguments);
//             json.credit_note_ncf = this.credit_note_ncf;
//             json.credit_note_partner_id = this.credit_note_partner_id;
//             return json;
//         }
//         //@override
//         init_from_JSON(json) {
//             super.init_from_JSON(...arguments);
//             this.credit_note_ncf = json.credit_note_ncf;
//             this.credit_note_partner_id = json.credit_note_partner_id;
//         }
//         set_fiscal_data(ncf, partner_id) {
//             this.credit_note_ncf = ncf;
//             this.credit_note_partner_id = partner_id;
//         }
//     }

//     Registries.Model.extend(PosGlobalState, L10nDoPosPosGlobalState);
//     Registries.Model.extend(Order, L10nDoPosOrder);
//     Registries.Model.extend(Payment, L10nDoPayment);

// });
