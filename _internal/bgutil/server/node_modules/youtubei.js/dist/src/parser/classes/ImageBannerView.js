import { YTNode } from '../helpers.js';
import Thumbnail from './misc/Thumbnail.js';
export default class ImageBannerView extends YTNode {
    static type = 'ImageBannerView';
    image;
    style;
    constructor(data) {
        super();
        this.image = Thumbnail.fromResponse(data.image);
        this.style = data.style;
    }
}
//# sourceMappingURL=ImageBannerView.js.map