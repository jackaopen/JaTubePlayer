import { YTNode } from '../../helpers.js';
import { Parser } from '../../index.js';
export default class PivotBar extends YTNode {
    static type = 'PivotBar';
    items;
    constructor(data) {
        super();
        this.items = Parser.parseArray(data.items);
    }
}
//# sourceMappingURL=PivotBar.js.map