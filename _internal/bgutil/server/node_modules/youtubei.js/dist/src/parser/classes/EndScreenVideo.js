import { YTNode } from '../helpers.js';
import { Parser } from '../index.js';
import Author from './misc/Author.js';
import Text from './misc/Text.js';
import Thumbnail from './misc/Thumbnail.js';
import NavigationEndpoint from './NavigationEndpoint.js';
export default class EndScreenVideo extends YTNode {
    static type = 'EndScreenVideo';
    id;
    title;
    thumbnails;
    thumbnail_overlays;
    author;
    endpoint;
    short_view_count;
    badges;
    duration;
    constructor(data) {
        super();
        this.id = data.videoId;
        this.title = new Text(data.title);
        this.thumbnails = Thumbnail.fromResponse(data.thumbnail);
        this.thumbnail_overlays = Parser.parseArray(data.thumbnailOverlays);
        this.author = new Author(data.shortBylineText, data.ownerBadges);
        this.endpoint = new NavigationEndpoint(data.navigationEndpoint);
        this.short_view_count = new Text(data.shortViewCountText);
        this.badges = Parser.parseArray(data.badges);
        this.duration = {
            text: new Text(data.lengthText).toString(),
            seconds: data.lengthInSeconds
        };
    }
}
//# sourceMappingURL=EndScreenVideo.js.map