import { YTNode } from '../helpers.js';
import NavigationEndpoint from './NavigationEndpoint.js';
import Thumbnail from './misc/Thumbnail.js';
export default class HeroPlaylistThumbnail extends YTNode {
    static type = 'HeroPlaylistThumbnail';
    thumbnails;
    on_tap_endpoint;
    constructor(data) {
        super();
        this.thumbnails = Thumbnail.fromResponse(data.thumbnail);
        this.on_tap_endpoint = new NavigationEndpoint(data.onTap);
    }
}
//# sourceMappingURL=HeroPlaylistThumbnail.js.map