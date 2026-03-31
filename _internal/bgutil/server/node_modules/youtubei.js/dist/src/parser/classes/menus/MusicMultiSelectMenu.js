import { YTNode } from '../../helpers.js';
import { Parser } from '../../index.js';
import Text from '../misc/Text.js';
import MusicMenuItemDivider from './MusicMenuItemDivider.js';
import MusicMultiSelectMenuItem from './MusicMultiSelectMenuItem.js';
export default class MusicMultiSelectMenu extends YTNode {
    static type = 'MusicMultiSelectMenu';
    title;
    options;
    constructor(data) {
        super();
        if (Reflect.has(data, 'title') && Reflect.has(data.title, 'musicMenuTitleRenderer')) {
            this.title = new Text(data.title.musicMenuTitleRenderer?.primaryText);
        }
        this.options = Parser.parseArray(data.options, [MusicMultiSelectMenuItem, MusicMenuItemDivider]);
    }
}
//# sourceMappingURL=MusicMultiSelectMenu.js.map