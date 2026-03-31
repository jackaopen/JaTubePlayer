import Text from './misc/Text.js';
import Thumbnail from './misc/Thumbnail.js';
import NavigationEndpoint from './NavigationEndpoint.js';
import { YTNode } from '../helpers.js';
export default class CollaboratorInfoCardContent extends YTNode {
    static type = 'CollaboratorInfoCardContent';
    channel_avatar;
    custom_text;
    channel_name;
    subscriber_count;
    endpoint;
    constructor(data) {
        super();
        this.channel_avatar = Thumbnail.fromResponse(data.channelAvatar);
        this.custom_text = new Text(data.customText);
        this.channel_name = new Text(data.channelName);
        this.subscriber_count = new Text(data.subscriberCountText);
        this.endpoint = new NavigationEndpoint(data.endpoint);
    }
}
//# sourceMappingURL=CollaboratorInfoCardContent.js.map