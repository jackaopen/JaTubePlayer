import { YTNode } from '../helpers.js';
export default class BadgeView extends YTNode {
    text;
    style;
    accessibility_label;
    constructor(data) {
        super();
        this.text = data.badgeText;
        this.style = data.badgeStyle;
        this.accessibility_label = data.accessibilityLabel;
    }
}
//# sourceMappingURL=BadgeView.js.map