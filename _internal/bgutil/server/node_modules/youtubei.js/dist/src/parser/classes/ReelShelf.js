import { YTNode } from '../helpers.js';
import { Parser } from '../index.js';
import NavigationEndpoint from './NavigationEndpoint.js';
import Text from './misc/Text.js';
export default class ReelShelf extends YTNode {
    static type = 'ReelShelf';
    title;
    items;
    endpoint;
    constructor(data) {
        super();
        this.title = new Text(data.title);
        this.items = Parser.parseArray(data.items);
        if (Reflect.has(data, 'endpoint')) {
            this.endpoint = new NavigationEndpoint(data.endpoint);
        }
    }
    // XXX: Alias for consistency.
    get contents() {
        return this.items;
    }
}
//# sourceMappingURL=ReelShelf.js.map