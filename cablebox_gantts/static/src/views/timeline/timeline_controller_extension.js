import {patch} from "@web/core/utils/patch";
import {TimelineController} from "@web_timeline/views/timeline/timeline_controller.esm";

patch(TimelineController.prototype, {
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

