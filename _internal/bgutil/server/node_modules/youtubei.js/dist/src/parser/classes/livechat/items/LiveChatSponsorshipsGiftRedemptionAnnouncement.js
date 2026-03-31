import { YTNode } from '../../../helpers.js';
import NavigationEndpoint from '../../NavigationEndpoint.js';
import Author from '../../misc/Author.js';
import Text from '../../misc/Text.js';
export default class LiveChatSponsorshipsGiftRedemptionAnnouncement extends YTNode {
    static type = 'LiveChatSponsorshipsGiftRedemptionAnnouncement';
    id;
    timestamp_usec;
    timestamp_text;
    author;
    message;
    menu_endpoint;
    context_menu_accessibility_label;
    constructor(data) {
        super();
        this.id = data.id;
        this.timestamp_usec = data.timestampUsec;
        this.timestamp_text = new Text(data.timestampText);
        this.author = new Author(data.authorName, data.authorBadges, data.authorPhoto, data.authorExternalChannelId);
        this.message = new Text(data.message);
        this.menu_endpoint = new NavigationEndpoint(data.contextMenuEndpoint);
        this.context_menu_accessibility_label = data.contextMenuAccessibility.accessibilityData.label;
    }
}
//# sourceMappingURL=LiveChatSponsorshipsGiftRedemptionAnnouncement.js.map