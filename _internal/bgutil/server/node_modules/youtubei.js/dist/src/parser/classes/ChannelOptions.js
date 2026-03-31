import Text from './misc/Text.js';
import Thumbnail from './misc/Thumbnail.js';
import NavigationEndpoint from './NavigationEndpoint.js';
import { YTNode } from '../helpers.js';
export default class ChannelOptions extends YTNode {
    static type = 'ChannelOptions';
    avatar;
    endpoint;
    name;
    links;
    constructor(data) {
        super();
        this.avatar = Thumbnail.fromResponse(data.avatar);
        this.endpoint = new NavigationEndpoint(data.avatarEndpoint);
        this.name = data.name;
        this.links = data.links.map((link) => new Text(link));
    }
}
//# sourceMappingURL=ChannelOptions.js.map