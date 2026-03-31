import { YTNode } from '../helpers.js';
import { Parser } from '../index.js';
export default class MerchandiseShelf extends YTNode {
    static type = 'MerchandiseShelf';
    title;
    menu;
    items;
    constructor(data) {
        super();
        this.title = data.title;
        this.menu = Parser.parseItem(data.actionButton);
        this.items = Parser.parseArray(data.items);
    }
    // XXX: Alias for consistency.
    get contents() {
        return this.items;
    }
}
//# sourceMappingURL=MerchandiseShelf.js.map