import {patch} from "@web/core/utils/patch";
import {TimelineModel} from "@web_timeline/views/timeline/timeline_model";

patch(TimelineModel.prototype, {
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

