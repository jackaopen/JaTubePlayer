import Text from '../misc/Text.js';
import { YTNode } from '../../helpers.js';
export default class MarkChatItemAsDeletedAction extends YTNode {
    static type = 'MarkChatItemAsDeletedAction';
    deleted_state_message;
    target_item_id;
    constructor(data) {
        super();
        this.deleted_state_message = new Text(data.deletedStateMessage);
        this.target_item_id = data.targetItemId;
    }
}
//# sourceMappingURL=MarkChatItemAsDeletedAction.js.map