import Thumbnail from './misc/Thumbnail.js';
import { YTNode } from '../helpers.js';
export default class MusicThumbnail extends YTNode {
    static type = 'MusicThumbnail';
    contents;
    constructor(data) {
        super();
        this.contents = Thumbnail.fromResponse(data.thumbnail);
    }
}
//# sourceMappingURL=MusicThumbnail.js.map