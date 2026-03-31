import { YTNode } from '../helpers.js';
import NavigationEndpoint from './NavigationEndpoint.js';
import Text from './misc/Text.js';
export default class ItemSectionTab extends YTNode {
    static type = 'Tab';
    title;
    selected;
    endpoint;
    constructor(data) {
        super();
        this.title = new Text(data.title);
        this.selected = !!data.selected;
        this.endpoint = new NavigationEndpoint(data.endpoint);
    }
}
//# sourceMappingURL=ItemSectionTab.js.map