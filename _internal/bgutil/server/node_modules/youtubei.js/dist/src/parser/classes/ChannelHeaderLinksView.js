import { YTNode } from '../helpers.js';
import Text from './misc/Text.js';
export default class ChannelHeaderLinksView extends YTNode {
    static type = 'ChannelHeaderLinksView';
    first_link;
    more;
    constructor(data) {
        super();
        if (Reflect.has(data, 'firstLink')) {
            this.first_link = Text.fromAttributed(data.firstLink);
        }
        if (Reflect.has(data, 'more')) {
            this.more = Text.fromAttributed(data.more);
        }
    }
}
//# sourceMappingURL=ChannelHeaderLinksView.js.map