import Text from './misc/Text.js';
import Thumbnail from './misc/Thumbnail.js';
import { YTNode } from '../helpers.js';
export default class ProfileColumnUserInfo extends YTNode {
    static type = 'ProfileColumnUserInfo';
    title;
    thumbnails;
    constructor(data) {
        super();
        this.title = new Text(data.title);
        this.thumbnails = Thumbnail.fromResponse(data.thumbnail);
    }
}
//# sourceMappingURL=ProfileColumnUserInfo.js.map