import { Parser } from '../index.js';
import { YTNode } from '../helpers.js';
import Text from './misc/Text.js';
export default class MusicHeader extends YTNode {
    static type = 'MusicHeader';
    header;
    title;
    constructor(data) {
        super();
        if (Reflect.has(data, 'header')) {
            this.header = Parser.parseItem(data.header);
        }
        if (Reflect.has(data, 'title')) {
            this.title = new Text(data.title);
        }
    }
}
//# sourceMappingURL=MusicHeader.js.map