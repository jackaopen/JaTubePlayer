import { YTNode } from '../helpers.js';
import Text from './misc/Text.js';
export default class HashtagHeader extends YTNode {
    static type = 'HashtagHeader';
    hashtag;
    hashtag_info;
    constructor(data) {
        super();
        this.hashtag = new Text(data.hashtag);
        this.hashtag_info = new Text(data.hashtagInfoText);
    }
}
//# sourceMappingURL=HashtagHeader.js.map