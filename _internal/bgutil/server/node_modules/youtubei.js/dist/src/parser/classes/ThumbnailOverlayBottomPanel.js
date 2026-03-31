import { YTNode } from '../helpers.js';
import Text from './misc/Text.js';
export default class ThumbnailOverlayBottomPanel extends YTNode {
    static type = 'ThumbnailOverlayBottomPanel';
    text;
    icon_type;
    constructor(data) {
        super();
        if (Reflect.has(data, 'text')) {
            this.text = new Text(data.text);
        }
        if (Reflect.has(data, 'icon') && Reflect.has(data.icon, 'iconType')) {
            this.icon_type = data.icon.iconType;
        }
    }
}
//# sourceMappingURL=ThumbnailOverlayBottomPanel.js.map