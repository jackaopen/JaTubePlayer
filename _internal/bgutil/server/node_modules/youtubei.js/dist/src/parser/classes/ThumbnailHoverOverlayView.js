import { YTNode } from '../helpers.js';
import Text from './misc/Text.js';
export default class ThumbnailHoverOverlayView extends YTNode {
    static type = 'ThumbnailHoverOverlayView';
    icon_name;
    text;
    style;
    constructor(data) {
        super();
        this.icon_name = data.icon.sources[0].clientResource.imageName;
        this.text = Text.fromAttributed(data.text);
        this.style = data.style;
    }
}
//# sourceMappingURL=ThumbnailHoverOverlayView.js.map