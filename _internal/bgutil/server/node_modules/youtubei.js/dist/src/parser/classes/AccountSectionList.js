import { Parser } from '../index.js';
import AccountChannel from './AccountChannel.js';
import AccountItemSection from './AccountItemSection.js';
import { YTNode } from '../helpers.js';
export default class AccountSectionList extends YTNode {
    static type = 'AccountSectionList';
    contents;
    footers;
    constructor(data) {
        super();
        this.contents = Parser.parseArray(data.contents, AccountItemSection);
        this.footers = Parser.parseArray(data.footers, AccountChannel);
    }
}
//# sourceMappingURL=AccountSectionList.js.map