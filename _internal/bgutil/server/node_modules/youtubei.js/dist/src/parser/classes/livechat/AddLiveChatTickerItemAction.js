import { Parser } from '../../index.js';
import { YTNode } from '../../helpers.js';
export default class AddLiveChatTickerItemAction extends YTNode {
    static type = 'AddLiveChatTickerItemAction';
    item;
    duration_sec; // TODO: check this assumption.
    constructor(data) {
        super();
        this.item = Parser.parseItem(data.item);
        this.duration_sec = data.durationSec;
    }
}
//# sourceMappingURL=AddLiveChatTickerItemAction.js.map