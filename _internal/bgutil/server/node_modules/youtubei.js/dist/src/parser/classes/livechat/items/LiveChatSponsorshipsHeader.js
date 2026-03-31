import { Parser } from '../../../index.js';
import { YTNode } from '../../../helpers.js';
import NavigationEndpoint from '../../NavigationEndpoint.js';
import Text from '../../misc/Text.js';
import Thumbnail from '../../misc/Thumbnail.js';
import LiveChatAuthorBadge from '../../LiveChatAuthorBadge.js';
export default class LiveChatSponsorshipsHeader extends YTNode {
    static type = 'LiveChatSponsorshipsHeader';
    author_name;
    author_photo;
    author_badges;
    primary_text;
    menu_endpoint;
    context_menu_accessibility_label;
    image;
    constructor(data) {
        super();
        this.author_name = new Text(data.authorName);
        this.author_photo = Thumbnail.fromResponse(data.authorPhoto);
        this.author_badges = Parser.parseArray(data.authorBadges, LiveChatAuthorBadge);
        this.primary_text = new Text(data.primaryText);
        this.menu_endpoint = new NavigationEndpoint(data.contextMenuEndpoint);
        this.context_menu_accessibility_label = data.contextMenuAccessibility.accessibilityData.label;
        this.image = Thumbnail.fromResponse(data.image);
    }
}
//# sourceMappingURL=LiveChatSponsorshipsHeader.js.map