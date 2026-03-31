import { Parser } from '../../index.js';
import { YTNode } from '../../helpers.js';
export default class AppendContinuationItemsAction extends YTNode {
    static type = 'AppendContinuationItemsAction';
    contents;
    target;
    constructor(data) {
        super();
        this.contents = Parser.parseArray(data.continuationItems);
        this.target = data.target;
    }
}
//# sourceMappingURL=AppendContinuationItemsAction.js.map