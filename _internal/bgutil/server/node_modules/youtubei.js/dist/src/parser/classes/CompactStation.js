import { YTNode } from '../helpers.js';
import Text from './misc/Text.js';
import Thumbnail from './misc/Thumbnail.js';
import NavigationEndpoint from './NavigationEndpoint.js';
export default class CompactStation extends YTNode {
    static type = 'CompactStation';
    title;
    description;
    video_count;
    endpoint;
    thumbnail;
    constructor(data) {
        super();
        this.title = new Text(data.title);
        this.description = new Text(data.description);
        this.video_count = new Text(data.videoCountText);
        this.endpoint = new NavigationEndpoint(data.navigationEndpoint);
        this.thumbnail = Thumbnail.fromResponse(data.thumbnail);
    }
}
//# sourceMappingURL=CompactStation.js.map