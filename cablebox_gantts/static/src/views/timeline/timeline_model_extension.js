import {patch} from "@web/core/utils/patch";
import {TimelineModel} from "@web_timeline/views/timeline/timeline_model.esm";

patch(TimelineModel.prototype, {
    setup(params) {
        super.setup(...arguments);
        this.unique_by = params.unique_by;
        this.group_order_date = params.group_order_date;
    },
    async load(searchParams) {
        await super.load(...arguments);
        // Remove fully delivered orders so they disappear from the timeline.
        // We check `delivery_status_percentage` field; if it's 100 (or string '100'),
        // exclude the record.
        if (Array.isArray(this.data) && this.data.length) {
            this.data = this.data.filter((record) => {
                const perc = record.delivery_status_percentage;
                // handle possibilities: number, string, undefined
                return !(perc !== undefined && (Number(perc) === 100));
            });
        }
        if (this.group_order_date) {
            this.data.sort((left, right) => {
                const leftDate = left[this.group_order_date] || "";
                const rightDate = right[this.group_order_date] || "";
                return leftDate.localeCompare(rightDate) || left.id - right.id;
            });
        }
        if (!this.unique_by) {
            return;
        }
        const seen = new Set();
        this.data = this.data.filter((record) => {
            let value = record[this.unique_by];
            if (Array.isArray(value)) {
                value = value[0];
            }
            if (!value || seen.has(value)) {
                return false;
            }
            seen.add(value);
            return true;
        });
        this.notify();
    },
    _event_data_transform(record) {
        const [date_start, date_stop] = this._get_event_dates(record);
        let group = record[this.last_group_bys[0]];

        const res = super._event_data_transform(record);

        // Aseguramos que las fechas se traten como locales para evitar desfases de zona horaria
        // date_start y date_stop son objetos Luxon DateTime provenientes de _get_event_dates
        res.start = new Date(date_start.year, date_start.month - 1, date_start.day);
        if (date_stop) {
            res.end = new Date(date_stop.year, date_stop.month - 1, date_stop.day);
        }

        if (group && typeof group === "string") {
            res.group = group;
        }
        return res;
    },
});
