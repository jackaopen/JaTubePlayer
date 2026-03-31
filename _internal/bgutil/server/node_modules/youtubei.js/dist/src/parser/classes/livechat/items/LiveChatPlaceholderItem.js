import { YTNode } from '../../../helpers.js';
export default class LiveChatPlaceholderItem extends YTNode {
    static type = 'LiveChatPlaceholderItem';
    id;
    timestamp;
    constructor(data) {
        super();
        this.id = data.id;
        this.timestamp = Math.floor(parseInt(data.timestampUsec) / 1000);
    }
}
//# sourceMappingURL=LiveChatPlaceholderItem.js.map