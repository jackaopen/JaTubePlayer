import { Parser } from '../index.js';
import { YTNode } from '../helpers.js';
export default class ProfileColumnStats extends YTNode {
    static type = 'ProfileColumnStats';
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
//# sourceMappingURL=ProfileColumnStats.js.map