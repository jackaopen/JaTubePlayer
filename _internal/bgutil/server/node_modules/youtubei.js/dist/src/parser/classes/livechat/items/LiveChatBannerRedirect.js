import { YTNode } from '../../../helpers.js';
import { Parser } from '../../../index.js';
import Button from '../../Button.js';
import Text from '../../misc/Text.js';
import Thumbnail from '../../misc/Thumbnail.js';
export default class LiveChatBannerRedirect extends YTNode {
    static type = 'LiveChatBannerRedirect';
    banner_message;
    author_photo;
    inline_action_button;
    context_menu_button;
    constructor(data) {
        super();
        this.banner_message = new Text(data.bannerMessage);
        this.author_photo = Thumbnail.fromResponse(data.authorPhoto);
        this.inline_action_button = Parser.parseItem(data.inlineActionButton, Button);
        this.context_menu_button = Parser.parseItem(data.contextMenuButton, Button);
    }
}
//# sourceMappingURL=LiveChatBannerRedirect.js.map