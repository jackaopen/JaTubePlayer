import { Parser } from '../index.js';
import { YTNode } from '../helpers.js';
export default class RichItem extends YTNode {
    static type = 'RichItem';
    content;
    constructor(data) {
        super();
        this.content = Parser.parseItem(data.content);
    }
}
//# sourceMappingURL=RichItem.js.map