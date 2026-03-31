import { YTNode } from '../helpers.js';
import Text from './misc/Text.js';
export default class ThumbnailOverlayNowPlaying extends YTNode {
    static type = 'ThumbnailOverlayNowPlaying';
    text;
    constructor(data) {
        super();
        this.text = new Text(data.text).toString();
    }
}
//# sourceMappingURL=ThumbnailOverlayNowPlaying.js.map