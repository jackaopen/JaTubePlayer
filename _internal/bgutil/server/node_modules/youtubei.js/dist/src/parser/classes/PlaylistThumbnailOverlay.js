import { YTNode } from '../helpers.js';
import Text from './misc/Text.js';
export default class PlaylistThumbnailOverlay extends YTNode {
    static type = 'PlaylistThumbnailOverlay';
    icon_type;
    text;
    constructor(data) {
        super();
        if (Reflect.has(data, 'icon'))
            this.icon_type = data.icon.iconType;
        this.text = new Text(data.text);
    }
}
//# sourceMappingURL=PlaylistThumbnailOverlay.js.map