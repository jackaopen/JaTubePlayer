import Text from './misc/Text.js';
import Thumbnail from './misc/Thumbnail.js';
import NavigationEndpoint from './NavigationEndpoint.js';
import { YTNode } from '../helpers.js';
export default class EndScreenPlaylist extends YTNode {
    static type = 'EndScreenPlaylist';
    id;
    title;
    author;
    endpoint;
    thumbnails;
    video_count;
    constructor(data) {
        super();
        this.id = data.playlistId;
        this.title = new Text(data.title);
        this.author = new Text(data.longBylineText);
        this.endpoint = new NavigationEndpoint(data.navigationEndpoint);
        this.thumbnails = Thumbnail.fromResponse(data.thumbnail);
        this.video_count = new Text(data.videoCountText);
    }
}
//# sourceMappingURL=EndScreenPlaylist.js.map