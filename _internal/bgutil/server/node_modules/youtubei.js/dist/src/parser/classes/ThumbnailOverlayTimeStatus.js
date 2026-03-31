import Text from './misc/Text.js';
import { YTNode } from '../helpers.js';
export default class ThumbnailOverlayTimeStatus extends YTNode {
    static type = 'ThumbnailOverlayTimeStatus';
    text;
    style;
    constructor(data) {
        super();
        this.text = new Text(data.text).toString();
        this.style = data.style;
    }
}
//# sourceMappingURL=ThumbnailOverlayTimeStatus.js.map