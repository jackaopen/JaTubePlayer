import Text from './misc/Text.js';
import Thumbnail from './misc/Thumbnail.js';
import { YTNode } from '../helpers.js';
export default class BrowserMediaSession extends YTNode {
    static type = 'BrowserMediaSession';
    album;
    thumbnails;
    constructor(data) {
        super();
        this.album = new Text(data.album);
        this.thumbnails = Thumbnail.fromResponse(data.thumbnailDetails);
    }
}
//# sourceMappingURL=BrowserMediaSession.js.map