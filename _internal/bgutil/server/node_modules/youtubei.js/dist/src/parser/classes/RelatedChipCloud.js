import { Parser } from '../index.js';
import { YTNode } from '../helpers.js';
export default class RelatedChipCloud extends YTNode {
    static type = 'RelatedChipCloud';
    content;
    constructor(data) {
        super();
        this.content = Parser.parseItem(data.content);
    }
}
//# sourceMappingURL=RelatedChipCloud.js.map