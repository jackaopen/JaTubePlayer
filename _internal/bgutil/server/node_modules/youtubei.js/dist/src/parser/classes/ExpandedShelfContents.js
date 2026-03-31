import { Parser } from '../index.js';
import { YTNode } from '../helpers.js';
export default class ExpandedShelfContents extends YTNode {
    static type = 'ExpandedShelfContents';
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
//# sourceMappingURL=ExpandedShelfContents.js.map