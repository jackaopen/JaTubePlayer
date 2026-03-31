import Thumbnail from './misc/Thumbnail.js';
import { YTNode } from '../helpers.js';
export default class SingleHeroImage extends YTNode {
    static type = 'SingleHeroImage';
    thumbnails;
    style;
    constructor(data) {
        super();
        this.thumbnails = Thumbnail.fromResponse(data.thumbnail);
        this.style = data.style;
    }
}
//# sourceMappingURL=SingleHeroImage.js.map