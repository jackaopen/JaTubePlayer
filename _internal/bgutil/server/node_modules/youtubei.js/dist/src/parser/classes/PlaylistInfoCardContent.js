import Text from './misc/Text.js';
import Thumbnail from './misc/Thumbnail.js';
import NavigationEndpoint from './NavigationEndpoint.js';
import { YTNode } from '../helpers.js';
export default class PlaylistInfoCardContent extends YTNode {
    static type = 'PlaylistInfoCardContent';
    title;
    thumbnails;
    video_count;
    channel_name;
    endpoint;
    constructor(data) {
        super();
        this.title = new Text(data.playlistTitle);
        this.thumbnails = Thumbnail.fromResponse(data.thumbnail);
        this.video_count = new Text(data.playlistVideoCount);
        this.channel_name = new Text(data.channelName);
        this.endpoint = new NavigationEndpoint(data.action);
    }
}
//# sourceMappingURL=PlaylistInfoCardContent.js.map