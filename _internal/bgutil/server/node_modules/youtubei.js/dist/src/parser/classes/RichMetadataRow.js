import { Parser } from '../index.js';
import { YTNode } from '../helpers.js';
export default class RichMetadataRow extends YTNode {
    static type = 'RichMetadataRow';
    contents;
    constructor(data) {
        super();
        this.contents = Parser.parseArray(data.contents);
    }
}
//# sourceMappingURL=RichMetadataRow.js.map