import { Parser } from '../../index.js';
import Button from '../Button.js';
import KidsCategoryTab from './KidsCategoryTab.js';
import { YTNode } from '../../helpers.js';
export default class KidsCategoriesHeader extends YTNode {
    static type = 'kidsCategoriesHeader';
    category_tabs;
    privacy_button;
    constructor(data) {
        super();
        this.category_tabs = Parser.parseArray(data.categoryTabs, KidsCategoryTab);
        this.privacy_button = Parser.parseItem(data.privacyButtonRenderer, Button);
    }
}
//# sourceMappingURL=KidsCategoriesHeader.js.map