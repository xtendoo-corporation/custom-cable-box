import {patch} from "@web/core/utils/patch";
import {TimelineRenderer} from "@web_timeline/views/timeline/timeline_renderer.esm";
import {_t} from "@web/core/l10n/translation";

patch(TimelineRenderer.prototype, {
    setup() {
        super.setup(...arguments);
        this.scales = this.params.scales || ["day", "week", "month", "year"];
    },
    async split_groups(records) {
        if (this.model.last_group_bys.length === 0) {
            return records;
        }
        const grouped_field = this.model.last_group_bys[0];
        const field_type = this.fields[grouped_field]?.type;

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
                            content: group_name,
                            order: seq++,
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
        return super.split_groups(records);
    },
});

