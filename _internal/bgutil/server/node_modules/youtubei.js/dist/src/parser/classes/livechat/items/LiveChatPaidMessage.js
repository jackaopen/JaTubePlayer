import { YTNode } from '../../../helpers.js';
import { Parser } from '../../../index.js';
import NavigationEndpoint from '../../NavigationEndpoint.js';
import Author from '../../misc/Author.js';
import Text from '../../misc/Text.js';
import Thumbnail from '../../misc/Thumbnail.js';
import CreatorHeartView from './CreatorHeartView.js';
import LiveChatItemBumperView from './LiveChatItemBumperView.js';
import PdgReplyButtonView from './PdgReplyButtonView.js';
export default class LiveChatPaidMessage extends YTNode {
    static type = 'LiveChatPaidMessage';
    id;
    message;
    author;
    author_name_text_color;
    header_background_color;
    header_text_color;
    body_background_color;
    body_text_color;
    purchase_amount;
    menu_endpoint;
    context_menu_accessibility_label;
    timestamp;
    timestamp_usec;
    timestamp_text;
    timestamp_color;
    header_overlay_image;
    text_input_background_color;
    lower_bumper;
    creator_heart_button;
    is_v2_style;
    reply_button;
    constructor(data) {
        super();
        this.id = data.id;
        this.message = new Text(data.message);
        this.author = new Author(data.authorName, data.authorBadges, data.authorPhoto, data.authorExternalChannelId);
        this.author_name_text_color = data.authorNameTextColor;
        this.header_background_color = data.headerBackgroundColor;
        this.header_text_color = data.headerTextColor;
        this.body_background_color = data.bodyBackgroundColor;
        this.body_text_color = data.bodyTextColor;
        this.purchase_amount = new Text(data.purchaseAmountText).toString();
        this.menu_endpoint = new NavigationEndpoint(data.contextMenuEndpoint);
        this.context_menu_accessibility_label = data.contextMenuAccessibility.accessibilityData.label;
        this.timestamp = Math.floor(parseInt(data.timestampUsec) / 1000);
        this.timestamp_usec = data.timestampUsec;
        if (Reflect.has(data, 'timestampText')) {
            this.timestamp_text = new Text(data.timestampText).toString();
        }
        this.timestamp_color = data.timestampColor;
        if (Reflect.has(data, 'headerOverlayImage')) {
            this.header_overlay_image = Thumbnail.fromResponse(data.headerOverlayImage);
        }
        this.text_input_background_color = data.textInputBackgroundColor;
        this.lower_bumper = Parser.parseItem(data.lowerBumper, LiveChatItemBumperView);
        this.creator_heart_button = Parser.parseItem(data.creatorHeartButton, CreatorHeartView);
        this.is_v2_style = data.isV2Style;
        this.reply_button = Parser.parseItem(data.replyButton, PdgReplyButtonView);
    }
}
//# sourceMappingURL=LiveChatPaidMessage.js.map