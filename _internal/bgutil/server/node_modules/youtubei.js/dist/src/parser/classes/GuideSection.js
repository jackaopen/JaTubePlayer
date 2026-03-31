import Text from './misc/Text.js';
import * as Parser from '../parser.js';
import { YTNode } from '../helpers.js';
export default class GuideSection extends YTNode {
    static type = 'GuideSection';
    title;
    items;
    constructor(data) {
        super();
        if (Reflect.has(data, 'formattedTitle')) {
            this.title = new Text(data.formattedTitle);
        }
        this.items = Parser.parseArray(data.items);
    }
}
//# sourceMappingURL=GuideSection.js.map