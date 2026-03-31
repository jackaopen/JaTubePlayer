import Thumbnail from './misc/Thumbnail.js';
import NavigationEndpoint from './NavigationEndpoint.js';
import { YTNode } from '../helpers.js';
export default class BackstageImage extends YTNode {
    static type = 'BackstageImage';
    image;
    endpoint;
    constructor(data) {
        super();
        this.image = Thumbnail.fromResponse(data.image);
        this.endpoint = new NavigationEndpoint(data.command);
    }
}
//# sourceMappingURL=BackstageImage.js.map