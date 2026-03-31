import Text from './misc/Text.js';
import { YTNode } from '../helpers.js';
export default class MetadataRow extends YTNode {
    static type = 'MetadataRow';
    title;
    contents;
    constructor(data) {
        super();
        this.title = new Text(data.title);
        this.contents = data.contents.map((content) => new Text(content));
    }
}
//# sourceMappingURL=MetadataRow.js.map