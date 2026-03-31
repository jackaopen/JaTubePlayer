import { Parser } from '../index.js';
import { YTNode } from '../helpers.js';
export default class PlaylistSidebar extends YTNode {
    static type = 'PlaylistSidebar';
    items;
    constructor(data) {
        super();
        this.items = Parser.parseArray(data.items);
    }
    // XXX: alias for consistency
    get contents() {
        return this.items;
    }
}
//# sourceMappingURL=PlaylistSidebar.js.map