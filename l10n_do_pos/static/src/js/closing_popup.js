import { ClosePosPopup } from "@point_of_sale/app/navbar/closing_popup/closing_popup";
import { patch } from "@web/core/utils/patch";
import { ConnectionLostError } from "@web/core/network/rpc";
import { deduceUrl } from "@point_of_sale/utils";
import { parseFloat } from "@web/views/fields/parsers";

patch(ClosePosPopup.prototype, {
    async closeSession() {
        if (!this.pos.config.l10n_do_fiscal_journal) {
            return await super.closeSession(...arguments);
        }

        this.pos._resetConnectedCashier();
        if (this.pos.config.customer_display_type === "proxy") {
            const proxyIP = this.pos.getDisplayDeviceIP();
            fetch(`${deduceUrl(proxyIP)}/hw_proxy/customer_facing_display`, {
                method: "POST",
                headers: {
                    Accept: "application/json",
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({ params: { action: "close" } }),
                targetAddressSpace: odoo.use_lna ? "local" : undefined,
            }).catch(() => {
                console.log("Failed to send data to customer display");
            });
        }

        const syncSuccess = await this.pos.push_orders_with_closing_popup();
        if (!syncSuccess) {
            return;
        }

        if (this.pos.config.cash_control) {
            const response = await this.pos.data.call(
                "pos.session",
                "post_closing_cash_details",
                [this.pos.session.id],
                {
                    counted_cash: parseFloat(
                        this.state.payments[this.props.default_cash_details.id].counted
                    ),
                }
            );
            if (!response.successful) {
                return this.handleClosingError(response);
            }
        }

        try {
            await this.pos.data.call("pos.session", "update_closing_control_state_session", [
                this.pos.session.id,
                this.state.notes,
            ]);
        } catch (error) {
            if (!error.data && error.data.message !== "This session is already closed.") {
                throw error;
            }
        }

        try {
            const bankPaymentMethodDiffPairs = this.props.non_cash_payment_methods
                .filter((pm) => pm.type == "bank")
                .map((pm) => [pm.id, this.getDifference(pm.id)]);
            const response = await this.pos.data.call(
                "pos.session",
                "close_session_from_ui",
                [this.pos.session.id, bankPaymentMethodDiffPairs],
                {
                    context: {
                        login_number: odoo.login_number,
                    },
                }
            );
            if (!response.successful) {
                return this.handleClosingError(response);
            }
            localStorage.removeItem(`pos.session.${odoo.pos_config_id}`);
            this.pos.redirectToBackend();
        } catch (error) {
            if (error instanceof ConnectionLostError) {
                throw error;
            } else {
                await this.handleClosingControlError();
            }
        }
    },
});
