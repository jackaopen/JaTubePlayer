import { Parser } from '../index.js';
import { YTNode } from '../helpers.js';
export default class HorizontalList extends YTNode {
    static type = 'HorizontalList';
    visible_item_count;
    items;
    constructor(data) {
        super();
        this.visible_item_count = data.visibleItemCount;
        this.items = Parser.parseArray(data.items);
    }
    // XXX: Alias for consistency.
    get contents() {
        return this.items;
    }
}
//# sourceMappingURL=HorizontalList.js.map