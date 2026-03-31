import { YTNode } from '../helpers.js';
import { Parser } from '../index.js';
import Text from './misc/Text.js';
export default class ChannelFeaturedContent extends YTNode {
    static type = 'ChannelFeaturedContent';
    title;
    items;
    constructor(data) {
        super();
        this.title = new Text(data.title);
        this.items = Parser.parseArray(data.items);
    }
}
//# sourceMappingURL=ChannelFeaturedContent.js.map