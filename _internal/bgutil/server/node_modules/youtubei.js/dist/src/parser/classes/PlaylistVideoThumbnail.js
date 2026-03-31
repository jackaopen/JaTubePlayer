import Thumbnail from './misc/Thumbnail.js';
import { YTNode } from '../helpers.js';
export default class PlaylistVideoThumbnail extends YTNode {
    static type = 'PlaylistVideoThumbnail';
    thumbnail;
    constructor(data) {
        super();
        this.thumbnail = Thumbnail.fromResponse(data.thumbnail);
    }
}
//# sourceMappingURL=PlaylistVideoThumbnail.js.map