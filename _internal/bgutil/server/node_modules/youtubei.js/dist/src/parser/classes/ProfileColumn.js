import { YTNode } from '../helpers.js';
import { Parser } from '../index.js';
export default class ProfileColumn extends YTNode {
    static type = 'ProfileColumn';
    items;
    constructor(data) {
        super();
        this.items = Parser.parseArray(data.items);
    }
    // XXX: Alias for consistency.
    get contents() {
        return this.items;
    }
}
//# sourceMappingURL=ProfileColumn.js.map