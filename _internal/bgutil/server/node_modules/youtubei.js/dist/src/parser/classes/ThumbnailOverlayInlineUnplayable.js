import { YTNode } from '../helpers.js';
import Text from './misc/Text.js';
export default class ThumbnailOverlayInlineUnplayable extends YTNode {
    static type = 'ThumbnailOverlayInlineUnplayable';
    text;
    icon_type;
    constructor(data) {
        super();
        this.text = new Text(data.text).toString();
        this.icon_type = data.icon.iconType;
    }
}
//# sourceMappingURL=ThumbnailOverlayInlineUnplayable.js.map