import { YTNode } from '../helpers.js';
import NavigationEndpoint from './NavigationEndpoint.js';
export default class ChipView extends YTNode {
    static type = 'ChipView';
    text;
    display_type;
    endpoint;
    chip_entity_key;
    constructor(data) {
        super();
        this.text = data.text;
        this.display_type = data.displayType;
        this.endpoint = new NavigationEndpoint(data.tapCommand);
        this.chip_entity_key = data.chipEntityKey;
    }
}
//# sourceMappingURL=ChipView.js.map