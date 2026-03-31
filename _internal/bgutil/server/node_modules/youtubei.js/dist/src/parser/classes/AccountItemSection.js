import { Parser } from '../index.js';
import AccountItem from './AccountItem.js';
import AccountItemSectionHeader from './AccountItemSectionHeader.js';
import { YTNode } from '../helpers.js';
import CompactLink from './CompactLink.js';
export default class AccountItemSection extends YTNode {
    static type = 'AccountItemSection';
    contents;
    header;
    constructor(data) {
        super();
        this.contents = Parser.parseArray(data.contents, [AccountItem, CompactLink]);
        this.header = Parser.parseItem(data.header, AccountItemSectionHeader);
    }
}
//# sourceMappingURL=AccountItemSection.js.map