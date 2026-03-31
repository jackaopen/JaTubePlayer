import { YTNode } from '../helpers.js';
import NavigationEndpoint from './NavigationEndpoint.js';
import Text from './misc/Text.js';
import Thumbnail from './misc/Thumbnail.js';
export default class VideoInfoCardContent extends YTNode {
    static type = 'VideoInfoCardContent';
    title;
    channel_name;
    view_count;
    video_thumbnails;
    duration;
    endpoint;
    constructor(data) {
        super();
        this.title = new Text(data.videoTitle);
        this.channel_name = new Text(data.channelName);
        this.view_count = new Text(data.viewCountText);
        this.video_thumbnails = Thumbnail.fromResponse(data.videoThumbnail);
        this.duration = new Text(data.lengthString);
        this.endpoint = new NavigationEndpoint(data.action);
    }
}
//# sourceMappingURL=VideoInfoCardContent.js.map