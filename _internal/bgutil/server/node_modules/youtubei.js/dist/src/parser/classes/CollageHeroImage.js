import NavigationEndpoint from './NavigationEndpoint.js';
import Thumbnail from './misc/Thumbnail.js';
import { YTNode } from '../helpers.js';
export default class CollageHeroImage extends YTNode {
    static type = 'CollageHeroImage';
    left;
    top_right;
    bottom_right;
    endpoint;
    constructor(data) {
        super();
        this.left = Thumbnail.fromResponse(data.leftThumbnail);
        this.top_right = Thumbnail.fromResponse(data.topRightThumbnail);
        this.bottom_right = Thumbnail.fromResponse(data.bottomRightThumbnail);
        this.endpoint = new NavigationEndpoint(data.navigationEndpoint);
    }
}
//# sourceMappingURL=CollageHeroImage.js.map