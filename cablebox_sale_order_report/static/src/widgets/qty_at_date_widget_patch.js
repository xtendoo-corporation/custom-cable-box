/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { QtyAtDateWidget } from "@sale_stock/widgets/qty_at_date_widget";

patch(QtyAtDateWidget.prototype, {
    initCalcData() {
        super.initCalcData(...arguments);
        const { data } = this.props.record;
        if (data.scheduled_date) {
            // Evaluamos si no hay suficiente a mano hoy, pero sí habrá en la fecha esperada
            this.calcData.is_forecasted_only =
                this.calcData.will_be_fulfilled &&
                !this.calcData.will_be_late &&
                data.free_qty_today < data.qty_to_deliver;
        }
    }
});
