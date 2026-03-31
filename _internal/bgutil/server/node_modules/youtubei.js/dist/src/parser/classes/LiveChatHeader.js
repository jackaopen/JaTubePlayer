import { YTNode } from '../helpers.js';
import { Parser } from '../index.js';
import Button from './Button.js';
import SortFilterSubMenu from './SortFilterSubMenu.js';
import Menu from './menus/Menu.js';
export default class LiveChatHeader extends YTNode {
    static type = 'LiveChatHeader';
    overflow_menu;
    collapse_button;
    view_selector;
    constructor(data) {
        super();
        this.overflow_menu = Parser.parseItem(data.overflowMenu, Menu);
        this.collapse_button = Parser.parseItem(data.collapseButton, Button);
        this.view_selector = Parser.parseItem(data.viewSelector, SortFilterSubMenu);
    }
}
//# sourceMappingURL=LiveChatHeader.js.map