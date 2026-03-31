import { YTNode } from '../helpers.js';
import AccessibilityData from './misc/AccessibilityData.js';
export default class MusicInlineBadge extends YTNode {
    static type = 'MusicInlineBadge';
    icon_type;
    accessibility;
    constructor(data) {
        super();
        this.icon_type = data.icon.iconType;
        if ('accessibilityData' in data
            && 'accessibilityData' in data.accessibilityData) {
            this.accessibility = {
                accessibility_data: new AccessibilityData(data.accessibilityData.accessibilityData)
            };
        }
    }
    get label() {
        return this.accessibility?.accessibility_data?.label;
    }
}
//# sourceMappingURL=MusicInlineBadge.js.map