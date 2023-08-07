odoo.define('l10n_do_pos.models', function (require) {
    "use strict";

    var { Order, PosGlobalState } = require('point_of_sale.models');
    var Registries = require('point_of_sale.Registries');

    const L10nDoPosPosGlobalState = (PosGlobalState) => class L10nDoPosPosGlobalState extends PosGlobalState {
        async _processData(loadedData) {
            await super._processData(loadedData);
            this.fiscal_types = loadedData['account.fiscal.type']
        }

        get_fiscal_type_by_id(id) {
            var self = this;
            var res_fiscal_type = false;
            self.fiscal_types.forEach(function (fiscal_type) {
                if (fiscal_type.id === id) {
                    res_fiscal_type = fiscal_type;
                }
            });
            if (!res_fiscal_type) {
                res_fiscal_type = this.get_fiscal_type_by_prefix('B02');
            }
            return res_fiscal_type;
        }

        get_fiscal_type_by_prefix(prefix) {
            var self = this;
            var res_fiscal_type = false;
            // TODO: try make at best performance
            self.fiscal_types.forEach(function (fiscal_type) {
                if (fiscal_type.prefix === prefix) {
                    res_fiscal_type = fiscal_type;
                }
            });
            if (res_fiscal_type) {
                return res_fiscal_type;
            }
            self.gui.show_popup('error', {
                'title': _t('Fiscal type not found'),
                'body': _t('This fiscal type not exist.'),
            });
            return false;
        }

    }

    const L10nDoPosOrder = (Order) => class L10nDoPosOrder extends Order {
        /**
         * @override
         */
        constructor(obj, options) {
            super(...arguments); 

            var self = this;
            this.ncf = '';
            this.ncf_origin_out = '';
            this.ncf_expiration_date = '';
            this.fiscal_type_id = false;
            this.fiscal_sequence_id = false;
            this.fiscal_type = self.pos.get_fiscal_type_by_prefix(
                'B02'
            );
            // self.set_fiscal_position_auto = false;
            // if (this.get_mode() === 'return') {

            //     this.fiscal_type =
            //         self.pos.get_fiscal_type_by_prefix(
            //             'B04'
            //         );

            // } else if (client) {
            //     if (client.sale_fiscal_type_id) {
            //         this.fiscal_type =
            //             self.pos.get_fiscal_type_by_id(
            //                 client.sale_fiscal_type_id[0]
            //             );
            //     } else {
            //         this.fiscal_type =
            //             self.pos.get_fiscal_type_by_prefix(
            //                 'B02'
            //             );
            //     }
            // }
        }

        set_fiscal_type(fiscal_type) {
            this.fiscal_type = fiscal_type;
            if (fiscal_type && fiscal_type.fiscal_position_id){
                this.set_fiscal_position(_.find(this.pos.fiscal_positions, function(fp) {
                    return fp.id === fiscal_type.fiscal_position_id[0];
                }));
                for (let line of this.get_orderlines()) {
                    line.set_quantity(line.quantity);
                }
            }
        }

        get_fiscal_type() {
            return this.fiscal_type;
        }
        set_partner(partner){
            super.set_partner(partner); 
            console.log(this)
            if (partner && partner.sale_fiscal_type_id) { 
                this.set_fiscal_type(this.pos.get_fiscal_type_by_id(partner.sale_fiscal_type_id[0]));
            } else {
                this.set_fiscal_type(this.pos.get_fiscal_type_by_prefix('B02'));
            }
        }

        // export_as_JSON() {

        //     var self = this;
        //     var loaded = _super_order.export_as_JSON.call(this);
        //     var current_order = self.pos.get_order();

        //     if (self.pos.get_order()) {
        //         loaded.ncf = current_order.ncf;
        //         loaded.ncf_origin_out = current_order.ncf_origin_out;
        //         loaded.ncf_expiration_date = current_order.ncf_expiration_date;
        //         loaded.fiscal_type_id = current_order.fiscal_type_id;
        //         loaded.fiscal_sequence_id = current_order.fiscal_sequence_id;
        //     }

        //     return loaded;
        // }

        // TODO: Try for return order
        // For returned order (credit note)
        // add_payment_credit_note(credit_note_ncf, cashregister) {
        //     var self = this;
        //     var payment_lines = self.get_paymentlines();
        //     var is_on_payment_line = false;

        //     payment_lines.forEach(
        //         function (payment_line) {
        //             if (payment_line.get_returned_ncf()) {
        //                 if (payment_line.get_returned_ncf() ===
        //                     credit_note_ncf) {
        //                     is_on_payment_line = true;
        //                 }
        //             }
        //         });

        //     if (is_on_payment_line) {

        //         self.pos.gui.show_popup('error', {
        //             'title': _t('The credit note is in the order'),
        //             'body': _t('Credit note ' + credit_note_ncf +
        //                 ' is in the order, please try again'),
        //         });

        //         return false;

        //     }
        //     // TODO: esta parte podria buscar mejor por la factura y
        //     //  no por la orden
        //     var domain = [
        //         ['ncf', '=', credit_note_ncf],
        //         ['returned_order', '=', true],
        //         ['is_used_in_order', '=', false],
        //     ];
        //     self.pos.loading_screen_on();
        //     rpc.query({
        //         model: 'pos.order',
        //         method: 'search_read',
        //         args: [domain],
        //         limit: 1,
        //     } {
        //         timeout: 3000,
        //         shadow: true, 
        //     }).then(function (result) {

        //         if (result.length > 0) {
        //             self.add_paymentline(cashregister);
        //             var select_paymentline = self.selected_paymentline;
        //             select_paymentline.set_returned_ncf(credit_note_ncf);
        //             select_paymentline.set_returned_order_amount(
        //                 -1 * result[0].amount_total
        //             );
        //             select_paymentline.set_amount(
        //                 -1 * result[0].amount_total
        //             );
        //             self.pos.gui.screen_instances
        //                 .payment.reset_input();
        //             self.pos.gui.screen_instances
        //                 .payment.render_paymentlines();
        //             self.pos.loading_screen_off();

        //         } else {
        //             self.pos.loading_screen_off();
        //             self.pos.gui.show_popup('error', {
        //                 'title': _t('Not exist'),
        //                 'body': _t('Credit mote number ' + credit_note_ncf +
        //                     ' does exist'),
        //             });
        //         }
        //     } function (err, ev) {
        //         self.pos.loading_screen_off();
        //         console.log(err);
        //         console.log(ev);
        //         ev.preventDefault();
        //         var error_body =
        //             _t('Your Internet connection is probably down.');
        //         if (err.data) {
        //             var except = err.data;
        //             error_body = except.arguments ||
        //                 except.message || error_body;
        //         }
        //         self.gui.show_popup('error', {
        //             'title': _t('Error: Could not Save Changes'),
        //             'body': error_body,
        //         });
        //     });
        // }
    }

    // var models = require('point_of_sale.models');
    // var core = require('web.core');
    // var _t = core._t;
    // var rpc = require('web.rpc');
    // var _super_order = models.Order.prototype;

    // models.load_fields('res.partner', ['sale_fiscal_type_id']);
    // models.load_fields('account.journal', ['is_for_credit_notes']);
    // models.load_fields('account.tax', ['tax_group_id']);

    // models.load_models({
    //     model: 'account.journal',
    //     fields: ['name', 'l10n_do_fiscal_journal'],
    //     domain(self) {
    //         return [['id', '=', self.config.invoice_journal_id[0]]];
    //     }
    //     loaded(self, journals) {
    //         self.invoice_journal = false;
    //         if (journals[0]) {
    //             self.invoice_journal = journals[0];
    //         }
    //     }
    // });

    // models.load_models({
    //     model: 'account.fiscal.sequence',
    //     fields: ['name', 'fiscal_type_id'],
    //     domain(self) {
    //         return [
    //             ['state', '=', 'active'],
    //             ['type', 'in', ['out_invoice', 'out_refund']],
    //             ['company_id', '=', self.company.id],
    //         ];
    //     }
    //     loaded(self, fiscal_sequences) {
    //         self.fiscal_sequences = fiscal_sequences;
    //     }
    // });


    // var _paylineproto = models.Paymentline.prototype;
    // models.Paymentline = models.Paymentline.extend({
    //     initialize() {
    //         _paylineproto.initialize.apply(this, arguments);
    //         this.returned_ncf = null;
    //         this.returned_order_amount = 0;
    //     }

    //     set_returned_ncf(returned_move_name) {
    //         this.returned_ncf = returned_move_name;
    //     }
    //     get_returned_ncf() {
    //         return this.returned_ncf;
    //     }
    //     set_returned_order_amount(returned_order_amount) {
    //         this.returned_order_amount = returned_order_amount;
    //     }
    //     get_returned_order_amount() {
    //         return this.returned_order_amount;
    //     }
    //     export_as_JSON() {
    //         var loaded = _paylineproto.export_as_JSON.call(this);
    //         loaded.returned_ncf = this.get_returned_ncf();
    //         return loaded;
    //     }
    // });

    // return models;
    Registries.Model.extend(PosGlobalState, L10nDoPosPosGlobalState);
    Registries.Model.extend(Order, L10nDoPosOrder);

});
