import { YTNode } from '../helpers.js';
import Text from './misc/Text.js';
export default class ThumbnailOverlayPlaybackStatus extends YTNode {
    static type = 'ThumbnailOverlayPlaybackStatus';
    texts;
    constructor(data) {
        super();
        this.texts = data.texts.map((text) => new Text(text));
    }
}
//# sourceMappingURL=ThumbnailOverlayPlaybackStatus.js.map