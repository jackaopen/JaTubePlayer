import { YTNode } from '../helpers.js';
import Thumbnail from './misc/Thumbnail.js';
export default class AnimatedThumbnailOverlayView extends YTNode {
    static type = 'AnimatedThumbnailOverlayView';
    thumbnail;
    constructor(data) {
        super();
        this.thumbnail = Thumbnail.fromResponse(data.thumbnail);
    }
}
//# sourceMappingURL=AnimatedThumbnailOverlayView.js.map