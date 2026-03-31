import { YTNode } from '../../helpers.js';
import { Parser } from '../../index.js';
import ChannelSwitcherPage from '../ChannelSwitcherPage.js';
export default class UpdateChannelSwitcherPageAction extends YTNode {
    static type = 'UpdateChannelSwitcherPageAction';
    header;
    contents;
    constructor(data) {
        super();
        const page = Parser.parseItem(data.page, ChannelSwitcherPage);
        if (page) {
            this.header = page.header;
            this.contents = page.contents;
        }
    }
}
//# sourceMappingURL=UpdateChannelSwitcherPageAction.js.map