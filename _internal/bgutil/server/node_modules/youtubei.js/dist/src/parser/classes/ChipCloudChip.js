import Text from './misc/Text.js';
import NavigationEndpoint from './NavigationEndpoint.js';
import { YTNode } from '../helpers.js';
export default class ChipCloudChip extends YTNode {
    static type = 'ChipCloudChip';
    is_selected;
    endpoint;
    text;
    constructor(data) {
        super();
        this.is_selected = data.isSelected;
        if (Reflect.has(data, 'navigationEndpoint')) {
            this.endpoint = new NavigationEndpoint(data.navigationEndpoint);
        }
        this.text = new Text(data.text).toString();
    }
}
//# sourceMappingURL=ChipCloudChip.js.map