import { Parser } from '../../index.js';
import { YTNode } from '../../helpers.js';
export default class ReplaceChatItemAction extends YTNode {
    static type = 'ReplaceChatItemAction';
    target_item_id;
    replacement_item;
    constructor(data) {
        super();
        this.target_item_id = data.targetItemId;
        this.replacement_item = Parser.parseItem(data.replacementItem);
    }
}
//# sourceMappingURL=ReplaceChatItemAction.js.map