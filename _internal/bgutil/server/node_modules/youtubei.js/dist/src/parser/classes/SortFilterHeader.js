import { YTNode } from '../helpers.js';
import { Parser, YTNodes } from '../index.js';
export default class SortFilterHeader extends YTNode {
    static type = 'SortFilterHeader';
    filter_menu;
    constructor(data) {
        super();
        this.filter_menu = Parser.parseItem(data.filterMenu, YTNodes.SortFilterSubMenu);
    }
}
//# sourceMappingURL=SortFilterHeader.js.map