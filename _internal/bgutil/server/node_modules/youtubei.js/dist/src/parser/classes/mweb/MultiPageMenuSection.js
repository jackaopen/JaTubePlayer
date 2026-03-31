import { YTNode } from '../../helpers.js';
import { Parser } from '../../index.js';
export default class MultiPageMenuSection extends YTNode {
    static type = 'MultiPageMenuSection';
    items;
    constructor(data) {
        super();
        this.items = Parser.parseArray(data.items);
    }
}
//# sourceMappingURL=MultiPageMenuSection.js.map