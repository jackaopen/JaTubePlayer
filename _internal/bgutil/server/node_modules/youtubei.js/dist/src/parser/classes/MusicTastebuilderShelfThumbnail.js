import { YTNode } from '../helpers.js';
import { Thumbnail } from '../misc.js';
export default class MusicTastebuilderShelfThumbnail extends YTNode {
    static type = 'MusicTastebuilderShelfThumbnail';
    thumbnail;
    constructor(data) {
        super();
        this.thumbnail = Thumbnail.fromResponse(data.thumbnail);
    }
}
//# sourceMappingURL=MusicTastebuilderShelfThumbnail.js.map