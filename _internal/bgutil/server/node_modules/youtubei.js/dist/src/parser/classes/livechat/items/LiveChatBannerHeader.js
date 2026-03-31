import { YTNode } from '../../../helpers.js';
import { Parser } from '../../../index.js';
import Button from '../../Button.js';
import Text from '../../misc/Text.js';
export default class LiveChatBannerHeader extends YTNode {
    static type = 'LiveChatBannerHeader';
    text;
    icon_type;
    context_menu_button;
    constructor(data) {
        super();
        this.text = new Text(data.text);
        if (Reflect.has(data, 'icon') && Reflect.has(data.icon, 'iconType')) {
            this.icon_type = data.icon.iconType;
        }
        this.context_menu_button = Parser.parseItem(data.contextMenuButton, Button);
    }
}
//# sourceMappingURL=LiveChatBannerHeader.js.map