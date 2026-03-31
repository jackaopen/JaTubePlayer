import { YTNode } from '../helpers.js';
import { Parser } from '../index.js';
import Button from './Button.js';
import NavigationEndpoint from './NavigationEndpoint.js';
import Text from './misc/Text.js';
import Thumbnail from './misc/Thumbnail.js';
export default class ChannelAboutFullMetadata extends YTNode {
    static type = 'ChannelAboutFullMetadata';
    id;
    name;
    avatar;
    canonical_channel_url;
    primary_links;
    view_count;
    joined_date;
    description;
    email_reveal;
    can_reveal_email;
    country;
    buttons;
    constructor(data) {
        super();
        this.id = data.channelId;
        this.name = new Text(data.title);
        this.avatar = Thumbnail.fromResponse(data.avatar);
        this.canonical_channel_url = data.canonicalChannelUrl;
        this.primary_links = data.primaryLinks?.map((link) => ({
            endpoint: new NavigationEndpoint(link.navigationEndpoint),
            icon: Thumbnail.fromResponse(link.icon),
            title: new Text(link.title)
        })) ?? [];
        this.view_count = new Text(data.viewCountText);
        this.joined_date = new Text(data.joinedDateText);
        this.description = new Text(data.description);
        this.email_reveal = new NavigationEndpoint(data.onBusinessEmailRevealClickCommand);
        this.can_reveal_email = !data.signInForBusinessEmail;
        this.country = new Text(data.country);
        this.buttons = Parser.parseArray(data.actionButtons, Button);
    }
}
//# sourceMappingURL=ChannelAboutFullMetadata.js.map