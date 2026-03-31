import Text from './misc/Text.js';
import { YTNode } from '../helpers.js';
export default class MetadataRowHeader extends YTNode {
    static type = 'MetadataRowHeader';
    content;
    has_divider_line;
    constructor(data) {
        super();
        this.content = new Text(data.content);
        this.has_divider_line = data.hasDividerLine;
    }
}
//# sourceMappingURL=MetadataRowHeader.js.map