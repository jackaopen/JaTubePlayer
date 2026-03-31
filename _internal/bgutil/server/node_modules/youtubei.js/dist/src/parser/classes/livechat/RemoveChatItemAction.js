import { YTNode } from '../../helpers.js';
export default class RemoveChatItemAction extends YTNode {
    static type = 'RemoveChatItemAction';
    target_item_id;
    constructor(data) {
        super();
        this.target_item_id = data.targetItemId;
    }
}
//# sourceMappingURL=RemoveChatItemAction.js.map