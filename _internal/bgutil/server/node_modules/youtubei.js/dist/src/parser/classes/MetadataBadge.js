import { YTNode } from '../helpers.js';
export default class MetadataBadge extends YTNode {
    static type = 'MetadataBadge';
    icon_type;
    style;
    label;
    tooltip;
    constructor(data) {
        super();
        if (Reflect.has(data, 'icon')) {
            this.icon_type = data.icon.iconType;
        }
        if (Reflect.has(data, 'style')) {
            this.style = data.style;
        }
        if (Reflect.has(data, 'label')) {
            this.label = data.label;
        }
        if (Reflect.has(data, 'tooltip') || Reflect.has(data, 'iconTooltip')) {
            this.tooltip = data.tooltip || data.iconTooltip;
        }
    }
}
//# sourceMappingURL=MetadataBadge.js.map