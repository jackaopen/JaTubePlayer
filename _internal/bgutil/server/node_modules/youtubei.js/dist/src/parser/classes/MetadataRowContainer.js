import { Parser } from '../index.js';
import { YTNode } from '../helpers.js';
export default class MetadataRowContainer extends YTNode {
    static type = 'MetadataRowContainer';
    rows;
    collapsed_item_count;
    constructor(data) {
        super();
        this.rows = Parser.parseArray(data.rows);
        this.collapsed_item_count = data.collapsedItemCount;
    }
}
//# sourceMappingURL=MetadataRowContainer.js.map