import { YTNode } from '../../helpers.js';
export default class RemoveChatItemByAuthorAction extends YTNode {
    static type = 'RemoveChatItemByAuthorAction';
    external_channel_id;
    constructor(data) {
        super();
        this.external_channel_id = data.externalChannelId;
    }
}
//# sourceMappingURL=RemoveChatItemByAuthorAction.js.map