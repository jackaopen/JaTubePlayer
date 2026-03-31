import Text from './misc/Text.js';
import { YTNode } from '../helpers.js';
export default class ItemSectionHeader extends YTNode {
    static type = 'ItemSectionHeader';
    title;
    constructor(data) {
        super();
        this.title = new Text(data.title);
    }
}
//# sourceMappingURL=ItemSectionHeader.js.map