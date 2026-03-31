import Text from './misc/Text.js';
import { YTNode } from '../helpers.js';
export default class ThumbnailOverlaySidePanel extends YTNode {
    static type = 'ThumbnailOverlaySidePanel';
    text;
    icon_type;
    constructor(data) {
        super();
        this.text = new Text(data.text);
        this.icon_type = data.icon.iconType;
    }
}
//# sourceMappingURL=ThumbnailOverlaySidePanel.js.map