import Text from './misc/Text.js';
import NavigationEndpoint from './NavigationEndpoint.js';
import { YTNode } from '../helpers.js';
export default class ToggleMenuServiceItem extends YTNode {
    static type = 'ToggleMenuServiceItem';
    text;
    toggled_text;
    icon_type;
    toggled_icon_type;
    default_endpoint;
    toggled_endpoint;
    constructor(data) {
        super();
        this.text = new Text(data.defaultText);
        this.toggled_text = new Text(data.toggledText);
        this.icon_type = data.defaultIcon.iconType;
        this.toggled_icon_type = data.toggledIcon.iconType;
        this.default_endpoint = new NavigationEndpoint(data.defaultServiceEndpoint);
        this.toggled_endpoint = new NavigationEndpoint(data.toggledServiceEndpoint);
    }
}
//# sourceMappingURL=ToggleMenuServiceItem.js.map