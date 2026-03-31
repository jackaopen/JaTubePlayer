import { Parser } from '../../index.js';
import { YTNode } from '../../helpers.js';
export default class LiveChatActionPanel extends YTNode {
    static type = 'LiveChatActionPanel';
    id;
    contents;
    target_id;
    constructor(data) {
        super();
        this.id = data.id;
        this.contents = Parser.parse(data.contents);
        this.target_id = data.targetId;
    }
}
//# sourceMappingURL=LiveChatActionPanel.js.map