import { YTNode } from '../../helpers.js';
import NavigationEndpoint from '../NavigationEndpoint.js';
import AccessibilityData from '../misc/AccessibilityData.js';
export default class PivotBarItem extends YTNode {
    static type = 'PivotBarItem';
    pivot_identifier;
    endpoint;
    title;
    accessibility_label;
    icon_type;
    accessibility;
    constructor(data) {
        super();
        this.pivot_identifier = data.pivotIdentifier;
        this.endpoint = new NavigationEndpoint(data.navigationEndpoint);
        this.title = new Text(data.title);
        if ('accessibility' in data
            && 'accessibilityData' in data.accessibility) {
            this.accessibility = {
                accessibility_data: new AccessibilityData(data.accessibility.accessibilityData)
            };
        }
        if (Reflect.has(data, 'icon') && Reflect.has(data.icon, 'iconType'))
            this.icon_type = data.icon.iconType;
    }
    get label() {
        return this.accessibility?.accessibility_data?.label;
    }
}
//# sourceMappingURL=PivotBarItem.js.map