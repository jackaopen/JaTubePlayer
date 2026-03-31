import { Parser } from '../../index.js';
import { YTNode } from '../../helpers.js';
import MultiPageMenu from '../menus/MultiPageMenu.js';
export default class GetMultiPageMenuAction extends YTNode {
    static type = 'GetMultiPageMenuAction';
    menu;
    constructor(data) {
        super();
        this.menu = Parser.parseItem(data.menu, MultiPageMenu);
    }
}
//# sourceMappingURL=GetMultiPageMenuAction.js.map