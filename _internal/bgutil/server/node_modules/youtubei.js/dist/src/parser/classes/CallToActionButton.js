import Text from './misc/Text.js';
import { YTNode } from '../helpers.js';
export default class CallToActionButton extends YTNode {
    static type = 'CallToActionButton';
    label;
    icon_type;
    style;
    constructor(data) {
        super();
        this.label = new Text(data.label);
        this.icon_type = data.icon.iconType;
        this.style = data.style;
    }
}
//# sourceMappingURL=CallToActionButton.js.map