import { YTNode } from '../helpers.js';
import { Parser } from '../index.js';
import NavigationEndpoint from './NavigationEndpoint.js';
export default class ExpandableTab extends YTNode {
    static type = 'ExpandableTab';
    title;
    endpoint;
    selected;
    content;
    constructor(data) {
        super();
        this.title = data.title;
        this.endpoint = new NavigationEndpoint(data.endpoint);
        this.selected = data.selected;
        this.content = Parser.parseItem(data.content);
    }
}
//# sourceMappingURL=ExpandableTab.js.map