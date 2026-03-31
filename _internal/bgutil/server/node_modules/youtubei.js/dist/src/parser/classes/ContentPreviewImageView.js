import { YTNode } from '../helpers.js';
import Thumbnail from './misc/Thumbnail.js';
export default class ContentPreviewImageView extends YTNode {
    static type = 'ContentPreviewImageView';
    image;
    style;
    constructor(data) {
        super();
        this.image = Thumbnail.fromResponse(data.image);
        this.style = data.style;
    }
}
//# sourceMappingURL=ContentPreviewImageView.js.map