import Text from './misc/Text.js';
import { YTNode } from '../helpers.js';
export default class ChannelVideoPlayer extends YTNode {
    static type = 'ChannelVideoPlayer';
    id;
    title;
    description;
    view_count;
    published_time;
    constructor(data) {
        super();
        this.id = data.videoId;
        this.title = new Text(data.title);
        this.description = new Text(data.description);
        this.view_count = new Text(data.viewCountText);
        this.published_time = new Text(data.publishedTimeText);
    }
}
//# sourceMappingURL=ChannelVideoPlayer.js.map