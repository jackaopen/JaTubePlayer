import { YTNode } from '../helpers.js';
import Text from './misc/Text.js';
export default class ThumbnailOverlayLoadingPreview extends YTNode {
    static type = 'ThumbnailOverlayLoadingPreview';
    text;
    constructor(data) {
        super();
        this.text = new Text(data.text);
    }
}
//# sourceMappingURL=ThumbnailOverlayLoadingPreview.js.map