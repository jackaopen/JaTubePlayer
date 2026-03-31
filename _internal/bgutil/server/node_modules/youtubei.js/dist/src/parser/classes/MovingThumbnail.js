import { YTNode } from '../helpers.js';
import Thumbnail from './misc/Thumbnail.js';
export default class MovingThumbnail extends YTNode {
    static type = 'MovingThumbnail';
    constructor(data) {
        super();
        return data.movingThumbnailDetails?.thumbnails.map((thumbnail) => new Thumbnail(thumbnail)).sort((a, b) => b.width - a.width);
    }
}
//# sourceMappingURL=MovingThumbnail.js.map