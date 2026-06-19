import {patch} from "@web/core/utils/patch";
import {TimelineRenderer} from "@web_timeline/views/timeline/timeline_renderer.esm";
import {_t} from "@web/core/l10n/translation";

patch(TimelineRenderer.prototype, {
    setup() {
        super.setup(...arguments);
        this.scales = this.params.scales || ["day", "week", "month", "year"];
        this.group_label_date = this.params.group_label_date;
        this.group_order_date = this.params.group_order_date;
    },
    async split_groups(records) {
        if (this.model.last_group_bys.length === 0) {
            return records;
        }
        const grouped_field = this.model.last_group_bys[0];
        const field_type = this.fields[grouped_field]?.type;
        const makeGroupContent = (evt, fallback) => {
            if (!this.group_label_date || !evt[this.group_label_date]) {
                return fallback;
            }
            return `${evt[this.group_label_date]} - ${fallback}`;
        };
        const makeGroupOrder = (evt, fallback) => {
            if (!this.group_order_date || !evt[this.group_order_date]) {
                return fallback;
            }
            return `${evt[this.group_order_date]}-${String(fallback).padStart(8, "0")}`;
        };

        if (field_type === 'char' || field_type === 'selection') {
            const groups = [];
            let seq = 1;
            for (const evt of records) {
                const group_name = evt[grouped_field];
                if (group_name && typeof group_name === "string") {
                    const group = groups.find((g) => g.id === group_name);
                    if (!group) {
                        groups.push({
                            id: group_name,
                            content: makeGroupContent(evt, group_name),
                            order: makeGroupOrder(evt, seq++),
                        });
                    }
                } else if (!group_name) {
                     const unassigned = groups.find((g) => g.id === -1);
                     if (!unassigned) {
                         groups.push({id: -1, content: _t("<b>UNASSIGNED</b>"), order: -1});
                     }
                }
            }
            return groups;
        }
        const groups = await super.split_groups(records);
        if (!this.group_label_date && !this.group_order_date) {
            return groups;
        }
        for (const group of groups) {
            if (group.id === -1) {
                continue;
            }
            const evt = records.find((record) => {
                const value = record[grouped_field];
                return Array.isArray(value) && value[0] === group.id;
            });
            if (evt) {
                group.content = makeGroupContent(evt, group.content);
                group.order = makeGroupOrder(evt, group.order);
            }
        }
        return groups;
    },
});
