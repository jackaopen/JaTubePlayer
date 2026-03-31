import Text from '../misc/Text.js';
import { YTNode } from '../../helpers.js';
export default class MarkChatItemsByAuthorAsDeletedAction extends YTNode {
    static type = 'MarkChatItemsByAuthorAsDeletedAction';
    deleted_state_message;
    external_channel_id;
    constructor(data) {
        super();
        this.deleted_state_message = new Text(data.deletedStateMessage);
        this.external_channel_id = data.externalChannelId;
    }
}
//# sourceMappingURL=MarkChatItemsByAuthorAsDeletedAction.js.map