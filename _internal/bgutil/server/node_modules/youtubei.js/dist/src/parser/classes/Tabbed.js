import { YTNode } from '../helpers.js';
import { Parser } from '../index.js';
export default class Tabbed extends YTNode {
    static type = 'Tabbed';
    contents;
    constructor(data) {
        super();
        this.contents = Parser.parse(data);
    }
}
//# sourceMappingURL=Tabbed.js.map