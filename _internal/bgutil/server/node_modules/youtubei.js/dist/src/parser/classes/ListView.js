import { YTNode } from '../helpers.js';
import { Parser } from '../index.js';
import ListItemView from './ListItemView.js';
export default class ListView extends YTNode {
    static type = 'ListView';
    items;
    constructor(data) {
        super();
        this.items = Parser.parseArray(data.listItems, ListItemView);
    }
}
//# sourceMappingURL=ListView.js.map