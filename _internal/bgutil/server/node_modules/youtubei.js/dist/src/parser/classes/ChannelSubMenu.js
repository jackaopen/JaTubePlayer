import { YTNode } from '../helpers.js';
import { Parser } from '../index.js';
import NavigationEndpoint from './NavigationEndpoint.js';
export default class ChannelSubMenu extends YTNode {
    static type = 'ChannelSubMenu';
    content_type_sub_menu_items;
    sort_setting;
    constructor(data) {
        super();
        this.content_type_sub_menu_items = data.contentTypeSubMenuItems.map((item) => ({
            endpoint: new NavigationEndpoint(item.navigationEndpoint || item.endpoint),
            selected: item.selected,
            title: item.title
        }));
        this.sort_setting = Parser.parseItem(data.sortSetting);
    }
}
//# sourceMappingURL=ChannelSubMenu.js.map