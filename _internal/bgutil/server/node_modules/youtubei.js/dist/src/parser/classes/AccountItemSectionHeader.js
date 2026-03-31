import Text from './misc/Text.js';
import { YTNode } from '../helpers.js';
export default class AccountItemSectionHeader extends YTNode {
    static type = 'AccountItemSectionHeader';
    title;
    constructor(data) {
        super();
        this.title = new Text(data.title);
    }
}
//# sourceMappingURL=AccountItemSectionHeader.js.map