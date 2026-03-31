import { Parser } from '../../../index.js';
import Button from '../../Button.js';
import NavigationEndpoint from '../../NavigationEndpoint.js';
import Text from '../../misc/Text.js';
import { YTNode } from '../../../helpers.js';
export default class LiveChatAutoModMessage extends YTNode {
    static type = 'LiveChatAutoModMessage';
    menu_endpoint;
    moderation_buttons;
    auto_moderated_item;
    header_text;
    timestamp;
    id;
    constructor(data) {
        super();
        this.menu_endpoint = new NavigationEndpoint(data.contextMenuEndpoint);
        this.moderation_buttons = Parser.parseArray(data.moderationButtons, Button);
        this.auto_moderated_item = Parser.parseItem(data.autoModeratedItem);
        this.header_text = new Text(data.headerText);
        this.timestamp = Math.floor(parseInt(data.timestampUsec) / 1000);
        this.id = data.id;
    }
}
//# sourceMappingURL=LiveChatAutoModMessage.js.map