import { YTNode } from '../helpers.js';
import Thumbnail from './misc/Thumbnail.js';
import Author from './misc/Author.js';
import Text from './misc/Text.js';
export default class ReelPlayerHeader extends YTNode {
    static type = 'ReelPlayerHeader';
    reel_title_text;
    timestamp_text;
    channel_title_text;
    channel_thumbnail;
    author;
    constructor(data) {
        super();
        this.reel_title_text = new Text(data.reelTitleText);
        this.timestamp_text = new Text(data.timestampText);
        this.channel_title_text = new Text(data.channelTitleText);
        this.channel_thumbnail = Thumbnail.fromResponse(data.channelThumbnail);
        this.author = new Author(data.channelNavigationEndpoint, undefined);
    }
}
//# sourceMappingURL=ReelPlayerHeader.js.map