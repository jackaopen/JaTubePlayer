import { YTNode } from '../helpers.js';
import { Parser } from '../index.js';
import SortFilterSubMenu from './SortFilterSubMenu.js';
export default class TranscriptFooter extends YTNode {
    static type = 'TranscriptFooter';
    language_menu;
    constructor(data) {
        super();
        this.language_menu = Parser.parseItem(data.languageMenu, SortFilterSubMenu);
    }
}
//# sourceMappingURL=TranscriptFooter.js.map