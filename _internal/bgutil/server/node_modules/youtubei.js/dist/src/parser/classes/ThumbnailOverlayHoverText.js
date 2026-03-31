import Text from './misc/Text.js';
import { YTNode } from '../helpers.js';
export default class ThumbnailOverlayHoverText extends YTNode {
    static type = 'ThumbnailOverlayHoverText';
    text;
    icon_type;
    constructor(data) {
        super();
        this.text = new Text(data.text);
        this.icon_type = data.icon.iconType;
    }
}
//# sourceMappingURL=ThumbnailOverlayHoverText.js.map