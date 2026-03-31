import { Parser } from '../index.js';
import { YTNode } from '../helpers.js';
export default class MetadataScreen extends YTNode {
    static type = 'MetadataScreen';
    section_list;
    constructor(data) {
        super();
        this.section_list = Parser.parseItem(data);
    }
}
//# sourceMappingURL=MetadataScreen.js.map