import { YTNode } from '../helpers.js';
import { Parser } from '../index.js';
import { Text, Thumbnail } from '../misc.js';
import Factoid from './Factoid.js';
import NavigationEndpoint from './NavigationEndpoint.js';
import UploadTimeFactoid from './UploadTimeFactoid.js';
import ViewCountFactoid from './ViewCountFactoid.js';
import HypePointsFactoid from './HypePointsFactoid.js';
export default class VideoDescriptionHeader extends YTNode {
    static type = 'VideoDescriptionHeader';
    channel;
    channel_navigation_endpoint;
    channel_thumbnail;
    factoids;
    publish_date;
    title;
    views;
    constructor(data) {
        super();
        this.title = new Text(data.title);
        this.channel = new Text(data.channel);
        this.channel_navigation_endpoint = new NavigationEndpoint(data.channelNavigationEndpoint);
        this.channel_thumbnail = Thumbnail.fromResponse(data.channelThumbnail);
        this.publish_date = new Text(data.publishDate);
        this.views = new Text(data.views);
        this.factoids = Parser.parseArray(data.factoid, [Factoid, HypePointsFactoid, ViewCountFactoid, UploadTimeFactoid]);
    }
}
//# sourceMappingURL=VideoDescriptionHeader.js.map