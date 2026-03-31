import { YTNode } from '../../helpers.js';
import { Parser } from '../../index.js';
export default class ReplaceLiveChatAction extends YTNode {
    static type = 'ReplaceLiveChatAction';
    to_replace;
    replacement;
    constructor(data) {
        super();
        this.to_replace = data.toReplace;
        this.replacement = Parser.parseItem(data.replacement);
    }
}
//# sourceMappingURL=ReplaceLiveChatAction.js.map