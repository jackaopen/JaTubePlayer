import { YTNode } from '../helpers.js';
import { Parser } from '../index.js';
import ItemSectionTab from './ItemSectionTab.js';
import Text from './misc/Text.js';
export default class ItemSectionTabbedHeader extends YTNode {
    static type = 'ItemSectionTabbedHeader';
    title;
    tabs;
    end_items;
    constructor(data) {
        super();
        this.title = new Text(data.title);
        this.tabs = Parser.parseArray(data.tabs, ItemSectionTab);
        if (Reflect.has(data, 'endItems')) {
            this.end_items = Parser.parseArray(data.endItems);
        }
    }
}
//# sourceMappingURL=ItemSectionTabbedHeader.js.map