import { YTNode } from '../helpers.js';
import { Parser } from '../index.js';
import Author from './misc/Author.js';
import Text from './misc/Text.js';
import NavigationEndpoint from './NavigationEndpoint.js';
export default class GridChannel extends YTNode {
    static type = 'GridChannel';
    id;
    author;
    subscribers;
    video_count;
    endpoint;
    subscribe_button;
    constructor(data) {
        super();
        this.id = data.channelId;
        this.author = new Author({
            ...data.title,
            navigationEndpoint: data.navigationEndpoint
        }, data.ownerBadges, data.thumbnail);
        this.subscribers = new Text(data.subscriberCountText);
        this.video_count = new Text(data.videoCountText);
        this.endpoint = new NavigationEndpoint(data.navigationEndpoint);
        this.subscribe_button = Parser.parseItem(data.subscribeButton);
    }
}
//# sourceMappingURL=GridChannel.js.map