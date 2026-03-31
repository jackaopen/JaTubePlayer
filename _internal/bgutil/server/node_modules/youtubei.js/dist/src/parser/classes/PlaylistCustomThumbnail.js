import { YTNode } from '../helpers.js';
import Thumbnail from './misc/Thumbnail.js';
export default class PlaylistCustomThumbnail extends YTNode {
    static type = 'PlaylistCustomThumbnail';
    thumbnail;
    constructor(data) {
        super();
        this.thumbnail = Thumbnail.fromResponse(data.thumbnail);
    }
}
//# sourceMappingURL=PlaylistCustomThumbnail.js.map