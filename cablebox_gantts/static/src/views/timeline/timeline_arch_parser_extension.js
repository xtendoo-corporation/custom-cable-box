import {patch} from "@web/core/utils/patch";
import {TimelineArchParser} from "@web_timeline/views/timeline/timeline_arch_parser.esm";

patch(TimelineArchParser.prototype, {
    parse(arch, fields) {
        const archInfo = super.parse(arch, fields);
        const timelineNode = arch.tagName === "timeline" ? arch : arch.querySelector("timeline");

        if (timelineNode && timelineNode.hasAttribute("scales")) {
            archInfo.scales = timelineNode
                .getAttribute("scales")
                .split(",")
                .map((s) => s.trim());
        } else if (!archInfo.scales) {
            // Default scales if not specified and not already set by parent
            archInfo.scales = ["day", "week", "month", "year"];
        }
        if (timelineNode && timelineNode.hasAttribute("unique_by")) {
            archInfo.unique_by = timelineNode.getAttribute("unique_by");
            if (!archInfo.fieldNames.includes(archInfo.unique_by)) {
                archInfo.fieldNames.push(archInfo.unique_by);
            }
        }
        for (const attrName of ["group_label_date", "group_order_date"]) {
            if (timelineNode && timelineNode.hasAttribute(attrName)) {
                archInfo[attrName] = timelineNode.getAttribute(attrName);
                if (!archInfo.fieldNames.includes(archInfo[attrName])) {
                    archInfo.fieldNames.push(archInfo[attrName]);
                }
            }
        }
        return archInfo;
    },
});
