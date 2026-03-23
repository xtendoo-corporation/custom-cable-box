/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { QtyAtDateWidget } from "@sale_stock/widgets/qty_at_date_widget";

patch(QtyAtDateWidget.prototype, {
    initCalcData() {
        super.initCalcData(...arguments);
        const { data } = this.props.record;
        if (data.scheduled_date) {
            // Evaluamos si no hay suficiente físicamente hoy, pero sí habrá en la fecha esperada.
            // Odoo recicla variables dependiendo de si el pedido está confirmado o en borrador.
            const qty_physical = data.state === 'sale' ? data.qty_available_today : data.free_qty_today;
            
            this.calcData.is_forecasted_only =
                this.calcData.will_be_fulfilled &&
                qty_physical < data.qty_to_deliver;
        }
    }
});
