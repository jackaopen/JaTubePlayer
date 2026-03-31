import Text from './misc/Text.js';
import { YTNode } from '../helpers.js';
export default class FeedTabbedHeader extends YTNode {
    static type = 'FeedTabbedHeader';
    title;
    constructor(data) {
        super();
        this.title = new Text(data.title);
    }
}
//# sourceMappingURL=FeedTabbedHeader.js.map