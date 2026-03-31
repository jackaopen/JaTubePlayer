import { YTNode } from '../helpers.js';
import ClipCreation from './ClipCreation.js';
import { Parser } from '../index.js';
export default class ClipSection extends YTNode {
    static type = 'ClipSection';
    contents;
    constructor(data) {
        super();
        this.contents = Parser.parse(data.contents, true, [ClipCreation]);
    }
}
//# sourceMappingURL=ClipSection.js.map