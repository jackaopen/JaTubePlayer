import { YTNode } from '../../helpers.js';
import { Parser } from '../../index.js';
import MenuNavigationItem from './MenuNavigationItem.js';
import MenuServiceItem from './MenuServiceItem.js';
export default class MenuPopup extends YTNode {
    static type = 'MenuPopup';
    items;
    constructor(data) {
        super();
        this.items = Parser.parseArray(data.items, [MenuNavigationItem, MenuServiceItem]);
    }
}
//# sourceMappingURL=MenuPopup.js.map