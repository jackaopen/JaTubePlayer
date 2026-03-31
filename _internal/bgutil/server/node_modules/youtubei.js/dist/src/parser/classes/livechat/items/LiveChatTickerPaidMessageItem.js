import Author from '../../misc/Author.js';
import { Parser } from '../../../index.js';
import NavigationEndpoint from '../../NavigationEndpoint.js';
import Text from '../../misc/Text.js';
import { YTNode } from '../../../helpers.js';
export default class LiveChatTickerPaidMessageItem extends YTNode {
    static type = 'LiveChatTickerPaidMessageItem';
    id;
    author;
    amount;
    amount_text_color;
    start_background_color;
    end_background_color;
    duration_sec;
    full_duration_sec;
    show_item;
    show_item_endpoint;
    animation_origin;
    open_engagement_panel_command;
    constructor(data) {
        super();
        this.id = data.id;
        this.author = new Author(data.authorName || data.authorUsername, data.authorBadges, data.authorPhoto, data.authorExternalChannelId);
        if (Reflect.has(data, 'amount')) {
            this.amount = new Text(data.amount);
        }
        this.amount_text_color = data.amountTextColor;
        this.start_background_color = data.startBackgroundColor;
        this.end_background_color = data.endBackgroundColor;
        this.duration_sec = data.durationSec;
        this.full_duration_sec = data.fullDurationSec;
        this.show_item = Parser.parseItem(data.showItemEndpoint?.showLiveChatItemEndpoint?.renderer);
        this.show_item_endpoint = new NavigationEndpoint(data.showItemEndpoint);
        this.animation_origin = data.animationOrigin;
        this.open_engagement_panel_command = new NavigationEndpoint(data.openEngagementPanelCommand);
    }
}
//# sourceMappingURL=LiveChatTickerPaidMessageItem.js.map