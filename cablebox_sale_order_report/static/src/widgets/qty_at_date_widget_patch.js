/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { QtyAtDateWidget } from "@sale_stock/widgets/qty_at_date_widget";

patch(QtyAtDateWidget.prototype, {
    initCalcData() {
        super.initCalcData(...arguments);
        const { data } = this.props.record;
        if (data.scheduled_date) {
            // Evaluamos si no hay suficiente físicamente hoy, pero sí habrá en la fecha esperada.
            // Con el pedido confirmado, qty_available_today es lo RESERVADO (0 si el tipo de
            // operación tiene reserva manual aunque haya stock), así que no sirve como stock
            // físico: la cobertura es solo prevista si el movimiento depende de una entrada
            // futura (forecast_expected_date).
            const forecastedOnly = data.state === 'sale'
                ? !!data.forecast_expected_date
                : data.free_qty_today < data.qty_to_deliver;

            this.calcData.is_forecasted_only =
                this.calcData.will_be_fulfilled && forecastedOnly;

            // Compatibilidad con otros módulos que usan `reservation_issue` para pintar ámbar.
            this.calcData.reservation_issue = this.calcData.is_forecasted_only;

            // Para este cliente priorizamos mostrar ámbar cuando el forecast cubre la demanda
            // pendiente, aunque la cobertura llegue más tarde que la fecha prevista.
            if (this.calcData.is_forecasted_only) {
                this.calcData.forecasted_issue = false;
            }
        }
    }
});
