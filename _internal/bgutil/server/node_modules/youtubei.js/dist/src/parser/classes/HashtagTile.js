import { YTNode } from '../helpers.js';
import { Thumbnail } from '../misc.js';
import NavigationEndpoint from './NavigationEndpoint.js';
import Text from './misc/Text.js';
export default class HashtagTile extends YTNode {
    static type = 'HashtagTile';
    hashtag;
    hashtag_info_text;
    hashtag_thumbnail;
    endpoint;
    hashtag_background_color;
    hashtag_video_count;
    hashtag_channel_count;
    constructor(data) {
        super();
        this.hashtag = new Text(data.hashtag);
        this.hashtag_info_text = new Text(data.hashtagInfoText);
        this.hashtag_thumbnail = Thumbnail.fromResponse(data.hashtagThumbnail);
        this.endpoint = new NavigationEndpoint(data.onTapCommand);
        this.hashtag_background_color = data.hashtagBackgroundColor;
        this.hashtag_video_count = new Text(data.hashtagVideoCount);
        this.hashtag_channel_count = new Text(data.hashtagChannelCount);
    }
}
//# sourceMappingURL=HashtagTile.js.map