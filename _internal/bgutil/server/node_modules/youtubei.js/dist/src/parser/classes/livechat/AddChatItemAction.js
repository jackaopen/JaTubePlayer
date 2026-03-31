import { Parser } from '../../index.js';
import { YTNode } from '../../helpers.js';
export default class AddChatItemAction extends YTNode {
    static type = 'AddChatItemAction';
    item;
    client_id;
    constructor(data) {
        super();
        this.item = Parser.parseItem(data.item);
        if (Reflect.has(data, 'clientId')) {
            this.client_id = data.clientId;
        }
    }
}
//# sourceMappingURL=AddChatItemAction.js.map