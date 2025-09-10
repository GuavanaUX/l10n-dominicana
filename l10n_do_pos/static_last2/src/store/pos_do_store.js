import { _t } from "@web/core/l10n/translation";
import { Reactive } from "@web/core/utils/reactive";
import { registry } from "@web/core/registry";

export class PosDoStore extends Reactive {

    static serviceDependencies = ["pos_data"];

    constructor() {
        super();
        //this.env = env;
        //this.pos = pos;
        //this.setup();
        this.ready = this.setup(...arguments).then(() => this);
    }

    async setup(env, { pos_data }) {
        this.env = env;
        this.data = pos_data;
        console.log(this.data.models);
    }
}

export const posDoService = {
    dependencies: PosDoStore.serviceDependencies,
    async start(env, deps) {
        return new PosDoStore(env, deps).ready;
    },
};

registry.category("services").add("posDoService", posDoService);