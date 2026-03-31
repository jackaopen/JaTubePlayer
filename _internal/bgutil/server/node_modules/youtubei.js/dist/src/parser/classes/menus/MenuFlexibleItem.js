import { Parser } from '../../index.js';
import { YTNode } from '../../helpers.js';
import Button from '../Button.js';
import ButtonView from '../ButtonView.js';
import MenuServiceItem from './MenuServiceItem.js';
import DownloadButton from '../DownloadButton.js';
import MenuServiceItemDownload from './MenuServiceItemDownload.js';
export default class MenuFlexibleItem extends YTNode {
    static type = 'MenuFlexibleItem';
    menu_item;
    top_level_button;
    constructor(data) {
        super();
        this.menu_item = Parser.parseItem(data.menuItem, [MenuServiceItem, MenuServiceItemDownload]);
        this.top_level_button = Parser.parseItem(data.topLevelButton, [DownloadButton, ButtonView, Button]);
    }
}
//# sourceMappingURL=MenuFlexibleItem.js.map