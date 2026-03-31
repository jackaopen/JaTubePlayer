import { YTNode } from '../helpers.js';
import Thumbnail from './misc/Thumbnail.js';
export default class ThumbnailLandscapePortrait extends YTNode {
    static type = 'ThumbnailLandscapePortrait';
    landscape;
    portrait;
    constructor(data) {
        super();
        this.landscape = Thumbnail.fromResponse(data.landscape);
        this.portrait = Thumbnail.fromResponse(data.portrait);
    }
}
//# sourceMappingURL=ThumbnailLandscapePortrait.js.map