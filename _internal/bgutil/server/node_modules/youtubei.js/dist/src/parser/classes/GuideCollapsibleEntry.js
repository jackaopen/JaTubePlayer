import * as Parser from '../parser.js';
import GuideEntry from './GuideEntry.js';
import { YTNode } from '../helpers.js';
export default class GuideCollapsibleEntry extends YTNode {
    static type = 'GuideCollapsibleEntry';
    expander_item;
    collapser_item;
    expandable_items;
    constructor(data) {
        super();
        this.expander_item = Parser.parseItem(data.expanderItem, GuideEntry);
        this.collapser_item = Parser.parseItem(data.collapserItem, GuideEntry);
        this.expandable_items = Parser.parseArray(data.expandableItems);
    }
}
//# sourceMappingURL=GuideCollapsibleEntry.js.map