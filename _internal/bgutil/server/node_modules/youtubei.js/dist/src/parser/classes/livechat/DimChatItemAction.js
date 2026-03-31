import { YTNode } from '../../helpers.js';
export default class DimChatItemAction extends YTNode {
    static type = 'DimChatItemAction';
    client_assigned_id;
    constructor(data) {
        super();
        this.client_assigned_id = data.clientAssignedId;
    }
}
//# sourceMappingURL=DimChatItemAction.js.map