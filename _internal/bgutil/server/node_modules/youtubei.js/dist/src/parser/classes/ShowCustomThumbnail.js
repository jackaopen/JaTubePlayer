import { YTNode } from '../helpers.js';
import Thumbnail from './misc/Thumbnail.js';
export default class ShowCustomThumbnail extends YTNode {
    static type = 'ShowCustomThumbnail';
    thumbnail;
    constructor(data) {
        super();
        this.thumbnail = Thumbnail.fromResponse(data.thumbnail);
    }
}
//# sourceMappingURL=ShowCustomThumbnail.js.map