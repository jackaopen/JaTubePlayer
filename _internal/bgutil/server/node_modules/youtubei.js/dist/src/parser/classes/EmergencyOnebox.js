import { YTNode } from '../helpers.js';
import { Parser } from '../index.js';
import Menu from './menus/Menu.js';
import Text from './misc/Text.js';
export default class EmergencyOnebox extends YTNode {
    static type = 'EmergencyOnebox';
    title;
    first_option;
    menu;
    constructor(data) {
        super();
        this.title = new Text(data.title);
        this.first_option = Parser.parseItem(data.firstOption);
        this.menu = Parser.parseItem(data.menu, Menu);
    }
}
//# sourceMappingURL=EmergencyOnebox.js.map