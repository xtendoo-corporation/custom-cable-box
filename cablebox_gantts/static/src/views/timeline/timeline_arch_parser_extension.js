import {patch} from "@web/core/utils/patch";
import {TimelineArchParser} from "@web_timeline/views/timeline/timeline_arch_parser.esm";

patch(TimelineArchParser.prototype, {
    parse(arch, fields) {
        const archInfo = super.parse(arch, fields);
        const timelineNode = arch.tagName === "timeline" ? arch : arch.querySelector("timeline");

        if (timelineNode && timelineNode.hasAttribute("scales")) {
            archInfo.options.scales = timelineNode
                .getAttribute("scales")
                .split(",")
                .map((s) => s.trim());
        } else if (!archInfo.options.scales) {
            // Default scales if not specified and not already set by parent
            archInfo.options.scales = ["day", "week", "month", "year"];
        }
        return archInfo;
    },
});

