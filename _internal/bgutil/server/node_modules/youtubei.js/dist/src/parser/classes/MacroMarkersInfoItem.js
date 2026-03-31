import { YTNode } from '../helpers.js';
import { Parser } from '../index.js';
import Menu from './menus/Menu.js';
import Text from './misc/Text.js';
export default class MacroMarkersInfoItem extends YTNode {
    static type = 'MacroMarkersInfoItem';
    info_text;
    menu;
    constructor(data) {
        super();
        this.info_text = new Text(data.infoText);
        this.menu = Parser.parseItem(data.menu, Menu);
    }
}
//# sourceMappingURL=MacroMarkersInfoItem.js.map