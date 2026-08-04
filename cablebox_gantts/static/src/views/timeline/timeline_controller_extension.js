import {patch} from "@web/core/utils/patch";
import {TimelineController} from "@web_timeline/views/timeline/timeline_controller.esm";
import {onWillStart, onWillUnmount, useRef} from "@odoo/owl";
import {useModel} from "@web/model/model";
import {useSetupAction} from "@web/search/action_hook";
import {useSearchBarToggler} from "@web/search/search_bar/search_bar_toggler";
import {useDebounced} from "@web/core/utils/timing";
import {useService} from "@web/core/utils/hooks";

// Enhancements:
// 1) Keep existing custom _onGroupClick behaviour.
// 2) Add a periodic refresh so that orders which become 100% delivered
//    get removed automatically from the Gantt without a manual reload.
patch(TimelineController.prototype, {
    setup() {
        // Re-implement original TimelineController.setup logic (we can't call the
        // original function here because patching overrides it). We import the
        // small subset of hooks required and reproduce the initialization, then
        // add our interval-based auto-refresh.
        this.rootRef = useRef("root");
        this.model = useModel(this.props.Model, this.props.modelParams);
        useSetupAction({rootRef: useRef("root")});
        this.searchBarToggler = useSearchBarToggler();
        this.date_start = this.props.modelParams.date_start;
        this.date_stop = this.props.modelParams.date_stop;
        this.date_delay = this.props.modelParams.date_delay;
        this.open_popup_action = this.props.modelParams.open_popup_action;
        this.moveQueue = [];
        this.debouncedInternalMove = useDebounced(this.internalMove, 0);
        this.dialogService = useService("dialog");
        this.actionService = useService("action");

        // Start a periodic reload that will refresh the model and re-render
        // so that records that become fully delivered disappear.
        // Interval: 15 seconds (tunable)
        onWillStart(() => {
            this._cablebox_gantts_refresh_interval = setInterval(async () => {
                try {
                    await this.model.load(this.getSearchProps());
                    this.render();
                } catch (err) {
                    // ignore errors to avoid breaking the UI
                    // (network issues or temporary server problems)
                    console.warn('cablebox_gantts: auto-refresh failed', err);
                }
            }, 15000);
        });
        onWillUnmount(() => {
            if (this._cablebox_gantts_refresh_interval) {
                clearInterval(this._cablebox_gantts_refresh_interval);
                this._cablebox_gantts_refresh_interval = undefined;
            }
        });
    },

    _onGroupClick(item) {
        const groupField = this.model.last_group_bys[0];
        if (groupField === 'display_group') {
            // Si agrupamos por display_group, intentamos encontrar el pedido
            // a través de uno de los registros que pertenecen a ese grupo.
            const record = this.model.data.find(r => r.display_group === item.group);
            if (record && record.order_id) {
                const order_id = Array.isArray(record.order_id) ? record.order_id[0] : record.order_id;
                this.actionService.doAction({
                    type: "ir.actions.act_window",
                    res_model: "sale.order",
                    res_id: order_id,
                    views: [[false, "form"]],
                    view_mode: "form",
                    target: "new",
                });
                return;
            }
        }
        super._onGroupClick(...arguments);
    },
});

