import { YTNode } from '../helpers.js';
import { Parser } from '../index.js';
export default class ChannelSwitcherPage extends YTNode {
    static type = 'ChannelSwitcherPage';
    header;
    contents;
    constructor(data) {
        super();
        this.header = Parser.parseItem(data.header);
        this.contents = Parser.parse(data.contents, true);
    }
}
//# sourceMappingURL=ChannelSwitcherPage.js.map